import sys

from autocode.__main__ import agent


def main():
    while True:
        try:
            if len(sys.argv) > 1:
                prompt = " ".join(sys.argv[1:])
            else:
                prompt = input("Enter your prompt (Ctrl+C to exit): ")

            if not prompt.strip():
                print("Please provide a prompt")
                continue

            try:
                for message in agent.run_conversation(prompt):
                    print(message.to_markdown())
            except KeyboardInterrupt:
                print("\nStopped the AI loop...")
                break

        except KeyboardInterrupt:
            print("\nExiting conversation...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e


if __name__ == "__main__":
    main()
