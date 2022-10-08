from enum import Enum


class PlayerStatus(Enum):
    ALIVE = 0
    DEAD = 1


class NinetyNinePlayer:
    def __init__(self, player_id, np_random):
        """
        Initialize a player.

        Args:
            player_id (int): The id of the player
        """
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []  # A list of Card from base.py
        self.status = PlayerStatus.ALIVE

    def get_state(self, played_cards, legal_actions):
        """
        Encode the state for the player

        Args:
            played_cards (list): A list of played cards that seen by all the players

        Returns:
            (dict): The state of the player
        """
        return {
            "hand": [c.get_index() for c in self.hand],
            "played_cards": [c.get_index() for c in played_cards],
            "legal_actions": legal_actions,
        }

    def get_player_id(self):
        return self.player_id
