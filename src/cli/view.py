"""
view.py
"""

import typer

from .utils import echo, requires_library_init
from .. import api
from ..api.shopping_list import MergedIngredient

app = typer.Typer()


@app.command(name="plan")
@requires_library_init
def view_plan():
    """
    view_plan
    """
    plan = api.Plan.current()
    echo("Current plan:")
    echo(f"\tcreated: {plan.created.isoformat()}")
    if plan.recipes:
        recipes_multipliers = {}
        for recipe in plan.recipes:
            recipes_multipliers[recipe] = recipes_multipliers.get(recipe, 0) + 1
        echo("\trecipes:")
        for recipe, multiplier in recipes_multipliers.items():
            s = f"\t\t{recipe}"
            if multiplier > 1:
                s += f" (x{multiplier})"
            echo(s)


@app.command(name="list")
@requires_library_init
def view_list():
    """
    view_list
    """
    plan = api.Plan.current()
    ingredients = plan.shopping_list()
    echo("Current shopping list:")
    for ing_name in sorted(ingredients):
        amounts = ingredients[ing_name]
        echo(_format_ingredient_for_list(ing_name, amounts))


@app.command(name="recipe")
@requires_library_init
def view_recipe():
    """
    view recipe
    """
    # todo: serialize recipe nicely for terminal


def _format_ingredient_for_list(
    ing_name: str,
    amounts: MergedIngredient,
    max_width: int = 80,
) -> str:
    right = ""
    unique_recipes = len(set(amounts.amountless))
    match [unique_recipes, amounts.unitless, len(amounts.units)]:
        case [0, 0, 0]:
            raise ValueError("empty Amounts!")

        # ========================= single line cases =========================
        # only 1 unique recipe (could be repeated)
        case [1, 0, 0]:
            recipe_strings = (
                amounts.amountless[0]
                if (count := len(amounts.amountless)) == 1
                else f"{amounts.amountless[0]} (x{count})"
            )
            right = f"enough for {recipe_strings}"

        # just the unitless amount
        case [0, unitless, 0]:
            right = str(unitless)

        # only 1 unit e.g. {"kg": 2.5}
        case [0, 0, 1]:
            unit, amount = next(iter(amounts.units.items()))
            right = f"{amount} {unit}"

        # ========================== multi line cases ==========================
        case _:
            if amounts.amountless:
                right += f"\n\t{_format_amountless(amounts.amountless)}"
            if amounts.unitless:
                right += f"\n\t{amounts.unitless}"
            for unit, amount in amounts.units.items():
                right += f"\n\t{amount} {unit}"

    if "\n" in right:
        return f"{ing_name}:{right}"
    result = f"{ing_name}: {right}"
    if len(result) > max_width:
        return f"{ing_name}:\n\t{right}"
    else:
        return result


def _format_amountless(names: list[str]) -> str:
    def _format(name: str, count: int) -> str:
        return name if count == 1 else f"{name} (x{count})"

    counts = _count(names)
    if len(counts) == 1:
        name, count = next(iter(counts.items()))
        return f"enough for {_format(name, count)}"
    else:
        result = "enough for:"
        for name, count in counts.items():
            s = _format(name, count)
            result += f"\n\t\t{s}"
        return result


def _count(names: list[str]) -> dict[str, int]:
    counts = {}
    for name in names:
        counts[name] = counts.get(name, 0) + 1
    return counts
