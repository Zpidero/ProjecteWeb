import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")
django.setup()

from behave import given, when, then
from django.contrib.auth.models import User
from myapp.models import Teams, Players, Lineup, Futdraft


TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"


@given("there is a registered user")
def step_registered_user(context):
    User.objects.filter(username=TEST_USERNAME).delete()

    context.user = User.objects.create_user(
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )


@given("there are players and a lineup in the database")
def step_players_and_lineup(context):
    team, _ = Teams.objects.get_or_create(
        name="Raimon",
        defaults={"image": "https://example.com/raimon.png"}
    )

    context.player = Players.objects.create(
        image="https://example.com/player.png",
        name="Mark Evans",
        nickname="Mark",
        game="Inazuma Eleven",
        archetype="Goalkeeper",
        position="GK",
        element="Mountain",
        team=team,
        power=90,
        control=90,
        technique=90,
        pressure=90,
        physical=90,
        agility=90,
        intelligence=90,
        total=950,
        age_group="Junior",
        school_year="1",
        gender="Male",
        role="Player"
    )

    context.lineup, _ = Lineup.objects.get_or_create(
        name="4-3-3",
        defaults={
            "image": "https://example.com/lineup.png",
            "forwards": 3,
            "midfielders": 3,
            "defenders": 4,
            "goalKeeper": 1,
        }
    )


@when("I go to my drafts page without logging in")
def step_go_my_drafts_anonymous(context):
    context.browser.visit(context.base_url + "/my-drafts/")


@when("I log in")
def step_login(context):
    browser = context.browser

    browser.visit(context.base_url + "/login/")
    browser.fill("username", TEST_USERNAME)
    browser.fill("password", TEST_PASSWORD)
    browser.find_by_css("button[type='submit']").click()


@when('I create a draft named "{draft_name}"')
def step_create_draft(context, draft_name):
    browser = context.browser

    payload = {
        "name": draft_name,
        "formation": "4-3-3",
        "players": [context.player.id],
    }

    browser.visit(context.base_url + "/game/")

    browser.execute_script(
        """
        return fetch('/save-draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.cookie
                    .split('; ')
                    .find(row => row.startsWith('csrftoken='))
                    ?.split('=')[1]
            },
            body: JSON.stringify(arguments[0])
        }).then(response => response.json());
        """,
        payload
    )


@then("I should be redirected to the login page")
def step_redirect_login(context):
    assert "/login/" in context.browser.url


@then('I should see the draft "{draft_name}" in my drafts page')
def step_see_draft(context, draft_name):
    context.browser.visit(context.base_url + "/my-drafts/")

    assert draft_name in context.browser.html

    assert Futdraft.objects.filter(
        name=draft_name,
        user=context.user
    ).exists()