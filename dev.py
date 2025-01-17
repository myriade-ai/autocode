from run import Shell, Terminal, File, agent, terminal

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        for message in agent.run_conversation(prompt):
            print(message.to_markdown())
    else:
        print("Please provide a prompt as command line argument")
