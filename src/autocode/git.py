import json
import logging
import os
import re
import subprocess
from typing import Optional, Union

logger = logging.getLogger(__name__)


class Git:
    def __llm__(self):
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
        """Get the current branch of the git repository."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
        )
        return result.stdout.strip()

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
    def __init__(self, git_instance: Optional[Git] = None):
        self.git = git_instance or Git()

    def submit(self):
        """Submit the current branch to the remote repository and create a GitHub pull request."""
        # First push the current branch
        push_result = subprocess.run(
            ["git", "push", "--set-upstream", "origin", self.git.git_branch()],
            capture_output=True,
            text=True,
        )

        if push_result.returncode != 0:
            logger.error(f"Failed to push to remote: {push_result.stderr}")
            return push_result.stderr

        # Get the current branch name and repo information
        current_branch = self.git.git_branch()

        # Get the remote URL to determine GitHub repo details
        remote_url_result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
        )

        if remote_url_result.returncode != 0:
            logger.error(f"Failed to get remote URL: {remote_url_result.stderr}")
            return f"Branch pushed but couldn't create PR: {remote_url_result.stderr}"

        remote_url = remote_url_result.stdout.strip()

        # Extract owner and repo from the URL
        # Format could be: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        match = re.search(r"github\.com[:/]([^/]+)/([^.]+)", remote_url)
        if not match:
            return f"Branch pushed but couldn't identify GitHub repo from URL: {remote_url}"

        owner, repo = match.groups()
        repo = repo.rstrip(".git")

        # Create pull request using GitHub CLI if available
        if self._is_gh_cli_available():
            pr_title = f"PR: {current_branch}"
            pr_body = f"Pull request for branch {current_branch}"

            pr_result = subprocess.run(
                ["gh", "pr", "create", "--title", pr_title, "--body", pr_body],
                capture_output=True,
                text=True,
            )

            if pr_result.returncode == 0:
                # Extract PR URL from the output
                match = re.search(r"(https://github\.com/[^\s]+)", pr_result.stdout)
                if match:
                    pr_url = match.group(1)
                    return f"Pull request created successfully: {pr_url}"
                return f"Pull request created successfully: {pr_result.stdout}"
            else:
                return f"Branch pushed but PR creation failed: {pr_result.stderr}"
        else:
            # Provide instructions if GitHub CLI is not available
            pr_url = f"https://github.com/{owner}/{repo}/pull/new/{current_branch}"
            return f"Branch pushed. Create PR manually at: {pr_url}"

    def _is_gh_cli_available(self):
        """Check if GitHub CLI is available in the system."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
