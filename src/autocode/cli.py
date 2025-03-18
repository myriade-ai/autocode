import logging
import signal
import sys

from autocode.__main__ import agent

logger = logging.getLogger(__name__)


def main():
    # Set up a signal handler for SIGINT (Ctrl+C)
    def signal_handler(sig, frame):
        print("\nExiting conversation...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    initial_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    while True:
        try:
            if initial_prompt:
                prompt = initial_prompt
                initial_prompt = None
            else:
                prompt = input(
                    "Enter your prompt (Ctrl+C to exit, 'exit' or 'quit' to close): "
                )

            if not prompt.strip():
                print("Please provide a prompt")
                continue

            if prompt.lower() in ["exit", "quit"]:
                print("Exiting conversation...")
                break

            try:
                for message in agent.run_conversation(prompt):
                    print(message.to_terminal(display_image=True))
            except KeyboardInterrupt:
                print("\nStopped the AI loop...")
                # Give the user a chance to decide what to do next
                print("Press Ctrl+C again to exit completely or enter a new prompt.")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise e


if __name__ == "__main__":
    main()
