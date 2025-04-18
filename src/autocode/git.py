import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Union

from github import Github, GithubException

logger = logging.getLogger(__name__)


class Git:
    def __llm__(self):
        """Get the status of the git repository."""
        return self.status()

    @staticmethod
    def create_branch_and_checkout(name: str):
        """Create a new branch and checkout to it.
        If the name does not start with "autocode/", it will be added.
        """
        # if self.branch() != "master":
        # raise Exception("This function is only available in the master branch.")
        if not name.startswith("autocode/"):
            name = "autocode/" + name
        return subprocess.run(
            ["git", "checkout", "-b", name], capture_output=True, text=True
        ).stdout

    @staticmethod
    def branch():
        """Get the current branch of the git repository."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
        )
        return result.stdout.strip()

    @staticmethod
    def checkout(branch: str):
        """Checkout a branch of the git repository."""
        return subprocess.run(
            ["git", "checkout", branch], capture_output=True, text=True
        ).stdout

    @staticmethod
    def status():
        """Get the status of the git repository."""
        return subprocess.run(["git", "status"], capture_output=True, text=True).stdout

    @staticmethod
    def diff(path: Union[str, None] = None):
        """Get the diff of the git repository."""
        if path:
            return subprocess.run(
                ["git", "diff", path], capture_output=True, text=True
            ).stdout
        else:
            return subprocess.run(
                ["git", "diff"], capture_output=True, text=True
            ).stdout

    @staticmethod
    def stage(path: str = "."):
        """Stage the changes to the git repository."""
        return subprocess.run(
            ["git", "add", path], capture_output=True, text=True
        ).stdout

    @staticmethod
    def unstage(path: str = "."):
        """Unstage the changes to the git repository."""
        return subprocess.run(
            ["git", "reset", "--", path], capture_output=True, text=True
        ).stdout

    @staticmethod
    def commit(message):
        """Commit the changes to the git repository."""
        return subprocess.run(
            ["git", "commit", "-m", message], capture_output=True, text=True
        ).stdout

    @staticmethod
    def push():
        """Push the current branch to the remote repository."""
        return subprocess.run(["git", "push"], capture_output=True, text=True).stdout


class PullRequest:
    def __init__(self, git_instance: Optional[Git] = None):
        self.git = git_instance or Git()

    def submit(self):
        """Submit the current branch to the remote repository and create a GitHub pull request."""
        # First push the current branch
        push_result = subprocess.run(
            ["git", "push", "--set-upstream", "origin", Git.branch()],
            capture_output=True,
            text=True,
        )

        if push_result.returncode != 0:
            logger.error(f"Failed to push to remote: {push_result.stderr}")
            return push_result.stderr

        # Get the current branch name and repo information
        current_branch = Git.branch()

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

        # Try to get GitHub token from environment
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            # Look for token in standard locations
            token_paths = [
                Path.home() / ".github" / "token",
                Path.home() / ".config" / "gh" / "config.json",
            ]

            for path in token_paths:
                if path.exists():
                    if path.suffix == ".json":
                        try:
                            with open(path, "r") as f:
                                config = json.load(f)
                                # Extract token from GitHub CLI config
                                if (
                                    "hosts" in config
                                    and "github.com" in config["hosts"]
                                ):
                                    oauth_token = config["hosts"]["github.com"].get(
                                        "oauth_token"
                                    )
                                    if oauth_token:
                                        github_token = oauth_token
                                        break
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(
                                f"Error reading GitHub config file {path}: {e}"
                            )
                    else:
                        try:
                            github_token = path.read_text().strip()
                            break
                        except Exception as e:
                            logger.warning(f"Error reading token file {path}: {e}")

        if not github_token:
            return "Branch pushed but couldn't create PR: No GitHub token found. Set GITHUB_TOKEN environment variable."

        try:
            # Initialize PyGithub with token
            g = Github(github_token)
            github_repo = g.get_repo(f"{owner}/{repo}")

            # Create PR
            pr_title = f"PR: {current_branch}"
            pr_body = f"Pull request for branch {current_branch}"
            default_branch = github_repo.default_branch  # Usually "main" or "master"

            pr = github_repo.create_pull(
                title=pr_title, body=pr_body, base=default_branch, head=current_branch
            )

            return f"Pull request created successfully: {pr.html_url}"
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return f"Branch pushed but PR creation failed: {e}"
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return f"Branch pushed but PR creation failed: {e}"
