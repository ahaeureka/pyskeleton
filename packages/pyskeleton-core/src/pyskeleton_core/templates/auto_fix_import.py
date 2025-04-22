import fnmatch
import os
from pathlib import Path

import isort
from jinja2 import Environment, FileSystemLoader


class AutoFixImportPath:
    def __init__(self, project_name, project_dir: str):
        self.project_dir = Path(project_dir)
        self.project_name = project_name

    def render(self):
        directory = self.project_dir / "packages"
        for root, _, files in os.walk(directory):
            env = Environment(loader=FileSystemLoader(root))
            for file in fnmatch.filter(files, "*.py.j2"):
                tmpl = env.get_template(file)
                context = {"project_name": self.project_name.replace("-", "_")}
                output = tmpl.render(context)
                output_path = (
                    self.project_dir
                    / "packages"
                    / Path(root).relative_to(directory)
                    / file.replace(".j2", "")
                )
                with open(output_path, "w", encoding="utf8") as f:
                    f.write(isort.code(output))
