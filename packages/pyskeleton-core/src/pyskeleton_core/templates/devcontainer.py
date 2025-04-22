from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pyskeleton_core.utils.project import ProjectHelper


class DevContainerRenderer:
    def __init__(self, project_name, project_dir: str, py_version="3.11"):
        self.project_name = project_name
        self.output_dir = Path(project_dir)
        self.py_version = py_version
        # Ensure the output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render(self):
        project_root = ProjectHelper.get_project_root()
        env = Environment(
            loader=FileSystemLoader(project_root / "project-template" / ".devcontainer")
        )
        template = env.get_template("Dockerfile.dev.j2")
        context = {
            "project_name": self.project_name,
        }
        devcontainer_output = template.render(context)

        pth_tmplate = env.get_template("project.pth.j2")
        pth_context = {
            "project_name": self.project_name,
        }
        pth_output = pth_tmplate.render(pth_context)

        project_env = Environment(
            loader=FileSystemLoader(project_root / "project-template")
        )
        project_template = project_env.get_template(".devcontainer.json.j2")
        project_context = {
            "project_name": self.project_name,
        }
        project_output = project_template.render(project_context)
        mypy_template = project_env.get_template(".mypy.ini.j2")
        mypy_context = {
            "project_name": self.project_name,
        }
        mypy_output = mypy_template.render(mypy_context)
        with open(self.output_dir / ".devcontainer.json", "w", encoding="utf8") as f:
            f.write(project_output)
        with open(self.output_dir / ".mypy.ini", "w", encoding="utf8") as f:
            f.write(mypy_output)
        with open(
            self.output_dir / ".devcontainer" / "project.pth", "w", encoding="utf8"
        ) as f:
            f.write(pth_output)

        with open(
            self.output_dir / ".devcontainer" / "Dockerfile.dev", "w", encoding="utf8"
        ) as f:
            f.write(devcontainer_output)
        dockerfile_template = project_env.get_template("Dockerfile.j2")
        dockerfile_context = {
            "python_version": self.py_version,
        }
        dockerfile_output = dockerfile_template.render(dockerfile_context)
        with open(self.output_dir / "Dockerfile", "w", encoding="utf8") as f:
            f.write(dockerfile_output)
