import os
import subprocess
from tree_sitter import Language, Parser

# -----------------------------
# Configuration
# -----------------------------
LANGUAGES = ["java"]
BUILD_DIR = "build"
LIB_NAME = os.path.join(BUILD_DIR, "my-languages.so")
REPO_BASE_DIR = "."  # where tree-sitter repos will be cloned

# Ensure build directory exists
os.makedirs(BUILD_DIR, exist_ok=True)

# -----------------------------
# Clone language repos if missing
# -----------------------------
for lang in LANGUAGES:
    repo_dir = os.path.join(REPO_BASE_DIR, f"tree-sitter-{lang}")
    repo_url = f"https://github.com/tree-sitter/tree-sitter-{lang}.git"
    if not os.path.exists(repo_dir):
        print(f"\n>> Cloning {repo_url} ...")
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    else:
        print(f"\n>> Repo {repo_dir} already exists, skipping clone.")

# -----------------------------
# Build the .so library
# -----------------------------
print(f"\n>> Building parser library at {LIB_NAME} ...")
Language.build_library(
    # Output path
    LIB_NAME,
    # Source paths
    [os.path.join(REPO_BASE_DIR, f"tree-sitter-{lang}") for lang in LANGUAGES]
)
print(">> Build completed!\n")

# -----------------------------
# Load Java language
# -----------------------------
LANG_OBJ = Language(LIB_NAME, "java")
parser = Parser()
parser.set_language(LANG_OBJ)

# -----------------------------
# Test parsing a demo Java code
# -----------------------------
demo_code = b"""
public class Test {
    public void hello() {
        System.out.println("Hello, Tree-sitter!");
    }
}
"""
tree = parser.parse(demo_code)

print(">> Parser loaded successfully!")
print(f"-> Root node type: {tree.root_node.type}")
print(f"-> S-expression:\n{tree.root_node.sexp()}")
