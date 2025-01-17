import os


# Get the context of files/folders present
def list_directory_contents(path="."):
    return os.listdir(path)


# Assuming run.py CLI logic is defined here
def run_cli_logic():
    # Placeholder for existing run.py CLI logic
    pass


if __name__ == "__main__":
    # Print the context
    print("Context of current directory:", list_directory_contents())
    # Execute CLI logic
    run_cli_logic()
