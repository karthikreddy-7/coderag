import os
import sys

# Patterns/folders to ignore
IGNORE_DIRS = {
    "__pycache__",
    ".venv", "venv", "env",
    "node_modules",
    "build", "dist", "out",
    ".idea", ".vscode", ".git",
    ".mypy_cache", ".pytest_cache"
}

IGNORE_FILES = {
    ".DS_Store",
    ".env", ".env.local", ".gitignore",
    "Thumbs.db"
}

def print_dir_structure(root_path, indent=""):
    try:
        items = os.listdir(root_path)
    except PermissionError:
        print(f"{indent}[Permission Denied]")
        return

    items = sorted(
        [item for item in items if item not in IGNORE_FILES and item not in IGNORE_DIRS]
    )

    for i, item in enumerate(items):
        path = os.path.join(root_path, item)
        is_last = i == len(items) - 1
        branch = "└── " if is_last else "├── "
        print(f"{indent}{branch}{item}")
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_dir_structure(path, indent + extension)


if __name__ == "__main__":
    root_dir=("/home/karthik/dev/coderag/")
    print_dir_structure(root_dir)

