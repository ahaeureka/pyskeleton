import os
import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pyskeleton_core.templates.auto_fix_import import AutoFixImportPath
from pyskeleton_core.templates.devcontainer import DevContainerRenderer
from pyskeleton_core.utils.project import ProjectHelper


class ProjectCreator:
    def __init__(
        self,
        project_name: str,
        project_path: str,
        py_version="3.11",
        force=False,
        venv_path=None,
    ):
        self.project_name = project_name
        self.project_path = Path(project_path)
        self.py_version = py_version
        self.force = force
        self.venv_path = venv_path

    def update_project_name_toml(self):
        """
        Updates the project name in the project.toml file.
        """
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file == "pyproject.toml.j2":
                    _root = Path(root)
                    env = Environment(loader=FileSystemLoader(_root))
                    template = env.get_template("pyproject.toml.j2")
                    context = {
                        "project_name": self.project_name,
                    }
                    output = template.render(context)
                    with open(_root / "pyproject.toml", "w", encoding="utf8") as f:
                        f.write(output)

    def create_project_structure(self):
        self.project_path.parent.mkdir(parents=True, exist_ok=True)
        project_root = ProjectHelper.get_project_root()
        # copy project template files to the new project directory
        # This is a placeholder for the actual file copying logic
        if self.project_path.exists() and self.force:
            # Remove existing directory if force is True
            shutil.rmtree(self.project_path)
        # Copy the template project to the new project directory
        shutil.copytree(project_root / "project-template", self.project_path)

        def rename_template_dirs(root_dir: Path):
            for item in root_dir.iterdir():
                if item.is_dir():
                    # Rename the directory if it starts with "template"
                    if item.name.startswith("template"):
                        new_name = item.name.replace("template", self.project_name)
                        item.rename(item.parent / new_name)
                        # Continue with the renamed directory
                        item = item.parent / new_name
                    # Recursively process the directory
                    rename_template_dirs(item)

        rename_template_dirs(self.project_path)

    def clean_j2_files(self):
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".j2"):
                    os.remove(os.path.join(root, file))

    def create_venv_by_uv(self):
        """
        Create a virtual environment in the project using uv.
        """
        subprocess.run(
            ["uv", "venv", "--allow-existing", self.venv_path], cwd=self.project_path
        )

        # Activate the virtual environment
        # source /path/to/venv/bin/activate
        activate_script = os.path.join(self.venv_path, "bin", "activate")
        subprocess.run([".", activate_script], shell=True)
        # Install dependencies
        # uv sync --active --all-packages
        subprocess.run(
            ["uv", "sync", "--active", "--all-packages"], cwd=self.project_path
        )

    def render(self):
        devcontainer_renderer = DevContainerRenderer(
            self.project_name, self.project_path, self.py_version
        )
        devcontainer_renderer.render()
        AutoFixImportPath(self.project_name, self.project_path).render()

        # Add more renderers here as needed

    def run(self):
        self.create_project_structure()
        self.render()
        self.update_project_name_toml()
        self.clean_j2_files()
        if self.venv_path:
            self.create_venv_by_uv()


if __name__ == "__main__":
    creator = ProjectCreator("my-new-project", "/tmp/my-new-project", force=True)
    creator.run()
