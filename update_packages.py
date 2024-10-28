# ruff: noqa

import os
import re
import subprocess

import toml


def run_command(command):
    """Run a command and return the output."""
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error: {error.decode('utf-8')}")
        return None
    return output.decode("utf-8")


class CustomTOMLEncoder(toml.TomlEncoder):
    """Custom TOML encoder for the pyproject.toml file."""

    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict, preserve)
        self.dump_funcs[list] = self._dump_list

    def _dump_list(self, v):
        return "[{}]".format(",\n  ".join(self.dump_value(u) for u in v))


def update_packages():
    """Update the packages in the pyproject.toml file."""
    # Read the current pyproject.toml before updates
    with open("pyproject.toml", "r") as f:
        original_pyproject = toml.load(f)

    # Extract package names from pyproject.toml
    dependencies = original_pyproject["project"]["dependencies"]
    package_names = [re.split("[=<>]", dep)[0].strip() for dep in dependencies]

    # Run the uv pip install command with explicit package names
    command = f"uv pip install --upgrade {' '.join(package_names)}"
    result = run_command(command)
    if result is None:
        return

    print("Package update process completed.")

    # Create requirements file
    run_command("uv pip freeze > requirements.txt")
    print("requirements.txt created.")

    # Read the current pyproject.toml again
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    # Read the updated requirements
    with open("requirements.txt", "r") as f:
        updated_requirements = f.readlines()

    # Update the dependencies in pyproject.toml
    dependencies = pyproject["project"]["dependencies"]
    original_dependencies = original_pyproject["project"]["dependencies"]
    updates_made = False
    updated_packages = []

    for i, dep in enumerate(dependencies):
        name = re.split("[=<>]", dep)[0].strip()
        original_version = re.split("[=<>]", original_dependencies[i])[-1].strip()
        for req in updated_requirements:
            req_parts = req.strip().split("==")
            if len(req_parts) == 2:
                req_name, req_version = req_parts
            else:
                req_name = req_parts[0]
                req_version = None

            if req_name.lower() == name.lower():
                if req_version and req_version != original_version:
                    # Keep any existing version specifiers (e.g., >=)
                    specifier = re.search(r"([<>=]+)", dep)
                    if specifier:
                        new_dep = f"{name}{specifier.group(1)}{req_version}"
                    else:
                        new_dep = f"{name}>={req_version}"

                    if new_dep != original_dependencies[i]:
                        dependencies[i] = new_dep
                        updates_made = True
                        updated_packages.append((name, original_version, req_version))
                break

    if not updates_made:
        print(
            "No updates were necessary. All packages are already at their latest versions."
        )
        os.remove("requirements.txt")
        return

    # Print the list of updated packages
    print("\nUpdated packages:")
    for name, old_version, new_version in updated_packages:
        print(f"{name} @{old_version} to @{new_version}")

    # Write the updated pyproject.toml
    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f, encoder=CustomTOMLEncoder())
        # Add an extra newline at the end of the file
        f.write("\n")

    print("pyproject.toml has been updated with the latest package versions.")

    # Delete the requirements.txt file
    os.remove("requirements.txt")
    print("requirements.txt has been deleted.")

    # Run uv lock --upgrade
    print("Running uv lock --upgrade...")
    lock_result = run_command("uv lock --upgrade")
    if lock_result is not None:
        print("uv lock completed successfully.")
    else:
        print("Error occurred while running uv lock.")

    # Run uv sync
    print("Running uv sync...")
    sync_result = run_command("uv sync")
    if sync_result is not None:
        print("uv sync completed successfully.")
    else:
        print("Error occurred while running uv sync.")


if __name__ == "__main__":
    update_packages()
