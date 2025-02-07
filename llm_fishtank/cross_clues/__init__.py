# coding=utf-8
from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompts"
CLUE_GIVER_PROMPT_TEMPLATE = (PROMPT_DIR / "clue_giver_prompt.txt").read_text()
DISCUSS_PROMPT_TEMPLATE = (PROMPT_DIR / "discuss_and_vote_prompt.txt").read_text()
WORDLIST = (Path(__file__).parent / "dictionary.txt").read_text().splitlines()
