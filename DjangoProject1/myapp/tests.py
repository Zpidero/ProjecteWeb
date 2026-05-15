from django.contrib.auth.models import User
from django.test import TestCase

from .models import Teams, Players, Lineup, Futdraft


class FutdraftTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="testpassword123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="testpassword123"
        )

        self.team = Teams.objects.create(
            name="Raimon",
            image="https://example.com/raimon.png"
        )

        self.lineup = Lineup.objects.create(
            name="4-3-3",
            image="https://example.com/lineup.png",
            forwards=3,
            midfielders=3,
            defenders=4,
            goalKeeper=1
        )

        self.player1 = Players.objects.create(
            image="https://example.com/player1.png",
            name="Mark Evans",
            nickname="Mark",
            game="Inazuma Eleven",
            archetype="Goalkeeper",
            position="GK",
            element="Mountain",
            team=self.team,
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

        self.player2 = Players.objects.create(
            image="https://example.com/player2.png",
            name="Axel Blaze",
            nickname="Axel",
            game="Inazuma Eleven",
            archetype="Striker",
            position="FW",
            element="Fire",
            team=self.team,
            power=95,
            control=88,
            technique=92,
            pressure=85,
            physical=91,
            agility=90,
            intelligence=87,
            total=960,
            age_group="Junior",
            school_year="1",
            gender="Male",
            role="Player"
        )

        self.draft = Futdraft.objects.create(
            name="My first draft",
            user=self.user1,
            lineup=self.lineup,
            player_order=[self.player1.id, self.player2.id]
        )
        self.draft.players.set([self.player1, self.player2])

    def test_draft_is_associated_with_user(self):
        """A Futdraft is properly associated with the user who created it"""
        draft = Futdraft.objects.get(name="My first draft")

        self.assertEqual(draft.user, self.user1)
        self.assertEqual(draft.name, "My first draft")

    def test_draft_has_players(self):
        """A Futdraft can contain selected players"""
        draft = Futdraft.objects.get(name="My first draft")

        self.assertEqual(draft.players.count(), 2)
        self.assertIn(self.player1, draft.players.all())
        self.assertIn(self.player2, draft.players.all())

    def test_draft_keeps_player_order(self):
        """A Futdraft stores the selected player order"""
        draft = Futdraft.objects.get(name="My first draft")

        self.assertEqual(draft.player_order, [self.player1.id, self.player2.id])

    def test_user_only_gets_own_drafts(self):
        """Filtering drafts by user only returns drafts created by that user"""
        Futdraft.objects.create(
            name="Other user draft",
            user=self.user2,
            lineup=self.lineup,
            player_order=[self.player1.id]
        )

        user1_drafts = Futdraft.objects.filter(user=self.user1)
        user2_drafts = Futdraft.objects.filter(user=self.user2)

        self.assertEqual(user1_drafts.count(), 1)
        self.assertEqual(user2_drafts.count(), 1)
        self.assertEqual(user1_drafts.first().name, "My first draft")
        self.assertEqual(user2_drafts.first().name, "Other user draft")

    def test_draft_can_be_updated(self):
        """A Futdraft name can be updated"""
        draft = Futdraft.objects.get(name="My first draft")
        draft.name = "Updated draft"
        draft.save()

        updated_draft = Futdraft.objects.get(id=draft.id)
        self.assertEqual(updated_draft.name, "Updated draft")

    def test_draft_can_be_deleted(self):
        """A Futdraft can be deleted"""
        draft = Futdraft.objects.get(name="My first draft")
        draft_id = draft.id
        draft.delete()

        self.assertFalse(Futdraft.objects.filter(id=draft_id).exists())