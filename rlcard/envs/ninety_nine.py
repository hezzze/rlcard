import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.ninety_nine import Game
from rlcard.games.ninety_nine.utils import (
    encode_hand,
    ACTION_SPACE,
    ACTION_LIST,
    cards2list,
)


class NinetyNineEnv(Env):
    def __init__(self, config):
        self.name = "ninety_nine"
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[2, 4, 13] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def _extract_state(self, state):
        obs = np.zeros((2, 4, 13), dtype=int)
        encode_hand(obs, state["hand"])
        legal_action_ids = self._get_legal_actions()
        extracted_state = {"obs": obs, "legal_actions": legal_action_ids}
        extracted_state["raw_obs"] = state
        extracted_state["raw_legal_actions"] = [a for a in state["legal_actions"]]
        extracted_state["action_record"] = self.action_recorder
        return extracted_state

    def get_payoffs(self):

        return np.array(self.game.get_payoffs())

    def _decode_action(self, action_id):
        legal_ids = self._get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        # if (len(self.game.dealer.deck) + len(self.game.round.played_cards)) > 17:
        #    return ACTION_LIST[60]
        return ACTION_LIST[np.random.choice(legal_ids)]

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {ACTION_SPACE[action]: None for action in legal_actions}
        return OrderedDict(legal_ids)

    def get_perfect_information(self):
        """Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        """
        state = {}
        state["num_players"] = self.num_players
        state["hand_cards"] = [cards2list(player.hand) for player in self.game.players]
        state["played_cards"] = cards2list(self.game.round.played_cards)
        state["points"] = self.game.round.points
        state["game_pointer"] = self.game.round.game_pointer
        state["direction"] = self.game.round.direction
        state["legal_actions"] = self.game.round.get_legal_actions(self.game.players)
        return state
