import logging
import time
from json import dumps
from statistics import mean

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    Http404,
    HttpResponse,
    StreamingHttpResponse,
    HttpResponseBadRequest,
)
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from . import RESULTS_DIR, DEFAULT_SAMPLE_FILE
from .analyze_results import analyze, load_results_file, count_and_annotate_dupes
from .run_sample import gen_run_sample
from .sample import load_sample_definition

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "search_quality/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["json_gz"] = (path.name for path in RESULTS_DIR.glob("*.json.gz"))
        return context


class ResultsAnalysisView(LoginRequiredMixin, TemplateView):
    template_name = "search_quality/results-analysis.html"

    def get(self, request, *args, **kwargs):
        # ?json=query returns JSON for query
        raw = request.GET.get("json", None)
        if raw:
            file = self._resolve_url_param_to_file(kwargs["path"])

            search_results = load_results_file(file)

            for k, v in search_results.items():
                if k == raw:
                    count_and_annotate_dupes(v["results"])
                    return HttpResponse(
                        dumps(v, ensure_ascii=False, indent=2),
                        content_type="application/json",
                    )
            raise Http404()

        return super().get(request, *args, **kwargs)

    def _resolve_url_param_to_file(self, file):
        file = RESULTS_DIR / file
        if not file.is_file():
            raise Http404()
        return file

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        file = self._resolve_url_param_to_file(kwargs["path"])

        sample_definition = load_sample_definition(DEFAULT_SAMPLE_FILE)
        context["name"] = file.name
        analysis = analyze(file, sample_definition)
        context["analysis"] = analysis
        context["sample_definition_length"] = len(sample_definition)
        queries = set(q["Query"] for q in sample_definition)
        result_set_length = len(
            queries.intersection(k for k, v in analysis.items() if v is not None)
        )
        context["result_set_length"] = result_set_length
        context["result_set_percent"] = 100 * result_set_length / len(sample_definition)

        for k in [
            "result_count",
            "threeten_score_percent",
            "time_taken_seconds",
            "topthree_score_percent",
            "total_duplicate_count",
        ]:
            context[f"average_{k}"] = mean(
                r[k] for r in analysis.values() if r is not None
            )

        return context


@staff_member_required
@require_http_methods(["POST"])
def run(request):
    label = request.POST.get("label", None)
    if label:
        label = slugify(label)
    else:
        label = time.strftime("%Y-%m-%d_T_%H_%M_%S")
    out_file = RESULTS_DIR / f"sample-{label}.json.gz"

    if out_file.exists():
        return HttpResponseBadRequest("File exists.")

    def executor():
        yield "<h1>Running sample</h1>\n<pre>"

        try:
            for status in gen_run_sample(out_file=out_file):
                yield conditional_escape(status) + "\n"

            results_url = reverse(
                "search_quality:results-analysis",
                kwargs={"path": out_file.name},
            )

            yield f'</pre>Done. <a href="{conditional_escape(results_url)}">View results</a>'
        except Exception as e:
            yield f"""</pre>
                <div style="color: red">Error: {conditional_escape(str(e))}</div>
                <div>Check the server log for more details.</div>"""
            raise

    # Sadly, although this old trick for sending out a live-updating web page
    # works with Firefox and Chrome, it doesn’t seem to work with Safari. And it
    # doesn’t seem worth it to set up websockets or a ‘progress_message’
    # database table just for this.
    return StreamingHttpResponse(executor())
