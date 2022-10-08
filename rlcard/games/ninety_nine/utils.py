import numpy as np
from rlcard.games.base import Card
from collections import OrderedDict


# a map of color to its index
SUIT_MAP = {"S": 0, "H": 1, "D": 2, "C": 3}

RANK_MAP = {
    "A": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "T": 9,
    "J": 10,
    "Q": 11,
    "K": 12,
}

NUM_OF_PLAYERS = 4

SUITS = list(SUIT_MAP.keys())
SINGLE_ACTION = ["2", "3", "5", "6", "8", "9", "4", "K"]
DUAL_ACTION = ["T", "Q"]
CHOOSE_ACTION = ["A", "7", "J"]

ACTION_SPACE = {}
index = 0

for suit in SUITS:
    for action in SINGLE_ACTION:
        ACTION_SPACE[suit + action] = index
        index += 1
    for action in DUAL_ACTION:
        for sign in ["+", "-"]:
            ACTION_SPACE[suit + action + sign] = index
            index += 1
    for action in CHOOSE_ACTION:
        for idx in range(NUM_OF_PLAYERS):
            ACTION_SPACE[f"{suit}{action}->{idx}"] = index
            index += 1

ACTION_LIST = list(ACTION_SPACE.keys())


def action_to_card(action):
    """
    return the action str from a card

    action is of format "CA->0"/"HK"/"ST+"
    valid_suit = ['S', 'H', 'D', 'C']
    valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    Args:
        action (str): The action str


    Returns:
        rlcard.games.base.Card
    """
    return Card(action[0], action[1])


def encode_hand(plane, hand):
    """Encode hand and represerve it into plane

    Args:
        plane (array):
        A 2*4*13 numpy array to represent an
        arbitrary hand from a 52 card standard deck

        a 3-dimensional matrix plane[i][j][k]
        i: 0/1 card (two state)
        j: 4 suits
        k: 13 ranks

        example:
        if hand contains a H2: plane[1][1][1] = 1
                                     |  |  |
                                    x1  H  2  card

        hand (list): list of index of card ( 'H2'/ 'SA' )

    Returns:
        (array): 2*4*13 numpy array
    """
    # plane = np.zeros((2, 4, 13), dtype=int)
    plane[0] = np.ones((4, 13), dtype=int)
    hand = hand2dict(hand)
    for card, count in hand.items():
        si = SUIT_MAP[card[0]]
        ri = RANK_MAP[card[1]]
        plane[0][si][ri] = 0
        plane[count][si][ri] = 1

    return plane


def hand2dict(hand):
    """Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    """
    hand_dict = {}
    for card in hand:
        if card not in hand_dict:
            hand_dict[card] = 1
        else:
            hand_dict[card] += 1
    return hand_dict


def cards2list(cards):
    """Get the corresponding string representation of cards

    Args:
        cards (list): list of NinetyNine Cards objects

    Returns:
        (string): string representation of cards
    """
    cards_list = []
    for card in cards:
        cards_list.append(card.get_index())
    return cards_list
