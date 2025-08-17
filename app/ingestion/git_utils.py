# app/ingestion/git_utils.py
"""
Git Utils using python-gitlab:
- Fetch all files from a GitLab repo URL
- Get file content
"""

import gitlab
from typing import List, Optional
from urllib.parse import urlparse

from app.config.settings import PRIVATE_TOKEN


class GitUtils:
    def __init__(self, token: str = PRIVATE_TOKEN):
        self.gl = gitlab.Gitlab("https://gitlab.com", private_token=token)

    def _get_project_path(self, repo_url: str) -> str:
        """
        Convert GitLab URL to project path (namespace/project_name)
        Supports groups/subgroups automatically.
        """
        parsed = urlparse(repo_url)
        return parsed.path.strip("/")

    def _get_project(self, repo_url: str):
        project_path = self._get_project_path(repo_url)
        return self.gl.projects.get(project_path)

    def _get_default_branch(self, project) -> str:
        return project.default_branch or "main"

    def list_files(self, repo_url: str, branch: Optional[str] = None) -> List[str]:
        project = self._get_project(repo_url)
        branch = branch or self._get_default_branch(project)
        files = []
        stack = [""]  # start from root folder
        while stack:
            path = stack.pop()
            items = project.repository_tree(path=path, ref=branch)
            for item in items:
                if item["type"] == "tree":
                    stack.append(item["path"])
                else:
                    files.append(item["path"])
        return files

    def get_file_content(self, repo_url: str, file_path: str, branch: Optional[str] = None) -> str:
        project = self._get_project(repo_url)
        branch = branch or self._get_default_branch(project)
        f = project.files.get(file_path=file_path, ref=branch)
        return f.decode().decode("utf-8")


# Smoke test
if __name__ == "__main__":
    repo_url = "https://gitlab.com/basupallykarthikreddy/demo-project"
    git_utils = GitUtils()
    all_files = git_utils.list_files(repo_url)
    print(f"Found {len(all_files)} files in repo {repo_url}:")
    for f in all_files[:5]:
        content = git_utils.get_file_content(repo_url, f)
        print(f"{f} -> {content[:100]}...\n")
