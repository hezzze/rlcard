from ctypes import pointer
import unittest
import numpy as np

from rlcard.games.ninety_nine.game import NinetyNineGame as Game
from rlcard.games.ninety_nine.player import PlayerStatus
from rlcard.games.base import Card


class TestNinetyNineMethods(unittest.TestCase):
    def test_get_num_players(self):
        game = Game()
        num_players = game.get_num_players()
        self.assertEqual(num_players, 4)

    def test2(self):
        """
        Test illegal action
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("H", "5"))

        with self.assertRaises(Exception) as cm:
            game.step("S5")
        self.assertTrue("is not legal action" in cm.exception.args[0])

    def test3(self):
        """
        play 3 of spades, points increase 3, turn updated
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "3"))

        state, pointer = game.step("S3")
        self.assertEqual(state["points"], 3)
        self.assertEqual(pointer, 1)

    def test4(self):
        """
        play 3 of spades when points is 99, player dead
        """
        game = get_new_game()
        game.round.points = 99

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "3"))
        game.players[0].hand.append(Card("S", "8"))

        state, pointer = game.step("S8")
        self.assertEqual(game.players[0].status, PlayerStatus.DEAD)
        self.assertEqual(state["points"], 99)

    def test5(self):
        """
        play 4 of spades, direction switched
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "4"))

        state, pointer = game.step("S4")
        self.assertEqual(pointer, 3)  # -1 % 4 = 3

    def test6a(self):
        """
        played 7, go to used, player will not draw a card
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "4"))
        game.players[0].hand.append(Card("D", "7"))

        game.step("D7->1")
        self.assertEqual(len(game.players[0].hand), 5)
        self.assertEqual(len(game.players[1].hand), 1)
        self.assertTrue(Card("D", "7") in game.round.played_cards)

    def test6b(self):
        """
        played J, go to used, player will not draw a card
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("H", "4"))
        game.players[0].hand.append(Card("C", "J"))

        game.step("CJ->2")
        self.assertEqual(len(game.players[0].hand), 2)
        self.assertEqual(len(game.players[2].hand), 4)
        self.assertTrue(Card("C", "J") in game.round.played_cards)

    def test7(self):
        """
        used card get reshuffled and form a new unused deck
        """
        game = get_new_game()

        card1 = Card("S", "9")
        card2 = Card("H", "2")
        card3 = Card("C", "8")
        card4 = Card("D", "Q")

        game.round.played_cards.extend([card1, card2, card3, card4])

        card_to_play = Card("H", "K")
        game.players[0].hand.clear()
        game.players[0].hand.append(card_to_play)

        game.dealer.deck.clear()

        game.step("HK")

        # player will draw one of the card after new deck is created and shuffled
        self.assertTrue(
            game.players[0].hand[0] in [card1, card2, card3, card4, card_to_play]
        )

        # played card is shuffled into the deck or be drawn back to players hand
        self.assertTrue(
            card_to_play in game.dealer.deck or card_to_play in game.players[0].hand
        )

    def test8(self):
        """
        after move one player busted, left only 1 player alive, game ends
        """
        game = get_new_game()
        game.round.points = 99

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("C", "5"))

        for idx, p in enumerate(game.players):
            if idx not in [0, 1]:
                p.status = PlayerStatus.DEAD

        game.step("C5")
        self.assertEqual(game.players[0].status, PlayerStatus.DEAD)
        self.assertTrue(game.is_over())

    def test_jack_2(self):
        """
        play jack of spades, draw a card from another player
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "J"))

        expected_count0 = len(game.players[0].hand)
        expected_count1 = len(game.players[1].hand) - 1

        game.step("SJ->1")

        self.assertEqual(len(game.players[0].hand), expected_count0)
        self.assertEqual(len(game.players[1].hand), expected_count1)

    def test_jack_3(self):
        """
        play jack of hearts, another player will be busted if only has one card,
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "J"))

        game.players[2].hand.clear()
        game.players[2].hand.append(Card("D", "A"))

        game.step("SJ->2")

        self.assertEqual(game.players[2].status, PlayerStatus.DEAD)

    def test_queen_1(self):
        """
        play queen, select plus to add 20
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("H", "Q"))

        state, _ = game.step("HQ+")

        self.assertEqual(state["points"], 20)

    def test_queen_2(self):
        """
        play queen, select minus to substract 20
        """
        game = get_new_game()
        orig_p = 99
        game.round.points = orig_p

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("D", "Q"))

        state, _ = game.step("DQ-")

        self.assertEqual(state["points"], orig_p - 20)

    def test_ten1(self):
        """
        play ten, select plus to substract 10
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "T"))

        state, _ = game.step("ST+")

        self.assertEqual(state["points"], 10)

    def test_ten2(self):
        """
        play ten, select minus to substract 20
        """
        game = get_new_game()
        orig_p = 99
        game.round.points = orig_p

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("C", "T"))

        state, _ = game.step("CT-")

        self.assertEqual(state["points"], orig_p - 10)

    def test_ace1(self):
        """
        play ace, choose the 2nd next player
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("S", "A"))

        _, pointer = game.step("SA->2")

        self.assertEqual(pointer, 2)

    def test_seven1(self):
        """
        play seven, choose a player then cards are exchanged
        """
        game = get_new_game()

        game.players[0].hand.clear()
        card0 = Card("H", "7")
        card1 = Card("D", "4")
        card2 = Card("C", "6")
        game.players[0].hand.extend([card0, card1, card2])

        game.players[1].hand.clear()
        card3 = Card("S", "Q")
        game.players[1].hand.append(card3)

        game.step("H7->1")

        self.assertTrue(card3 in game.players[0].hand)
        self.assertEqual(len(game.players[0].hand), 1)
        self.assertTrue(card1 in game.players[1].hand)
        self.assertTrue(card2 in game.players[1].hand)
        self.assertEqual(len(game.players[1].hand), 2)

    def test_seven3(self):
        """
        player only has one card, plays seven on another player, causes death
        """
        game = get_new_game()

        game.players[0].hand.clear()
        card0 = Card("C", "7")
        game.players[0].hand.append(card0)

        game.players[3].hand.clear()
        card1 = Card("S", "T")
        card2 = Card("S", "J")
        card3 = Card("H", "2")
        game.players[3].hand.extend([card1, card2, card3])

        game.step("C7->3")

        self.assertEqual(len(game.players[0].hand), 3)
        self.assertEqual(game.players[3].status, PlayerStatus.DEAD)

    def test_king1(self):
        """
        player plays king the point is set to 99
        """
        game = get_new_game()

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("D", "K"))

        state, _ = game.step("DK")

        self.assertEqual(state["points"], 99)

    def test_king2(self):
        """
        player plays king when the point is 99, point stays 99 and player lives
        """
        game = get_new_game()
        game.round.points = 99

        game.players[0].hand.clear()
        game.players[0].hand.append(Card("C", "K"))

        state, _ = game.step("CK")

        self.assertEqual(state["points"], 99)
        self.assertEqual(game.players[0].status, PlayerStatus.ALIVE)


def get_new_game():
    game = Game()
    game.init_game()
    return game


if __name__ == "__main__":
    unittest.main()
