from autochat import Autochat

from .code_editor import CodeEditor
from .terminal import Terminal


class InsightfulAutochat(Autochat):
    """Extension of Autochat that can store and retrieve insights."""

    def __init__(self, instructions, *args, **kwargs):
        super().__init__(instructions, *args, **kwargs)
        self.insights_file = "insights.txt"
        self.insights = self._load_insights()
        self._update_instructions()
        self.add_function(self.store_insight)

    def _load_insights(self):
        """Load insights from the file"""
        try:
            with open(self.insights_file, "r") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []

    def _update_instructions(self):
        """Update the instructions with the loaded insights"""
        insights_text = "\n".join(self.insights)
        self.instruction += f"\n\nInsights and Feedback:\n{insights_text}"

    def store_insight(self, insight: str):
        """Store an insight for future guide to the agent.
        It should be general and not specific to a task.
        A good insight is something like "Don't commit all files unless explicitly asked".
        When the user is angry or frustrated, it's a good idea to store an insight.
        Don't store insights that are already in the file.
        """
        with open(self.insights_file, "a") as f:
            f.write(insight + "\n")
        self.insights.append(insight)
        self._update_instructions()
        print(f"Insight stored and instructions updated: {insight}")

    def get_insights(self):
        """Retrieve all stored insights"""
        return self.insights


# Initialize the agent with basic instructions
initial_instructions = """You are an agent, which leverage tools to help you complete tasks.
When you generate shells, you will have the ability to run commands in them.
Don't answer user query, but use tools to complete the task.
Your goal is to develop code (with shells & code editor).
Create or edit files as needed.
Before finishing, try to always verify the code is working as expected.
If you need to install something, ask the user for confirmation first.
If you really can't figure out how to do something, ask the user for help
Don't commit anything unless explicitly asked.
"""

# agent = InsightfulAutochat(initial_instructions, provider="openai", model="o1")
agent = InsightfulAutochat(initial_instructions, provider="anthropic")
terminal = Terminal()
agent.add_tool(terminal)
code_editor = CodeEditor()
agent.add_tool(code_editor)
# agent.add_tool(File)


if __name__ == "__main__":
    import sys

    while True:
        try:
            if len(sys.argv) > 1:
                prompt = " ".join(sys.argv[1:])
            else:
                prompt = input("Enter your prompt (Ctrl+C to exit): ")

            if not prompt.strip():
                print("Please provide a prompt")
                continue

            for message in agent.run_conversation(prompt):
                print(message.to_markdown())

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
