import json
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
from django.views.generic import TemplateView

from . import RESULTS_DIR, DEFAULT_SAMPLE_FILE
from .analyze_results import analyze, load_results_file, count_and_annotate_dupes
from .sample import load_sample_definition, gen_run_sample

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

        context["name"] = file.name
        analysis = analyze(file, load_sample_definition(DEFAULT_SAMPLE_FILE))
        context["analysis"] = analysis

        for k in [
            "topthree_score_percent",
            "threeten_score_percent",
            "total_duplicate_count",
            "time_taken_seconds",
        ]:
            context[f"average_{k}"] = mean(r[k] for r in analysis.values())

        return context


@staff_member_required
def run(request):
    if request.method != "POST":
        raise Http404()

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

        for status in gen_run_sample(out_file=out_file):
            yield conditional_escape(status) + "\n"

        done_url = reverse(
            "search_quality:results-analysis",
            kwargs={"path": out_file.name},
        )

        yield f'</pre><a href="{conditional_escape(done_url)}">Done!</a>'

    # Sadly, although this old trick for sending out a live-updating web page
    # works with Firefox and Chrome, it doesn’t seem to work with Safari. And it
    # doesn’t seem worth it to set up websockets or a ‘progress_message’
    # database table just for this.
    return StreamingHttpResponse(executor())
