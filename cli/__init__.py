import asyncio
from pathlib import Path

import typer

import api
from api.settings import Settings
from cli import new, routines
from cli import view

app = typer.Typer()
app.add_typer(new.app, name="new", help="Create new plan, recipe, etc")
app.add_typer(view.app, name="view", help="View plan, shopping list, etc")


@app.command()
def init(
    path: Path = typer.Argument(
        help="The path in which to initialise a new recipe library"
    ),
):
    """
    Initialise a new recipe library
    """
    path = path.absolute()
    print(f"you passed {path=}")
    api.init_library(path)


@app.command()
def config(
    recipe_library: str = typer.Option(
        "",
        "--recipe-library",
        help="The folder in which the YAML recipes are stored",
    ),
):
    """
    Update and/or view configuration
    """
    settings = Settings.from_file()
    if recipe_library:
        print(f"{recipe_library=}")
        if (recipe_library := Path(recipe_library)).exists():
            absolute_path = recipe_library.absolute()
            settings.recipe_library = absolute_path
            print(f"Saving recipe library: {absolute_path}")
            settings.save()
        else:
            typer.echo(f"{recipe_library} does not exist")

    print("config: ")
    for key, val in settings.model_dump().items():
        print(f"\t{key}: {val}".expandtabs(4))


@app.command()
def plan(
    query: list[str] = typer.Argument(help="Search term to find recipes"),
):
    """
    Add a recipe to a plan
    """
    query = " ".join(query)
    asyncio.run(routines.plan_recipe(query))


@app.command()
def export():
    """
    Convert YAML recipes to markdown
    """
    asyncio.run(routines.export_recipes())
