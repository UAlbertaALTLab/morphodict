import pytest
from django.http import HttpRequest
from django.template import RequestContext, Template
from pytest_django.asserts import assertHTMLEqual

from morphodict.preference import register_preference


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
    @register_preference
    class CheesePizza:
        choices = {
            "mozza": "mozzarella",
            "ricotta": "Ricotta",
            "vegan": "Daiya",
            "none": "no cheese",
        }
        default = "none"

    request = HttpRequest()
    empty_context = RequestContext(request, {})
    template = Template("""
    {% for choice, label in preferences.cheese_pizza.choices_with_labels %}
        <option value="{{ choice }}">{{ label|title }}</option>
    {% endfor %}
    """)

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


@pytest.mark.parametrize(
    "choice,label", [(None, "cats"), ("cat", "cats"), ("dog", "dogs")]
)
def test_choice_and_label_from_request_context(choice, label):
    @register_preference
    class Pets:
        cookie_name = "pet"
        choices = {"cat": "cats", "dog": "dogs"}
        default = "cat"  # Debatable

    assert choice is None or choice in Pets.choices

    request = HttpRequest()
    if choice is not None:
        request.COOKIES[Pets.cookie_name] = choice
    context_that_likes_label = RequestContext(request, {})
    template = Template("""
        I like {{ preferences.pets.current_label }}.
    """)
    rendered = template.render(context_that_likes_label)

    assert rendered.strip() == f"I like {label}."
