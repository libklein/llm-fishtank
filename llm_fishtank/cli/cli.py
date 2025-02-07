import typer
from llm_fishtank.cli.cross_clues import cross_clues_app

main_app = typer.Typer()
main_app.add_typer(cross_clues_app, name="cross-clues")

if __name__ == "__main__":
    main_app()
