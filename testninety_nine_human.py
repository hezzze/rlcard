""" A toy example of playing against DQN bot on NinetyNine
"""

import rlcard
import torch
from rlcard.agents import NinetyNineHumanAgent as HumanAgent


# Make environment
env = rlcard.make("ninety-nine")
human_agent = HumanAgent(env.num_actions)
dqn_agent = torch.load("experiments/leduc_holdem_dqn_result/model.pth")
env.set_agents([human_agent, dqn_agent, dqn_agent, dqn_agent])

print(">> NinetyNine DQN V1")

while True:
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    final_state = trajectories[0][-1]
    action_record = final_state["action_record"]
    state = final_state["raw_obs"]
    _action_list = []
    for i in range(1, len(action_record) + 1):
        if action_record[-i][0] == state["current_player"]:
            break
        _action_list.insert(0, action_record[-i])
    for pair in _action_list:
        print(">> Player", pair[0], "chooses ", end="")
        print(pair[1])
        print("")

    print("===============     Result     ===============")
    if payoffs[0] > 0:
        print("You win!")
    else:
        print("You lose!")
    print("")
    input("Press any key to continue...")
