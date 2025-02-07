from typing import Annotated
from typer import Typer, Option, Argument
from llm_fishtank.cross_clues.game import LLMApi, CrossClues
from llm_fishtank.cross_clues import (
    CLUE_GIVER_PROMPT_TEMPLATE,
    DISCUSS_PROMPT_TEMPLATE,
    WORDLIST,
)
from pathlib import Path
import random


cross_clues_app = Typer()


@cross_clues_app.command()
def play(
    personas: Annotated[
        list[str], Argument(help="Personas of chatbots playing the game")
    ],
    llm_endpoint: Annotated[
        str, Option(help="LLM endpoint", envvar="LLM_ENDPOINT")
    ] = "",
    api_key: Annotated[str, Option(help="LLM API Key", envvar="API_KEY")] = "",
    number_of_rows: Annotated[int, Option(help="Number of rows in the word grid")] = 5,
    number_of_cols: Annotated[int, Option(help="Number of cols in the word grid")] = 5,
    wordlist_file: Annotated[
        Path | None, Option(help="Path to a line-delimitted wordlist")
    ] = None,
):
    if not llm_endpoint or not api_key:
        raise ValueError("Please specify LLM endpoint and API key")

    llm_api = LLMApi(
        endpoint=llm_endpoint,
        api_key=api_key,
    )

    print(f"{llm_endpoint=}, {api_key=}")

    if wordlist_file is not None:
        words = wordlist_file.read_text().splitlines()
    else:
        words = WORDLIST

    row_words: list[str] = random.sample(words, number_of_rows)
    col_words: list[str] = random.sample(words, number_of_cols)

    game = CrossClues(
        llm_api,
        personas,
        row_words,
        col_words,
        CLUE_GIVER_PROMPT_TEMPLATE,
        DISCUSS_PROMPT_TEMPLATE,
    )
    game.play_game()
