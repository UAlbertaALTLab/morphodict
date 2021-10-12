import hashlib
import json
import logging
import time
from argparse import (
    ArgumentParser,
    BooleanOptionalAction,
    ArgumentDefaultsHelpFormatter,
)
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.db.models import Max
from tqdm import tqdm

from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.phrase_translate.translate import (
    translate_single_definition,
    TranslationStats,
)
from CreeDictionary.utils.english_keyword_extraction import stem_keywords
from morphodict.analysis import RichAnalysis, strict_generator
from morphodict.lexicon import DEFAULT_IMPORTJSON_FILE
from morphodict.lexicon.management.commands.buildtestimportjson import entry_sort_key
from morphodict.lexicon.models import (
    Wordform,
    Definition,
    DictionarySource,
    TargetLanguageKeyword,
    SourceLanguageKeyword,
    ImportStamp,
)
from morphodict.lexicon.util import to_source_language_keyword

logger = logging.getLogger(__name__)


class DictionarySourceCache:
    """
    Cache of DictionarySource objects.

    Call

        dictionary_source_cache.get_or_create("CW")

    to get the DictionarySource object with abbrv "CW", or create one if it does
    not yet exist.

    If you try to use more than one instance of this class at a time, you could
    get foreign key collisions on insert. So only create one.
    """

    def __init__(self):
        self.sources = {s.abbrv: s for s in DictionarySource.objects.all()}

    def get_or_create(self, abbrv):
        if (source := self.sources.get(abbrv, None)) is not None:
            return source
        source = DictionarySource.objects.create(abbrv=abbrv)
        self.sources[abbrv] = source
        return source


class InsertBuffer:
    """A container for objects to be bulk-inserted.

    Will automatically assign IDs to provided objects, and call
    `manager.bulk_create` every `count` objects. The caller is responsible for
    calling `save()` one final time when done.
    """

    def __init__(
        self,
        manager,
        count=2000,
        assign_id=False,
        trigger_deps=False,
        deps=[],
    ):
        """
        If assign_id is True, this class will assign IDs to objects added to it,
        so that they can immediately be used in foreign key references. While
        SQLite `INSERT … RETURNING` is supported in SQLite 3.35.0+, we don’t use
        that at all here. It’s not magic because you still have to be careful
        that foreign key references are already inserted.

        `deps` can be a list of other InsertBuffers to call save() on before
        save()ing this buffer to avoid foreign key constraint problems when not
        running inside a transaction. When inside a transaction, it’s safe to
        temporarily have dangling foreign keys that point at objects that will
        be added later, as long as everything is fixed up by the time the
        transaction commits. But when operations are not grouped together into a
        transaction, foreign keys have to be valid every step of the way. For
        example, if Definition objects point at Wordform objects, then a
        Wordform must really exist before the Definition can be inserted. To
        allow for this, the Definitions InsertBuffer can declare a dependency on
        the Wordform InsertBuffer, so that all previously-added Wordform objects
        will really exist before inserting any new Definition objects. These
        extra buffer flushes are slightly less efficient but there is still good
        batching, especially for the leaf objects.

        `trigger_deps` is a separate argument so that calling code can specify
        `deps` in a static manner while dynamically toggling whether they are
        used.
        """
        self._manager = manager
        self._count = count
        self._buffer = []
        self._assign_id = assign_id
        self._trigger_deps = trigger_deps
        self._deps = deps

        if self._assign_id:
            max_id = manager.aggregate(Max("id"))["id__max"]
            if max_id is None:
                max_id = 0
            self._next_id = max_id + 1

    def add(self, obj):
        """
        Add an object to the insert buffer. Also assign an id if assign_id is set.

        If the buffer is full, save the objects already in the buffer to the
        database.

        Note that the newly-added object itself is never saved during the add()
        call in which it is added, in case you want to do something with the
        assigned ID before the object gets saved.

        That is, it’s safe to

            foo = Foo(…)
            buffer.add(foo)
            foo.some_field = foo.id

        without needing to explicitly call `foo.save()`.
        """
        if len(self._buffer) >= self._count:
            self.save()

        if self._assign_id:
            if obj.id is None:
                obj.id = self._next_id
                self._next_id += 1
            else:
                raise Exception(
                    f"Passed object {obj} with existing id when assign_id=True"
                )

        self._buffer.append(obj)

    def save(self):
        if len(self._buffer) > 0:
            if self._trigger_deps:
                for d in self._deps:
                    d.save()

            self._manager.bulk_create(self._buffer)
            self._buffer = []


class FreshnessCheck:
    """
    Encapsulation of checking whether importjson content has changed since last
    import

    Checks are done by lemma. The lemma entry and all associated formOf entries
    are combined into a list, sorted, converted to JSON, and then a hash is
    taken of that string. If the hash already in the database matches the hash
    computed from the importjson input file, then we can assume the DB entry is
    fresh.
    """

    def __init__(self, new_data):
        """
        Create a new FreshnessCheck that will compare the DB to `new_data`.

        `new_data` should be a Python list of importjsondata; it could be loaded
        with `json.loads(importjsonfile.read())`
        """
        self._db_hashes_by_slug = {
            slug: hash
            for (slug, hash) in Wordform.objects.filter(
                is_lemma=True, import_hash__isnull=False
            ).values_list("slug", "import_hash")
        }

        entries_by_slug = defaultdict(list)
        for entry in new_data:
            if "slug" in entry:
                slug = entry["slug"]
            elif "formOf" in entry:
                slug = entry["formOf"]
            else:
                raise Exception(
                    f"Encountered entry without 'slug' or 'formOf' fields: {entry!r}"
                )
            entries_by_slug[slug].append(entry)

        importjson_hashes_by_slug = {}
        for slug, entries in entries_by_slug.items():
            # Same sort order as what sortimportjson uses
            entries.sort(key=entry_sort_key)
            # sort_keys is important
            entry_list_as_json = json.dumps(
                entries, ensure_ascii=False, indent=0, sort_keys=True
            ).encode("UTF-8")
            hash = hashlib.sha256(entry_list_as_json).hexdigest()[:20]
            importjson_hashes_by_slug[slug] = hash
        self._importjson_hash_for_slug = importjson_hashes_by_slug

    def db_hash_for_slug(self, slug):
        return self._db_hashes_by_slug.get(slug)

    def importjson_hash_for_slug(self, slug):
        return self._importjson_hash_for_slug[slug]

    def is_fresh(self, slug):
        db_hash = self.db_hash_for_slug(slug)
        if db_hash is None:
            return False
        importjson_hash = self.importjson_hash_for_slug(slug)
        return db_hash == importjson_hash


class Import:
    def __init__(
        self,
        importjson: list,
        translate_wordforms: bool,
        purge: bool,
        incremental: bool,
        atomic=True,
    ):
        """
        Create an Import process.

        If atomic is False, this will use batch processing that still works when
        not in a transaction.
        """
        self.dictionary_source_cache = DictionarySourceCache()
        self.data = importjson
        self.translate_wordforms = translate_wordforms
        self.incremental = incremental
        self.purge = purge

        self._has_run = False

        self.paradigm_manager = default_paradigm_manager()
        self.translation_stats = TranslationStats()

        trigger_deps = not atomic

        self.wordform_buffer = InsertBuffer(Wordform.objects, assign_id=True)
        self.definition_buffer = InsertBuffer(
            Definition.objects,
            assign_id=True,
            trigger_deps=trigger_deps,
            deps=[self.wordform_buffer],
        )
        self.citation_buffer = InsertBuffer(
            Definition.citations.through.objects,
            trigger_deps=trigger_deps,
            deps=[self.definition_buffer],
        )
        self.source_language_keyword_buffer = InsertBuffer(
            SourceLanguageKeyword.objects,
            trigger_deps=trigger_deps,
            deps=[self.wordform_buffer],
        )
        self.target_language_keyword_buffer = InsertBuffer(
            TargetLanguageKeyword.objects,
            trigger_deps=trigger_deps,
            deps=[self.wordform_buffer],
        )

    def run(self):
        """Run the import process.

        This is the only method that external code should call.
        """
        if self._has_run:
            raise Exception("run can only be called once")
        self._has_run = True

        freshness_check = FreshnessCheck(self.data)

        seen_slugs = set()
        if self.purge:
            existing_slugs = self.gather_slugs()

        form_definitions = []

        for entry in tqdm(self.data, smoothing=0):
            if "formOf" in entry:
                form_definitions.append(entry)
                continue

            if len(entry["senses"]) == 0:
                raise Exception(f'Error: no senses for slug {entry["slug"]}')
            for sense in entry["senses"]:
                if "definition" not in sense:
                    raise Exception(
                        f'Error: no "definition" in sense {sense!r} of slug {entry["slug"]}'
                    )

            seen_slugs.add(validate_slug_format(entry["slug"]))

            if self.incremental and freshness_check.is_fresh(entry["slug"]):
                continue

            if existing := Wordform.objects.filter(slug=entry["slug"]).first():
                # Cascade should take care of all related objects.
                existing.delete()

            fst_lemma = None
            if "fstLemma" in entry:
                fst_lemma = entry["fstLemma"]
            elif (analysis := entry.get("analysis")) is not None:
                fst_lemma = analysis[1]

            wf = Wordform(
                text=entry["head"],
                raw_analysis=entry.get("analysis", None),
                fst_lemma=fst_lemma,
                paradigm=entry.get("paradigm", None),
                slug=entry["slug"],
                is_lemma=True,
                linguist_info=entry.get("linguistInfo", {}),
                import_hash=freshness_check.importjson_hash_for_slug(entry["slug"]),
            )
            self.wordform_buffer.add(wf)
            assert wf.id is not None
            wf.lemma_id = wf.id

            if "senses" not in entry:
                raise Exception(
                    f"Invalid importjson: no senses for lemma text={wf.text} slug={wf.slug}"
                )

            self.populate_wordform_definitions(wf, entry["senses"])

            # Avoid dupes for this wordform
            seen_source_language_keywords: set[str] = set()

            slug_base = wf.slug.split("@")[0]
            if wf.text != slug_base and slug_base:
                self.add_source_language_keyword(
                    wf, slug_base, seen_source_language_keywords
                )
            if wf.fst_lemma and wf.text != wf.fst_lemma:
                self.add_source_language_keyword(
                    wf, wf.fst_lemma, seen_source_language_keywords
                )
            if wf.raw_analysis is None:
                self.index_unanalyzed_form(wf, seen_source_language_keywords)

        # Make sure everything is saved for upcoming formOf queries
        self.flush_insert_buffers()

        for entry in form_definitions:
            if self.incremental and freshness_check.is_fresh(entry["formOf"]):
                continue

            try:
                lemma = Wordform.objects.get(slug=entry["formOf"])
            except Wordform.DoesNotExist:
                raise Exception(
                    f"Encountered wordform with formOf for unknown slug={entry['formOf']!r}"
                )

            # If translate_wordforms is enabled, a Wordform for this inflection
            # may already have been created.
            wf = Wordform.objects.get_or_create(
                lemma=lemma,
                text=entry["head"],
                raw_analysis=entry["analysis"],
            )[0]
            self.create_definitions(wf, entry["senses"])

        self.flush_insert_buffers()

        if self.translate_wordforms:
            logger.info("Translation stats: %s", self.translation_stats)

        if self.purge:
            rows, breakdown = Wordform.objects.filter(
                slug__in=existing_slugs - seen_slugs
            ).delete()
            if rows:
                logger.warning(
                    f"Purged {rows:,} rows from database for existing entries not found in import file: %r",
                    breakdown,
                )

        timestamp = time.time()
        stamp, created = ImportStamp.objects.get_or_create(
            defaults={"timestamp": timestamp}
        )
        if not created:
            stamp.timestamp = time.time()
            stamp.save()

        call_command("builddefinitionvectors")

    def populate_wordform_definitions(self, wf, senses):
        should_do_translation = self.translate_wordforms

        if should_do_translation:
            has_analysis_and_paradigm = (
                (wf.analysis and wf.paradigm)
                if not settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT
                else (wf.fst_lemma and wf.paradigm)
            )

            if not has_analysis_and_paradigm:
                should_do_translation = False

        definitions_and_sources = self.create_definitions(wf, senses)

        if not should_do_translation:
            return

        lemma_text = (
            wf.text
            if not settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT
            else wf.fst_lemma
        )

        for (
            prefix_tags,
            suffix_tags,
        ) in self.paradigm_manager.all_analysis_template_tags(wf.paradigm):
            analysis = RichAnalysis((prefix_tags, lemma_text, suffix_tags))
            for generated in strict_generator().lookup(analysis.smushed()):
                # Skip re-instantiating lemma
                if analysis == wf.analysis:
                    continue

                inflected_wordform = Wordform(
                    # For now, leaving paradigm and linguist_info empty;
                    # code can get that info from the lemma instead.
                    text=generated,
                    raw_analysis=analysis.tuple,
                    lemma=wf,
                    is_lemma=False,
                )

                for d, sources in definitions_and_sources:

                    translation = translate_single_definition(
                        inflected_wordform, d.text, self.translation_stats
                    )
                    if translation is None:
                        continue

                    is_inflected_wordform_unsaved = inflected_wordform.id is None
                    if is_inflected_wordform_unsaved:
                        self.wordform_buffer.add(inflected_wordform)

                    self._add_definition(
                        inflected_wordform,
                        translation,
                        ("🤖" + source for source in sources),
                        auto_translation_source=d,
                    )

    def _add_definition(self, wordform, text, sources: list[str], **kwargs):
        """Lower-level method to add a definition.

        Note that this method does *NOT* index keyword definitions. For that,
        you want the `create_definitions` method.
        """
        d = Definition(wordform=wordform, text=text, **kwargs)
        self.definition_buffer.add(d)
        for s in sources:
            self.citation_buffer.add(
                Definition.citations.through(
                    dictionarysource_id=self.dictionary_source_cache.get_or_create(
                        s
                    ).abbrv,
                    definition_id=d.id,
                )
            )
        return d

    def create_definitions(self, wordform, senses):
        """Create definition objects for the given wordform and senses."""

        # Normally definition.citations.all() would tell you the sources, but to
        # allow batching of inserts we have to work with objects that have not
        # yet been inserted. And we can’t query relations using the Django API
        # on those.
        definitions_and_sources = []

        keywords = set()

        for sense in senses:
            kwargs = {}
            if "semanticDefinition" in sense:
                kwargs["raw_semantic_definition"] = sense["semanticDefinition"]
            if "coreDefinition" in sense:
                kwargs["raw_core_definition"] = sense["coreDefinition"]

            new_definition = self._add_definition(
                wordform, sense["definition"], sense["sources"], **kwargs
            )
            definitions_and_sources.append((new_definition, sense["sources"]))

            keywords.update(stem_keywords(new_definition.semantic_definition))

        for kw in keywords:
            self.target_language_keyword_buffer.add(
                TargetLanguageKeyword(text=kw, wordform=wordform)
            )

        return definitions_and_sources

    def gather_slugs(self):
        # For purging, this is used to track what existed initially
        return {
            v[0]
            for v in Wordform.objects.filter(slug__isnull=False).values_list("slug")
        }

    def flush_insert_buffers(self):
        self.wordform_buffer.save()
        self.definition_buffer.save()
        self.citation_buffer.save()
        self.source_language_keyword_buffer.save()
        self.target_language_keyword_buffer.save()

    def index_unanalyzed_form(self, wordform, seen):
        """Index unanalyzed forms such as phrases, Cree preverbs

        These get put into the SourceLanguageKeyword table.
        """
        keywords = set(
            to_source_language_keyword(piece) for piece in wordform.text.split()
        )

        for kw in keywords:
            self.add_source_language_keyword(wordform, kw, seen)

    def add_source_language_keyword(
        self, wordform: Wordform, keyword: str, seen: set[str]
    ):
        if keyword in seen:
            return

        self.source_language_keyword_buffer.add(
            SourceLanguageKeyword(wordform=wordform, text=keyword)
        )
        seen.add(keyword)


class Command(BaseCommand):
    help = """Update the database from an importjson file

    This command loads the dictionary data in an importjson file into the
    morphodict database. When run against an already-populated database, it
    synchronizes the database to match the contents of the importjson file.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        parser.add_argument(
            "--purge",
            action=BooleanOptionalAction,
            default=False,
            help="""
                Delete all existing entries that are not found in this import
                file. Used for importing a full dictionary file when keys may
                have changed.
            """,
        )
        parser.add_argument(
            "--atomic",
            action=BooleanOptionalAction,
            default=settings.DEBUG,
            help="""
                Run the import in a single transaction. This will make the
                import run much faster, but will lock up the database so that
                other processes can’t access it. Good for development use.
            """,
        )
        parser.add_argument(
            "--translate-wordforms",
            action=BooleanOptionalAction,
            default=settings.MORPHODICT_SUPPORTS_AUTO_DEFINITIONS,
            help="""
                Whether to attempt to provide automatic translations for
                inflected forms
            """,
        )
        parser.add_argument(
            "--incremental",
            action=BooleanOptionalAction,
            default=False,
            help="""
                Skip import of lemmas and their related forms if the associated
                importjson content has not changed since they were last
                imported.

                You will not want to use this if the language FSTs, the paradigm
                tables, or the phrase translation FSTs have been updated since
                the last import.
            """,
        )
        parser.add_argument(
            "json_file",
            help=f"The importjson file to import",
            nargs="?",
            default=DEFAULT_IMPORTJSON_FILE,
        )

    def handle(
        self,
        json_file,
        purge,
        atomic,
        translate_wordforms,
        incremental=False,
        **options,
    ):
        logger.info(f"Importing {json_file}")
        data = json.loads(Path(json_file).read_text())

        imp = Import(
            importjson=data,
            purge=purge,
            atomic=atomic,
            translate_wordforms=translate_wordforms,
            incremental=incremental,
        )

        if atomic:
            with transaction.atomic():
                imp.run()
        else:
            imp.run()


def validate_slug_format(proposed_slug):
    """Raise an error if the proposed slug is invalid

    For example, if contains a slash."""

    # a regex would run faster, but getting the quoting right for a literal
    # backslash probably isn’t worth it
    FORBIDDEN_SLUG_CHARS = "/\\ "
    if any(c in FORBIDDEN_SLUG_CHARS for c in proposed_slug):
        raise Exception(
            f"{proposed_slug=!r} contains one of the forbidden slug chars {FORBIDDEN_SLUG_CHARS!r}"
        )

    return proposed_slug
