import subprocess
import toml
import re
import os


def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error: {error.decode('utf-8')}")
        return None
    return output.decode("utf-8")


def update_packages():
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

    for i, dep in enumerate(dependencies):
        name = re.split("[=<>]", dep)[0].strip()
        for req in updated_requirements:
            req_parts = req.strip().split("==")
            if len(req_parts) == 2:
                req_name, req_version = req_parts
            else:
                req_name = req_parts[0]
                req_version = None

            if req_name.lower() == name.lower():
                if req_version:
                    # Keep any existing version specifiers (e.g., >=)
                    specifier = re.search(r"([<>=]+)", dep)
                    if specifier:
                        new_dep = f"{name}{specifier.group(1)}{req_version}"
                    else:
                        new_dep = f"{name}>={req_version}"

                    if new_dep != original_dependencies[i]:
                        dependencies[i] = new_dep
                        updates_made = True
                break

    if not updates_made:
        print(
            "No updates were necessary. All packages are already at their latest versions."
        )
        os.remove("requirements.txt")
        return

    # Custom TOML dumper to add new lines after each dependency
    class CustomTOMLEncoder(toml.TomlEncoder):
        def dump_sections(self, o, sup):
            retstr = super().dump_sections(o, sup)
            if sup == ["project", "dependencies"]:
                return "\n".join([line.rstrip() for line in retstr.split("\n")])
            return retstr

    # Write the updated pyproject.toml
    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f, encoder=CustomTOMLEncoder())

    print("pyproject.toml has been updated with the latest package versions.")

    # Delete the requirements.txt file
    os.remove("requirements.txt")
    print("requirements.txt has been deleted.")


if __name__ == "__main__":
    update_packages()
