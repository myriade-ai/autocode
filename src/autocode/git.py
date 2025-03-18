import logging
import subprocess
from typing import Union

logger = logging.getLogger(__name__)


class Git:
    def __repr__(self):
        """Get the status of the git repository."""
        return self.git_status()

    def git_status(self):
        """Get the status of the git repository."""
        return subprocess.run(["git", "status"], capture_output=True, text=True).stdout

    def git_diff(self, path: Union[str, None] = None):
        """Get the diff of the git repository."""
        if path:
            return subprocess.run(
                ["git", "diff", path], capture_output=True, text=True
            ).stdout
        else:
            return subprocess.run(
                ["git", "diff"], capture_output=True, text=True
            ).stdout

    def git_stage(self, path: str = "."):
        """Stage the changes to the git repository."""
        return subprocess.run(
            ["git", "add", path], capture_output=True, text=True
        ).stdout

    def git_unstage(self, path: str = "."):
        """Unstage the changes to the git repository."""
        return subprocess.run(
            ["git", "reset", "--", path], capture_output=True, text=True
        ).stdout

    def git_commit(self, message):
        """Commit the changes to the git repository."""
        return subprocess.run(
            ["git", "commit", "-m", message], capture_output=True, text=True
        ).stdout

    def git_push(self):
        """Push the current branch to the remote repository."""
        return subprocess.run(["git", "push"], capture_output=True, text=True).stdout


class PullRequest:
    def submit(self):
        """
        When the code is ready to be submitted, this function will:
        1. Show the changes to be submitted
        2. Ask the user for a review
        """
        # If tests pass, show changes and ask for review
        diff = subprocess.run(["git", "diff"], capture_output=True, text=True).stdout
        print("Changes to be submitted:")
        print(diff)

        user_input = input("Do you want to submit these changes? (y/n): ").lower()
        if user_input == "y":
            print("Changes have been pushed to branch: {branch_name}")
        else:
            print("Submission cancelled.")
