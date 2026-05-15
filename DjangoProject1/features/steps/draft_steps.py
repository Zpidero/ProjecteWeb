import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")
django.setup()

from behave import given, when, then
from django.contrib.auth.models import User
from myapp.models import Teams, Players, Lineup, Futdraft


TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"

OTHER_USERNAME = "otheruser"
OTHER_PASSWORD = "otherpassword123"

def create_test_player():
    team, _ = Teams.objects.get_or_create(
        name="Raimon",
        defaults={"image": "https://example.com/raimon.png"}
    )

    player = Players.objects.create(
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

    return player


def get_or_create_test_lineup():
    lineup, _ = Lineup.objects.get_or_create(
        name="4-3-3",
        defaults={
            "image": "https://example.com/lineup.png",
            "forwards": 3,
            "midfielders": 3,
            "defenders": 4,
            "goalKeeper": 1,
        }
    )
    return lineup


def get_csrf_token_from_cookie(browser):
    cookies = browser.cookies.all()
    return cookies.get("csrftoken")


@given("there is a registered user")
def step_registered_user(context):
    User.objects.filter(username=TEST_USERNAME).delete()

    context.user = User.objects.create_user(
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )


@given("there are two registered users")
def step_two_registered_users(context):
    User.objects.filter(username=TEST_USERNAME).delete()
    User.objects.filter(username=OTHER_USERNAME).delete()

    context.user = User.objects.create_user(
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )

    context.other_user = User.objects.create_user(
        username=OTHER_USERNAME,
        password=OTHER_PASSWORD
    )


@given("there are players and a lineup in the database")
def step_players_and_lineup(context):
    context.player = create_test_player()
    context.lineup = get_or_create_test_lineup()


@given('the user has a draft named "{draft_name}"')
def step_user_has_draft(context, draft_name):
    player = getattr(context, "player", None) or create_test_player()
    lineup = getattr(context, "lineup", None) or get_or_create_test_lineup()

    context.draft = Futdraft.objects.create(
        name=draft_name,
        user=context.user,
        lineup=lineup,
        player_order=[player.id],
    )
    context.draft.players.set([player])


@given('the second user has a draft named "{draft_name}"')
def step_second_user_has_draft(context, draft_name):
    player = getattr(context, "player", None) or create_test_player()
    lineup = getattr(context, "lineup", None) or get_or_create_test_lineup()

    context.other_draft = Futdraft.objects.create(
        name=draft_name,
        user=context.other_user,
        lineup=lineup,
        player_order=[player.id],
    )
    context.other_draft.players.set([player])


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
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch('/save-draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': arguments[1]
            },
            body: JSON.stringify(arguments[0])
        }).then(response => response.json());
        """,
        payload,
        csrf_token
    )

    context.last_response = result


@when('I edit the draft "{old_name}" to "{new_name}"')
def step_edit_draft(context, old_name, new_name):
    browser = context.browser

    draft = Futdraft.objects.get(name=old_name, user=context.user)

    payload = {
        "draft_id": draft.id,
        "name": new_name,
        "formation": "4-3-3",
        "players": list(draft.players.values_list("id", flat=True)),
    }

    browser.visit(context.base_url + f"/draft/{draft.id}/edit/")
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch('/save-draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': arguments[1]
            },
            body: JSON.stringify(arguments[0])
        }).then(response => response.json());
        """,
        payload,
        csrf_token
    )

    context.last_response = result


@when('I delete the draft "{draft_name}"')
def step_delete_draft(context, draft_name):
    browser = context.browser

    draft = Futdraft.objects.get(name=draft_name, user=context.user)

    browser.visit(context.base_url + "/my-drafts/")
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch(arguments[0], {
            method: 'POST',
            headers: {
                'X-CSRFToken': arguments[1]
            }
        }).then(response => response.json());
        """,
        f"/draft/{draft.id}/delete/",
        csrf_token
    )

    context.last_response = result


@when("I try to edit the other user's draft")
def step_try_edit_other_user_draft(context):
    browser = context.browser

    draft = context.other_draft

    payload = {
        "draft_id": draft.id,
        "name": "Hacked draft",
        "formation": "4-3-3",
        "players": list(draft.players.values_list("id", flat=True)),
    }

    browser.visit(context.base_url + "/game/")
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch('/save-draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': arguments[1]
            },
            body: JSON.stringify(arguments[0])
        }).then(response => {
            return {
                status: response.status,
                ok: response.ok
            };
        });
        """,
        payload,
        csrf_token
    )

    context.last_response = result


@when("I try to delete the other user's draft")
def step_try_delete_other_user_draft(context):
    browser = context.browser

    draft = context.other_draft

    browser.visit(context.base_url + "/my-drafts/")
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch(arguments[0], {
            method: 'POST',
            headers: {
                'X-CSRFToken': arguments[1]
            }
        }).then(response => {
            return {
                status: response.status,
                ok: response.ok
            };
        });
        """,
        f"/draft/{draft.id}/delete/",
        csrf_token
    )

    context.last_response = result


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


@then('I should not see the draft "{draft_name}" in my drafts page')
def step_not_see_draft(context, draft_name):
    context.browser.visit(context.base_url + "/my-drafts/")

    assert draft_name not in context.browser.html

    assert not Futdraft.objects.filter(
        name=draft_name,
        user=context.user
    ).exists()


@then("the request should fail with a security error")
def step_security_error(context):
    assert context.last_response["ok"] is False
    assert context.last_response["status"] in [400, 403, 404]

    if hasattr(context, "other_draft"):
        assert Futdraft.objects.filter(id=context.other_draft.id).exists()

@when("I try to create a draft with an empty name")
def step_create_draft_empty_name(context):
    browser = context.browser

    payload = {
        "name": "",
        "formation": "4-3-3",
        "players": [context.player.id],
    }

    browser.visit(context.base_url + "/game/")
    csrf_token = get_csrf_token_from_cookie(browser)

    result = browser.execute_script(
        """
        return fetch('/save-draft/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': arguments[1]
            },
            body: JSON.stringify(arguments[0])
        }).then(response => {
            return response.json().then(data => {
                return {
                    status: response.status,
                    ok: response.ok,
                    data: data
                };
            });
        });
        """,
        payload,
        csrf_token
    )

    context.last_response = result


@then('the draft creation should fail with the error "{error_message}"')
def step_draft_creation_should_fail(context, error_message):
    assert context.last_response["status"] == 400
    assert context.last_response["ok"] is False
    assert context.last_response["data"]["ok"] is False
    assert context.last_response["data"]["error"] == error_message