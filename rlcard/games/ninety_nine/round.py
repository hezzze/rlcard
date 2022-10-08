# -*- coding: utf-8 -*-
"""Limit texas holdem round class implementation"""
import re
from rlcard.games.ninety_nine import PlayerStatus
from rlcard.games.ninety_nine.utils import (
    SINGLE_ACTION,
    DUAL_ACTION,
    CHOOSE_ACTION,
    action_to_card,
)


class NinetyNineRound:
    """Round can call other Classes' functions to keep the game running"""

    def __init__(self, dealer, num_players, np_random):
        """
        Initialize the round class

        Args:
            raise_amount (int): the raise amount for each raise
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
        """
        self.np_random = np_random
        self.num_players = num_players

        # initial points
        self.points = 0

        self.dealer = dealer
        self.game_pointer = 0
        self.direction = 1
        self.played_cards = []

        self.next_turn_idx = -1

    # def start_new_round(self, game_pointer, raised=None):
    #     """
    #     Start a new bidding round

    #     Args:
    #         game_pointer (int): The game_pointer that indicates the next player
    #         raised (list): Initialize the chips for each player

    #     Note: For the first round of the game, we need to setup the big/small blind
    #     """
    #     self.game_pointer = game_pointer
    #     self.have_raised = 0
    #     self.not_raise_num = 0
    #     if raised:
    #         self.raised = raised
    #     else:
    #         self.raised = [0 for _ in range(self.num_players)]

    def proceed_round(self, players, action):
        """
        Call other classes functions to keep one round running

        1. remove the corresponding card from players hand since
        since an action is decided
        2. take effect
        3. draw/no draw card based on card effect
        4. check & set player status, and setup for next round

        Args:
            players (list): The list of players that play the game
            action (str): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        """
        if action not in self.get_legal_actions(players):
            raise Exception(
                "{} is not legal action. Legal actions: {}".format(
                    action, self.get_legal_actions(players)
                )
            )

        # action is of format "CA->0"/"HK"/"ST+"
        # valid_suit = ['S', 'H', 'D', 'C']
        # valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        ### 1
        card_to_play = action_to_card(action)
        self.played_cards.append(card_to_play)
        players[self.game_pointer].hand.remove(card_to_play)

        # normal cards: 6  (2,3,5,6,8,9)
        #     special cards
        #     1 x 2 = 2 (4, K)
        #     2 x 2 = 4 (10, Q)
        #     4 x 3 = 12 (A, 7, J)

        ### 2
        can_draw = True
        card_effect = action[1:]

        if card_effect in ["2", "3", "5", "6", "8", "9"]:
            self.points += int(card_effect)

        elif card_effect in ["T+", "T-", "Q+", "Q-"]:
            if card_effect == "T+":
                self.points += 10
            elif card_effect == "T-":
                self.points -= 10
            elif card_effect == "Q+":
                self.points += 20
            else:
                self.points -= 20

        elif re.search(r"[A|7|J]->(\d+)", card_effect):
            match = re.match(r"([A|7|J])->(\d+)", card_effect)
            type = match.group(1)
            target_idx = int(match.group(2))
            if players[target_idx].status != PlayerStatus.ALIVE:
                raise Exception(
                    "player #{} is dead. Illegal action!".format(target_idx)
                )
            if type == "A":  # choose next player
                self.next_turn_idx = target_idx

            elif type == "7":  # exchange cards with a player
                can_draw = False
                tmp_hand = players[self.game_pointer].hand
                players[self.game_pointer].hand = players[target_idx].hand
                players[target_idx].hand = tmp_hand

            elif type == "J":  # draw a card from another player
                can_draw = False
                target = players[target_idx]
                draw_idx = self.np_random.randint(0, len(target.hand))
                card_drawn = target.hand.pop(draw_idx)
                players[self.game_pointer].hand.append(card_drawn)
                pass

        elif card_effect == "4":
            self.direction = -self.direction

        elif card_effect == "K":
            self.points = 99

        ### 3
        if can_draw:
            if not self.dealer.deck:
                self.replace_deck()

            new_card = self.dealer.deck.pop()
            players[self.game_pointer].hand.append(new_card)

        ### 4

        if self.points > 99:
            # reset point
            self.points = 99
            # current player is declared dead
            players[self.game_pointer].status = PlayerStatus.DEAD

        for p in players:
            if len(p.hand) == 0:
                p.status = PlayerStatus.DEAD

        # move to the next player
        # Skip the dead players
        # if next turn is active, go straight to that player
        if self.next_turn_idx >= 0:
            self.game_pointer = self.next_turn_idx

            # reset next turn idx
            self.next_turn_idx = -1
        else:
            self.game_pointer = (self.game_pointer + self.direction) % self.num_players
            while players[self.game_pointer].status == PlayerStatus.DEAD:
                self.game_pointer = (
                    self.game_pointer + self.direction
                ) % self.num_players

        # game over will be checked in game.is_over()
        return self.game_pointer

    def get_legal_actions(self, players):
        """
        Obtain the legal actions for the current player


        Returns:
           (list):  A list of legal actions
        """
        full_actions = []
        hand = players[self.game_pointer].hand

        for card in hand:
            if card.rank in SINGLE_ACTION:
                full_actions.append(card.get_index())
            elif card.rank in DUAL_ACTION:
                # two actions each, plus/minus
                full_actions.extend([f"{card.get_index()}+", f"{card.get_index()}-"])
            elif card.rank in CHOOSE_ACTION:
                full_actions.extend(
                    [
                        f"{card.get_index()}->{idx}"
                        for idx in range(self.num_players)
                        if players[idx].status == PlayerStatus.ALIVE
                        and idx != self.game_pointer
                    ]
                )

        return full_actions

    def replace_deck(self):
        """Add cards have been played to deck"""
        self.dealer.deck.extend(self.played_cards)
        self.dealer.shuffle()
        self.played_cards = []
