"""
Dual agent module that implements a Manager and Developer agent system.

The Manager agent is responsible for the overall vision, task decomposition,
and reviewing the Developer agent's work. The Developer agent focuses on
implementing the specific tasks assigned by the Manager.
"""

import logging

import nest_asyncio
from autochat import Message

from autocode.agent_dev import agent as dev_agent
from autocode.agent_manager import agent as manager_agent

nest_asyncio.apply()
logger = logging.getLogger(__name__)


def get_human_input():
    # Get input from the user if no initial prompt is provided
    prompt = ""
    while True:
        if not prompt.strip():
            prompt = input(
                "\n🧑‍💻 Enter your request (Ctrl+C to exit, 'exit' or 'quit' to close):\n"
            )
        elif prompt.lower() in ["exit", "quit"]:
            print("Exiting dual-agent system...")
            raise SystemExit
        else:
            return prompt


class CollaborationTool:
    # TODO: Improve communication tool to allow agents to communicate with each other
    # 1. Discover other agents
    # 2. Send messages to other agents
    # 3. Receive messages from other agents

    def __llm__(self):
        """Display list of other agents"""
        return "Agents: \n" + "\n".join([agent.name for agent in self.agents])

    def __init__(self, agents: list):
        self.agents = agents

    def send_message(self, agent_name: str, message: str):
        """Send a message to another agent"""
        agent = next((a for a in self.agents if a.name == agent_name), None)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        for message in agent.run_conversation(message):
            print(message.to_terminal())


class Game:
    agents = []

    def _add_communication_tool(self):
        """
        Add a communication tool to the agents
        """
        collaboration_tool = CollaborationTool(self.agents)
        for agent in self.agents:
            agent.add_tool(collaboration_tool)

    def run(self):
        """
        Run the each agent in the game until they have finished their task
        or if they call another agent, run the other agent until it has finished its task
        etc.
        """
        self._add_communication_tool()
        first_agent = self.agents[0]
        while True:
            prompt = get_human_input()
            for message in first_agent.run_conversation(prompt):
                print(message.to_terminal())


game = Game()
game.agents.append(manager_agent)


def simple_response_callback(message):
    return Message(role="user", content="Send a message to the manager")


dev_agent.simple_response_callback = simple_response_callback
game.agents.append(dev_agent)  # TODO: developper should only talk to manager
game.run()

# TODO: add Human Agent ?


# def run(initial_prompt: Optional[str] = None):
#     prompt = initial_prompt

#     while True:
#         # Get input from the user if no initial prompt is provided
#         if not prompt:
#             prompt = input(
#                 "\n🧑‍💻 Enter your request (Ctrl+C to exit, 'exit' or 'quit' to close): "
#             )

#         if not prompt.strip():
#             print("Please provide a request")
#             prompt = None
#             continue

#         if prompt.lower() in ["exit", "quit"]:
#             print("Exiting dual-agent system...")
#             break

#         for message in manager_agent.run_conversation(prompt):
#             print(message.to_terminal())


# def main():
#     """
#     Entry point for the dual-agent system.
#     """
#     print("Starting the Dual-Agent (Manager-Developer) system...")
#     print("-----------------------------------------------------")
#     print("👨‍💼 Manager: Oversees development and provides instructions")
#     print("👩‍💻 Developer: Implements code based on Manager's instructions")
#     print("-----------------------------------------------------")

#     initial_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
#     run(initial_prompt)


# if __name__ == "__main__":
#     main()
#     main()
