import logging
import subprocess
from typing import Union

logger = logging.getLogger(__name__)


class Git:
    def __repr__(self):
        """Get the status of the git repository."""
        return self.git_status()

    # add condition so the function is deactivated if the user is not in "master" branch
    def git_create_branch_and_checkout(self, name: str):
        """Create a new branch and checkout to it.
        If the name does not start with "autocode/", it will be added.
        """
        if self.git_branch() != "master":
            raise Exception("This function is only available in the master branch.")
        if not name.startswith("autocode/"):
            name = "autocode/" + name
        return subprocess.run(
            ["git", "checkout", "-b", name], capture_output=True, text=True
        ).stdout

    def git_branch(self):
        """Get the current branch."""
        return subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        ).stdout.strip()

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
        """Submit the current branch to the remote repository."""
        return subprocess.run(["git", "push"], capture_output=True, text=True).stdou
