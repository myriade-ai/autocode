"""
Dual agent module that implements a Manager and Developer agent system.

The Manager agent is responsible for the overall vision, task decomposition,
and reviewing the Developer agent's work. The Developer agent focuses on
implementing the specific tasks assigned by the Manager.
"""

import logging
import signal
import sys
import tempfile
from typing import List, Optional

from autochat import Autochat
from autochat.model import Message

from autocode.code_editor import CodeEditor
from autocode.git import Git, PullRequest
from autocode.render import render_url_and_return_screenshot
from autocode.terminal import Terminal

logger = logging.getLogger(__name__)

# Manager agent instructions
MANAGER_INSTRUCTIONS = """
### Role & Purpose
You are a Senior Engineering Manager agent overseeing a software development project.
Your responsibilities include:
1. Understanding user requirements and breaking them down into actionable tasks
2. Providing clear instructions to the Developer agent
3. Reviewing code produced by the Developer agent
4. Providing feedback and requesting modifications when necessary
5. Maintaining the overall vision and quality of the project

### Guidelines for Task Assignment
- Be specific about what needs to be implemented
- Provide context and explain the purpose of the task
- Set clear expectations and acceptance criteria
- Suggest implementation approaches if helpful
- Avoid being too prescriptive - allow the Developer some freedom

### Guidelines for Code Review
- Check for logical correctness and adherence to requirements
- Verify error handling and edge cases
- Review code style and organization
- Consider performance implications
- Provide actionable feedback with specific examples
- Praise good work and be constructive with criticism

### Communication
- Be clear and concise in your communication
- Use technical language appropriate for a senior developer
- When necessary, explain the rationale behind decisions
- Be patient and supportive while maintaining high standards

You do not have direct access to development tools - the Developer agent will implement the actual code.
"""

# Developer agent instructions
DEVELOPER_INSTRUCTIONS = """
### Role & Purpose
You are a developer agent equipped with developer tools and functions to complete tasks.
Focus on developing or modifying code using these tools rather than directly answering the manager.

### Workflow
0. Find a good name for the branch and create it.
1. Think about the task given by the manager
2. Explore the possibilities
3. Make a plan
4. Run the project (back server, front server, test suite, ...). Use .terminal.json to setup the shells if it exists.
5. Develop (monitor if any of the project parts are not working)
6. Test your work
7. Ensure there is the minimum of changes (no more, no less)
8. Git commit
9. Tell the manager when you're done

### Tools
Some notes on tool usage.

#### Terminal / Shell Sessions
Use shell sessions to:
- Install dependencies
- Run commands, servers
- Run tests
- ...
Don't use the shell to edit files.
Don't use the shell to use git.

#### Code Editor
Use the code editor functions list_directory, search_files, read_file to get information about the project
Use the code editor functions (edit_file, write_file, delete_file, ...) to create or edit files as needed.
Never edit files outside of the code editor functions.

#### Git
Use git functions to review diffs & commit.
Make sure there is only the strict necessary changes for the task.

### Dependencies & Installation
If you need to install anything, request confirmation from the manager first.
Do not install anything unless explicitly asked or confirmed.

### Implementation
When implementing the manager's requests:
1. Make sure you fully understand the requirements before starting
2. Ask questions if anything is unclear
3. Provide updates on your progress
4. Explain your approach and reasoning
5. Be receptive to feedback and make requested changes promptly

### General Reminders
Your primary objective is to utilize tools/functions to implement the manager's requests.
Always verify that your actions and outputs align with manager instructions and requirements.
"""


class DualAgentSystem:
    """
    Implements a dual-agent system with a Manager agent and a Developer agent.

    The Manager agent oversees the development process and provides instructions
    to the Developer agent, which implements the actual code changes.
    """

    def __init__(self, provider="anthropic", model="claude-3-7-sonnet-latest"):
        """
        Initialize the dual-agent system with a Manager and Developer agent.

        Args:
            provider (str): The provider to use for the agents (default: "anthropic")
            model (str): The model to use for the agents (default: "claude-3-7-sonnet-latest")
        """
        # Initialize the Manager agent
        self.manager_agent = Autochat(
            MANAGER_INSTRUCTIONS, provider=provider, model=model
        )

        # Initialize the Developer agent with tools
        self.dev_agent = Autochat(
            DEVELOPER_INSTRUCTIONS, provider=provider, model=model
        )

        # Add tools to the Developer agent
        terminal = Terminal()
        self.dev_agent.add_tool(terminal)

        code_editor = CodeEditor()
        self.dev_agent.add_tool(code_editor)

        self.dev_agent.add_function(render_url_and_return_screenshot)

        git = Git()
        self.dev_agent.add_tool(git, "Git")

        pull_request = PullRequest()
        self.dev_agent.add_tool(pull_request)

        # Keep track of the conversation thread
        self.manager_user_history = []
        self.manager_dev_history = []

    def run(self, initial_prompt: Optional[str] = None):
        """
        Run the dual-agent system interactive session.

        Args:
            initial_prompt (str, optional): The initial prompt to start the conversation.
        """

        # Set up a signal handler for SIGINT (Ctrl+C)
        def signal_handler(sig, frame):
            print("\nExiting dual-agent system...")
            # Checkout to master before exiting
            try:
                Git.checkout("master")
            except Exception:
                pass
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        prompt = initial_prompt

        try:
            while True:
                # Get input from the user if no initial prompt is provided
                if not prompt:
                    prompt = input(
                        "\n🧑‍💻 Enter your request (Ctrl+C to exit, 'exit' or 'quit' to close): "
                    )

                if not prompt.strip():
                    print("Please provide a request")
                    prompt = None
                    continue

                if prompt.lower() in ["exit", "quit"]:
                    print("Exiting dual-agent system...")
                    break

                # Store user message in manager history
                self.manager_user_history.append(Message(role="user", content=prompt))

                print("\n👨‍💼 Manager is thinking...\n")

                # Send the prompt to the Manager agent
                manager_response = self._get_manager_response_to_user(prompt)
                print(f"👨‍💼 Manager: {manager_response}\n")

                # Manager instructs the Developer
                dev_instructions = self._get_manager_instructions_to_dev(
                    manager_response
                )
                print(f"👨‍💼 Manager → 👩‍💻 Developer: {dev_instructions}\n")

                print("👩‍💻 Developer is implementing...\n")

                # Developer works on the task
                dev_updates = self._run_developer_agent(dev_instructions)

                # Developer reports back to Manager
                print(f"\n👩‍💻 Developer → 👨‍💼 Manager: {dev_updates}\n")

                # Manager reviews the work
                manager_review = self._get_manager_review(dev_updates)
                print(f"👨‍💼 Manager review: {manager_review}\n")

                # Reset prompt for next iteration
                prompt = None

                # Checkout to master after the task is complete
                self.dev_agent.messages.append(
                    Message(role="user", content="Checkout to master")
                )
                Git.checkout("master")

        except KeyboardInterrupt:
            print("\nExiting dual-agent system...")
            # Checkout to master before exiting
            try:
                Git.checkout("master")
            except Exception:
                pass
            sys.exit(0)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            # Checkout to master before exiting
            try:
                Git.checkout("master")
            except Exception:
                pass
            raise e

    def _get_manager_response_to_user(self, prompt: str) -> str:
        """
        Get the Manager agent's response to the user's prompt.

        Args:
            prompt (str): The user's prompt

        Returns:
            str: The Manager agent's response
        """
        # Run the conversation with the Manager agent
        messages = [Message(role="user", content=prompt)]

        # Add history of previous user-manager interactions if any
        if self.manager_user_history:
            messages = self.manager_user_history

        response = ""
        for message in self.manager_agent.run_conversation(messages=messages):
            if message.role == "assistant":
                response = message.content

        # Update manager user history
        self.manager_user_history.append(Message(role="assistant", content=response))

        return response

    def _get_manager_instructions_to_dev(self, manager_response: str) -> str:
        """
        Get the Manager agent's instructions to the Developer agent.

        Args:
            manager_response (str): The Manager agent's response to the user

        Returns:
            str: The Manager agent's instructions to the Developer agent
        """
        # Ask the Manager agent to provide clear instructions to the Developer
        instruction_prompt = (
            "Based on the user request and your response, provide clear and specific "
            "instructions for the Developer agent to implement. Focus on what needs to be done, "
            "acceptance criteria, and any relevant context."
        )

        messages = [
            *self.manager_user_history,
            Message(role="user", content=instruction_prompt),
        ]

        instructions = ""
        for message in self.manager_agent.run_conversation(messages=messages):
            if message.role == "assistant":
                instructions = message.content

        # Update manager-dev history
        self.manager_dev_history.append(
            Message(role="user", content="TASK: " + instructions)
        )

        return instructions

    def _run_developer_agent(self, instructions: str) -> str:
        """
        Run the Developer agent with the Manager's instructions.

        Args:
            instructions (str): The Manager agent's instructions

        Returns:
            str: The Developer agent's update on the implementation
        """
        # Send the instructions to the Developer agent
        updates = ""
        for message in self.dev_agent.run_conversation(instructions):
            text = message.to_terminal(display_image=True)
            if "number|line content" in text:
                # Save content in a temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(text.encode("utf-8"))
                    temp_file_path = temp_file.name
                print(
                    f"👩‍💻 Developer: Hiding file content (copied to {temp_file_path})\n"
                )
            else:
                print(f"👩‍💻 Developer: {text}")
                updates += text + "\n"

        # Update manager-dev history
        self.manager_dev_history.append(Message(role="assistant", content=updates))

        return updates

    def _get_manager_review(self, dev_updates: str) -> str:
        """
        Get the Manager agent's review of the Developer agent's work.

        Args:
            dev_updates (str): The Developer agent's updates

        Returns:
            str: The Manager agent's review
        """
        # Ask the Manager agent to review the Developer's work
        review_prompt = (
            "Review the Developer's implementation and provide feedback. "
            "Assess if the implementation meets the requirements, identify any issues, "
            "and suggest improvements if necessary."
        )

        messages = [
            *self.manager_dev_history,
            Message(role="user", content=review_prompt),
        ]

        review = ""
        for message in self.manager_agent.run_conversation(messages=messages):
            if message.role == "assistant":
                review = message.content

        return review


def main():
    """
    Entry point for the dual-agent system.
    """
    print("Starting the Dual-Agent (Manager-Developer) system...")
    print("-----------------------------------------------------")
    print("👨‍💼 Manager: Oversees development and provides instructions")
    print("👩‍💻 Developer: Implements code based on Manager's instructions")
    print("-----------------------------------------------------")

    initial_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    dual_agent_system = DualAgentSystem()
    dual_agent_system.run(initial_prompt)


if __name__ == "__main__":
    main()
