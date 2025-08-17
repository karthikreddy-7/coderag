import os
import gitlab
from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import urlparse

from app.config.settings import PRIVATE_TOKEN, IGNORED_FOLDERS, IGNORED_FILES, ALLOWED_EXTENSIONS


class ProjectDataProvider(ABC):
    """Abstract base class for providing file lists and content from a project source."""
    @abstractmethod
    def list_files(self) -> List[str]:
        """Return a list of all relevant file paths in the project."""
        pass
    @abstractmethod
    def get_file_content(self, file_path: str) -> str:
        """Return the content of a specific file."""
        pass


class GitLabDataProvider(ProjectDataProvider):
    """Provides data by fetching from a remote GitLab repository via API."""
    def __init__(self, repo_url: str, branch: Optional[str] = None, token: str = PRIVATE_TOKEN):
        self.repo_url = repo_url
        self.gl = gitlab.Gitlab("https://gitlab.com", private_token=token)
        project_path = self._get_project_path(repo_url)
        self.project = self.gl.projects.get(project_path)
        self.branch = branch or self.project.default_branch or "main"

    def _get_project_path(self, repo_url: str) -> str:
        """Convert GitLab URL to project path (namespace/project_name)."""
        return urlparse(repo_url).path.strip("/")

    def list_files(self) -> List[str]:
        files = []
        items = self.project.repository_tree(ref=self.branch, recursive=True, all=True)
        for item in items:
            path_parts = item["path"].split('/')
            file_name = path_parts[-1]

            # Apply blacklist and whitelist filters
            if item["type"] == "blob" \
               and not any(part in IGNORED_FOLDERS for part in path_parts) \
               and file_name not in IGNORED_FILES \
               and os.path.splitext(file_name)[1] in ALLOWED_EXTENSIONS:
                files.append(item["path"])
        return files

    def get_file_content(self, file_path: str) -> str:
        f = self.project.files.get(file_path=file_path, ref=self.branch)
        return f.decode().decode("utf-8")


class LocalDataProvider(ProjectDataProvider):
    """Provides data from a local filesystem path."""
    def __init__(self, project_path: str):
        if not os.path.isdir(project_path):
            raise ValueError(f"Path is not a valid directory: {project_path}")
        self.project_path = project_path

    def list_files(self) -> List[str]:
        all_files = []
        for root, dirs, files in os.walk(self.project_path, topdown=True):
            # Efficiently prune ignored directories from the walk
            dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

            for file in files:
                # Apply whitelist and blacklist filters
                if file not in IGNORED_FILES and os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    all_files.append(os.path.relpath(full_path, self.project_path))
        return all_files

    def get_file_content(self, file_path: str) -> str:
        full_path = os.path.join(self.project_path, file_path)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()


if __name__ == "__main__":
    repo_url = "https://gitlab.com/basupallykarthikreddy/demo-project"
    git_utils = GitLabDataProvider(repo_url=repo_url)
    all_files = git_utils.list_files()
    print(f"Found {len(all_files)} files in repo {repo_url}:")
    for f in all_files:
        print(f"{f} \n")