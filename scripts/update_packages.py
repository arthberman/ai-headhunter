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
    dev_dependencies = original_pyproject["tool"]["uv"]["dev-dependencies"]

    def clean_package_name(dep):
        """Extract base package name, handling extras."""
        # First split by any version specifiers
        base = re.split("[=<>]", dep)[0].strip()
        # Then remove any extras in square brackets
        return re.split(r"\[", base)[0].strip()

    def get_package_with_extras(dep):
        """Get package name with extras but without version."""
        # Split by version specifiers
        base = re.split("[=<>]", dep)[0].strip()
        return base

    # Get package names with extras but without versions
    package_specs = [get_package_with_extras(dep) for dep in dependencies]
    dev_package_specs = [get_package_with_extras(dep) for dep in dev_dependencies]

    # Run the uv pip install command with package names (and extras if present)
    command = f"uv pip install --upgrade {' '.join(package_specs)}"
    result = run_command(command)
    if result is None:
        return

    # Run the uv pip install command for dev dependencies
    dev_command = f"uv pip install --upgrade {' '.join(dev_package_specs)}"
    dev_result = run_command(dev_command)
    if dev_result is None:
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
    dev_dependencies = pyproject["tool"]["uv"]["dev-dependencies"]
    original_dependencies = original_pyproject["project"]["dependencies"]
    original_dev_dependencies = original_pyproject["tool"]["uv"]["dev-dependencies"]
    updates_made = False
    updated_packages = []

    def update_dependency_version(dep, original_dep, req_version):
        """Update dependency version while preserving extras."""
        name = clean_package_name(dep)
        # Preserve any extras from the original dependency
        extras_match = re.search(r"\[(.*?)\]", original_dep)
        extras = f"[{extras_match.group(1)}]" if extras_match else ""

        # Keep any existing version specifiers (e.g., >=)
        specifier = re.search(r"([<>=]+)", original_dep)
        if specifier:
            return f"{name}{extras}{specifier.group(1)}{req_version}"
        return f"{name}{extras}>={req_version}"

    # Update main dependencies
    for i, dep in enumerate(dependencies):
        name = clean_package_name(dep)
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
                    new_dep = update_dependency_version(
                        dep, original_dependencies[i], req_version
                    )
                    if new_dep != original_dependencies[i]:
                        dependencies[i] = new_dep
                        updates_made = True
                        updated_packages.append((name, original_version, req_version))
                break

    # Update dev dependencies
    for i, dep in enumerate(dev_dependencies):
        name = clean_package_name(dep)
        original_version = re.split("[=<>]", original_dev_dependencies[i])[-1].strip()
        for req in updated_requirements:
            req_parts = req.strip().split("==")
            if len(req_parts) == 2:
                req_name, req_version = req_parts
            else:
                req_name = req_parts[0]
                req_version = None

            if req_name.lower() == name.lower():
                if req_version and req_version != original_version:
                    new_dep = update_dependency_version(
                        dep, original_dev_dependencies[i], req_version
                    )
                    if new_dep != original_dev_dependencies[i]:
                        dev_dependencies[i] = new_dep
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
