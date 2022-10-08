from copy import deepcopy, copy
import numpy as np

from rlcard.games.ninety_nine import Dealer
from rlcard.games.ninety_nine import Player, PlayerStatus
from rlcard.games.ninety_nine import Round

from rlcard.games.ninety_nine.utils import NUM_OF_PLAYERS


class NinetyNineGame:
    def __init__(self, allow_step_back=False):
        """Initialize the class limit holdem game"""
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()

        # Some configurations of the game
        # These arguments can be specified for creating new games

        # Small blind and big blind
        # self.small_blind = 1
        # self.big_blind = 2 * self.small_blind

        # Raise amount and allowed times
        # self.raise_amount = self.big_blind
        # self.allowed_raise_num = 4

        self.num_players = NUM_OF_PLAYERS

        # Save betting history
        # self.history_raise_nums = [0 for _ in range(4)]

        self.dealer = None
        self.players = None
        self.game_pointer = None
        self.round = None
        self.round_counter = None
        self.history = None

    def configure(self, game_config):
        """Specify some game specific parameters, such as number of players"""
        self.num_players = game_config["game_num_players"]

    def init_game(self):
        """
        Initialize the game of Ninety-Nine

        This version supports 4-player Ninety-Nine

        Returns:
            (tuple): Tuple containing:

                (dict): The first state of the game
                (int): Current player's id
        """
        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)

        # Initialize two players to play the game
        self.players = [Player(i, self.np_random) for i in range(self.num_players)]

        # Deal cards to each  player to prepare for the first round
        for i in range(5 * self.num_players):
            self.players[i % self.num_players].hand.append(self.dealer.deal_card())

        # The player next to the big blind plays the first
        # self.game_pointer = (b + 1) % self.num_players
        self.game_pointer = 0

        # Initialize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(
            dealer=self.dealer,
            num_players=self.num_players,
            np_random=self.np_random,
        )

        # Count the round.
        self.round_counter = 0

        # Save the history for stepping back to the last state.
        self.history = []

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer

    def step(self, action):
        """
        Get the next state

        Args:
            action (str): a specific action.

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next player id
        """
        if self.allow_step_back:
            # First snapshot the current state
            r = deepcopy(self.round)
            b = self.game_pointer
            p_c = self.round_counter
            d = deepcopy(self.dealer)
            p = deepcopy(self.round.played_cards)
            ps = deepcopy(self.players)
            self.history.append((r, b, p_c, d, p, ps))

        # Then we proceed to the next round
        self.game_pointer = self.round.proceed_round(self.players, action)

        self.round_counter += 1

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer

    def step_back(self):
        """
        Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        """
        if len(self.history) > 0:
            (
                self.round,
                self.game_pointer,
                self.round_counter,
                self.dealer,
                self.round.played_cards,
                self.players,
            ) = self.history.pop()
            return True
        return False

    def get_num_players(self):
        """
        Return the number of players in Ninety-Nine

        Returns:
            (int): The number of players in the game
        """
        return self.num_players

    @staticmethod
    def get_num_actions():
        """
        Return the number of applicable actions

        Returns:
            (int): The number of actions.
            normal cards: 1 x 6  (2,3,5,6,8,9)
            special cards
            1 x 2 (4, K)
            2 x 2 (10, Q)
            (num of players - 1) x 3 = 3(N-1) (A, 7, J)

            the above sum x 4 suits = total actions

            example:
            when NUM_OF_PLAYERS: 4
            get_num_actions() = 84

        """
        return (6 + 2 + 4 + 3 * (NUM_OF_PLAYERS - 1)) * 4

    def get_player_id(self):
        """
        Return the current player's id

        Returns:
            (int): current player's id
        """
        return self.game_pointer

    def get_state(self, game_pointer):
        """
        Return player's state

        Args:
            game_pointer (int): point to current player

        Returns:
            (dict): The state of the player
        """
        legal_actions = self.get_legal_actions()
        state = self.players[game_pointer].get_state(
            self.round.played_cards, legal_actions
        )
        state["points"] = self.round.points
        state["round_counter"] = self.round_counter
        state["game_pointer"] = self.round.game_pointer
        state["current_player"] = self.players[game_pointer]
        state["num_cards"] = [len(p.hand) for p in self.players]
        state["num_players"] = self.get_num_players()
        state["direction"] = self.round.direction

        return state

    def is_over(self):
        """
        Check if the game is over

        Returns:
            (boolean): True if the game is over
        """
        alive_players = [
            1 if p.status == PlayerStatus.ALIVE else 0 for p in self.players
        ]
        # If only one player is alive, the game is over.
        if sum(alive_players) == 1:
            return True

        return False

    def get_payoffs(self):
        """
        Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        """
        ### ~TODO : consider number of rounds, the less the more payoffs
        return [1 if p.status == PlayerStatus.ALIVE else 0 for p in self.players]

    def get_legal_actions(self):
        """
        Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """
        return self.round.get_legal_actions(self.players)
