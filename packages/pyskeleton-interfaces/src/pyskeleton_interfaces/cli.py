import os
import shutil
from typing import Annotated, Optional

import typer

cmder = typer.Typer()
create_cmder = typer.Typer(help="Create a new project or component.")
cmder.add_typer(
    create_cmder
)  # Add the create subcommand group to the main command group.


@create_cmder.command()
def create(
    project_name: str,
    project_path: Annotated[str, typer.Argument()] = os.getcwd(),
    python_version: Annotated[
        str,
        typer.Option(
            "--python-version",
            "-v",
            help="The Python version to use for the project. Default is 3.11.",
        ),
    ] = "3.11",
    venv_path: Optional[
        Annotated[
            str,
            typer.Option(
                "--venv",
                "-e",
                help="The path to the virtual environment. Default is None and will not create a venv.",
            ),
        ]
    ] = None,
    force: Annotated[
        bool, typer.Option(help="Force creation even if directory exists.")
    ] = False,
):
    """
    Create a new project with the specified name and path.
    """
    from pyskeleton_core.core.create_project import ProjectCreator

    creator = ProjectCreator(
        project_name,
        os.path.join(project_path, project_name),
        python_version,
        force,
        venv_path=venv_path,
    )
    try:
        creator.run()
        typer.echo(f"Project {project_name} created at {project_path}")
    except Exception as e:
        typer.secho(f"Error creating project: {e}", fg=typer.colors.RED)
        shutil.rmtree(creator.project_path, ignore_errors=True)
        raise typer.Exit(code=1) from e


def main():
    cmder()


if __name__ == "__main__":
    main()
