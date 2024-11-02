# ruff: noqa
import argparse
import os
import re
from typing import List, Tuple


def find_python_files(root_dir: str) -> List[str]:
    """Recursively find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def update_hub_references(
    file_path: str, environment: str, dry_run: bool
) -> Tuple[bool, List[str]]:
    """Update hub references in a file for the specified environment.

    In production: adds ':production' suffix
    In development: removes any environment suffix
    """
    with open(file_path, "r") as f:
        content = f.read()

    pattern = r'hub\.pull\([\'"]([^\'"]+?)(?::(?:production|development))?[\'"]\)'

    changes = []
    modified = False

    def replace_match(match):
        nonlocal modified
        prompt_name = match.group(1).split(":")[
            0
        ]  # Remove any existing environment suffix
        original = match.group(0)

        # For development, use prompt name without suffix
        if environment == "development":
            new_ref = f'hub.pull("{prompt_name}")'
        else:
            new_ref = f'hub.pull("{prompt_name}:{environment}")'

        if original != new_ref:
            modified = True
            changes.append(f"  {original} -> {new_ref}")
            return new_ref
        return original

    new_content = re.sub(pattern, replace_match, content)

    if modified and not dry_run:
        with open(file_path, "w") as f:
            f.write(new_content)

    return modified, changes


def main():
    parser = argparse.ArgumentParser(
        description="Update LangChain Hub references based on environment"
    )
    parser.add_argument(
        "--env",
        choices=["production", "development"],
        required=True,
        help="Environment to set (production or development)",
    )
    parser.add_argument(
        "--src", default="src", help="Source directory to scan (default: src)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without applying them"
    )

    args = parser.parse_args()
    python_files = find_python_files(args.src)
    changes_made = False

    for file_path in python_files:
        modified, changes = update_hub_references(file_path, args.env, args.dry_run)

        if modified:
            changes_made = True
            print(f"\nModified {file_path}:")
            for change in changes:
                print(change)

            if args.dry_run:
                print("(Dry run - no changes were actually made)")

    if not changes_made:
        print("\nNo changes were necessary.")


if __name__ == "__main__":
    main()
