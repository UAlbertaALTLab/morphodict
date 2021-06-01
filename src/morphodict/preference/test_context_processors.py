import pytest
from django.http import HttpRequest
from django.template import RequestContext, Template
from pytest_django.asserts import assertHTMLEqual

from morphodict.preference import Preference


@pytest.fixture(autouse=True)
def ensure_context_processors_are_enabled(settings):
    desired_processor = "morphodict.preference.context_processors.preferences"
    settings.TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": [desired_processor]},
        }
    ]


def test_can_access_choice_and_labels_in_template():
    class CheesePizza(Preference):
        choices = {
            "mozza": "mozzarella",
            "ricotta": "Ricotta",
            "vegan": "Daiya",
            "none": "no cheese",
        }
        default = "none"

    request = HttpRequest()
    empty_context = RequestContext(request, {})
    template = Template(
        """
    {% for choice, label in preferences.cheese_pizza.choices_with_labels %}
        <option value="{{ choice }}">{{ label|title }}</option>
    {% endfor %}
    """
    )

    html = template.render(empty_context)

    assertHTMLEqual(
        html,
        """
        <option value="mozza">Mozzarella</option>
        <option value="ricotta">Ricotta</option>
        <option value="vegan">Daiya</option>
        <option value="none">No Cheese</option>
    """,
    )
