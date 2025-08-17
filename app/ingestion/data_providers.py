import os
import gitlab
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import urlparse

from app.config.logging_config import setup_logging
from app.config.settings import PRIVATE_TOKEN, IGNORED_FOLDERS, IGNORED_FILES, ALLOWED_EXTENSIONS

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

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
        logger.debug(f"Initializing GitLabDataProvider for repo: {repo_url}")
        self.gl = gitlab.Gitlab("https://gitlab.com", private_token=token)
        project_path = self._get_project_path(repo_url)
        logger.debug(f"Converted repo URL to project path: {project_path}")
        self.project = self.gl.projects.get(project_path)
        self.branch = branch or self.project.default_branch or "main"
        logger.info(f"Using branch: {self.branch}")

    def _get_project_path(self, repo_url: str) -> str:
        """Convert GitLab URL to project path (namespace/project_name)."""
        return urlparse(repo_url).path.strip("/")

    def list_files(self) -> List[str]:
        files = []
        items = self.project.repository_tree(ref=self.branch, recursive=True, all=True)
        logger.debug(f"Fetched {len(items)} items from GitLab repository tree")
        for item in items:
            path_parts = item["path"].split('/')
            file_name = path_parts[-1]

            if item["type"] == "blob":
                if any(part in IGNORED_FOLDERS for part in path_parts):
                    logger.debug(f"Ignored folder in path: {item['path']}")
                    continue
                if file_name in IGNORED_FILES:
                    logger.debug(f"Ignored file: {file_name}")
                    continue
                if os.path.splitext(file_name)[1] not in ALLOWED_EXTENSIONS:
                    logger.debug(f"Skipped file due to extension filter: {file_name}")
                    continue
                files.append(item["path"])
                logger.debug(f"Added file: {item['path']}")
        logger.info(f"Total files after filtering: {len(files)}")
        return files

    def get_file_content(self, file_path: str) -> str:
        logger.debug(f"Fetching content for file: {file_path}")
        f = self.project.files.get(file_path=file_path, ref=self.branch)
        content = f.decode().decode("utf-8")
        logger.debug(f"Fetched {len(content)} characters for file: {file_path}")
        return content


class LocalDataProvider(ProjectDataProvider):
    """Provides data from a local filesystem path."""
    def __init__(self, project_path: str):
        if not os.path.isdir(project_path):
            raise ValueError(f"Path is not a valid directory: {project_path}")
        self.project_path = project_path
        logger.debug(f"Initialized LocalDataProvider for path: {project_path}")

    def list_files(self) -> List[str]:
        all_files = []
        for root, dirs, files in os.walk(self.project_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

            for file in files:
                if file not in IGNORED_FILES and os.path.splitext(file)[1] in ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_path)
                    all_files.append(rel_path)
                    logger.debug(f"Added file: {rel_path}")
                else:
                    logger.debug(f"Ignored file: {file}")
        logger.info(f"Total local files after filtering: {len(all_files)}")
        return all_files

    def get_file_content(self, file_path: str) -> str:
        full_path = os.path.join(self.project_path, file_path)
        logger.debug(f"Reading local file: {full_path}")
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        logger.debug(f"Read {len(content)} characters from file: {file_path}")
        return content


if __name__ == "__main__":
    repo_url = "https://gitlab.com/basupallykarthikreddy/demo-project"
    git_utils = GitLabDataProvider(repo_url=repo_url)
    all_files = git_utils.list_files()
    print(f"Found {len(all_files)} files in repo {repo_url}:")
    for f in all_files:
        print(f"{f} \n")