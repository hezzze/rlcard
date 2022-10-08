import pprint
import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils.utils import reorganize

env = rlcard.make("ninety-nine")
agent = RandomAgent(num_actions=env.num_actions)
env.set_agents([agent for _ in range(env.num_players)])
trajectories, payoffs = env.run()
# trajectories = reorganize(trajectories, payoffs)

# Print out the trajectories
print("\nTrajectories:")
pprint.pprint(trajectories)
print("\nSample raw observation:")
pprint.pprint(trajectories[0][0]["raw_obs"])
print("\nSample raw legal_actions:")
pprint.pprint(trajectories[0][0]["raw_legal_actions"])
print("\nPayoffs:")
print(payoffs)
