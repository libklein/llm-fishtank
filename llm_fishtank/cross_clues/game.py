# coding=utf-8
import rich.table

from openai import OpenAI
import random
from collections import defaultdict
from typing import List, Tuple, Dict
from os import environ

from pydantic import BaseModel, field_validator


class LLMApi:
    def __init__(self, endpoint: str, api_key: str):
        self._client = OpenAI(api_key=api_key, base_url=endpoint)

    def prompt(self, input_text: str) -> str:
        """Placeholder for actual LLM API call."""
        response = self._client.chat.completions.create(
            model="n/a",
            temperature=0.5,
            n=1,
            stop=None,
            messages=[{"role": "user", "content": input_text}],
        )
        return response.choices[0].message.content


class Response(BaseModel):
    message: str
    guess: Tuple[str, int]
    score: int

    # Define a pre-validation hook to parse guess
    @field_validator("guess", mode="before")
    def parse_guess(cls, v: str | Tuple[str, int]) -> Tuple[str, int]:
        if isinstance(v, str):
            col, row = tuple(iter(v))
            return col, int(row)
        return v


class CrossClues:
    def __init__(
        self,
        llm_api: LLMApi,
        models: List[str],
        row_words: List[str],
        col_words: List[str],
        clue_giver_prompt: str,
        discuss_and_vote_prompt: str,
    ) -> None:
        self.llm_api = llm_api
        self.models = models
        self.rows = len(row_words)
        self.cols = len(col_words)
        self.row_words = row_words
        self.col_words = col_words
        self.grid = self.initialize_grid()
        self.revealed: Dict[Tuple[str, int], Tuple[str, bool]] = {}
        self.history: List[Tuple[str, str, Tuple[str, int], Tuple[str, int]]] = []
        self.clue_giver_prompt = clue_giver_prompt
        self.discuss_and_vote_prompt = discuss_and_vote_prompt

    def initialize_grid(self) -> Dict[Tuple[str, int], Tuple[str, str]]:
        """Creates a grid using provided row and column words."""
        grid = {}
        for r in range(self.rows):
            for c in range(self.cols):
                grid[(chr(65 + r), c + 1)] = (self.row_words[r], self.col_words[c])
        return grid

    def _format_history_entry(
        self, entry: Tuple[str, str, Tuple[str, int], Tuple[str, int]]
    ) -> str:
        """Formats a history entry for display."""
        model, clue, coord, guess = entry
        word = self.grid[coord]
        return f"{model} gave clue: {clue} for {word}. Guessed: {guess}"

    def _print_grid(self) -> None:
        table = rich.table.Table()
        table.add_column(" ")
        for c in range(1, self.cols + 1):
            table.add_column(f"{chr(64 + c)}: {self.col_words[c - 1]}")
        for r in range(1, self.rows + 1):
            row = [f"{r}: {self.row_words[r-1]}"]
            # Add revealed words to the grid
            for c in range(1, self.cols + 1):
                coord = (chr(64 + r), c)
                word, was_correct = self.revealed.get(coord, ("", False))
                if word != "":
                    row.append(f"{word}{'✅' if was_correct else '❌'}")
                else:
                    row.append("?")
            table.add_row(*row)
        rich.console.Console().print(table)

    def clue_giver(self, llm: str, coordinate: Tuple[str, int]) -> str:
        """Uses the LLM API to generate a clue for a specific coordinate."""
        row_word, col_word = self.grid[coordinate]
        prompt = self.clue_giver_prompt.format(
            model=llm,
            coordinate=coordinate,
            row_word=row_word,
            column_word=col_word,
            row_words="'" + ", ".join(self.row_words) + "'",
            column_words="'" + ", ".join(self.col_words) + "'",
            revealed_words="'" + ", ".join(x for x, _ in self.revealed.values()) + "'",
            history_of_clues="\n".join(map(self._format_history_entry, self.history)),
        )

        clue = self.llm_api.prompt(prompt)
        # Extract the last word from the response
        clue = clue.split()[-1].replace(".", "")
        print(f"[Clue-Giver {llm}] Coordinate {coordinate}: Clue -> {clue}")
        return clue

    def discuss_and_vote(self, clue_giver_model: str, clue: str) -> Tuple[str, int]:
        """Uses the LLM API to simulate AI models discussing and voting on a coordinate."""
        votes: Dict[Tuple[str, int], int] = defaultdict(int)
        confidence_scores: Dict[Tuple[str, int], List[int]] = defaultdict(list)

        for _ in range(12):  # Up to 12 discussion turns
            model = random.choice(self.models)
            prompt = self.discuss_and_vote_prompt.format(
                model=model,
                clue_word=clue,
                clue_giver_name=clue_giver_model,
                row_words="'" + ", ".join(self.row_words) + "'",
                column_words="'" + ", ".join(self.col_words) + "'",
                revealed_words="'"
                + ", ".join(x for x, _ in self.revealed.values())
                + "'",
                history_of_clues="\n".join(
                    map(self._format_history_entry, self.history)
                ),
            )
            raw_response = self.llm_api.prompt(prompt)
            # print(raw_response, file=sys.stderr)

            try:
                first_bracket = raw_response.rindex("{")
                last_bracket = raw_response.rindex("}") + 1
                filtered_response = raw_response[first_bracket:last_bracket]
                response = Response.model_validate_json(filtered_response)
            except Exception as e:
                # print(f"Error: {e}\n{raw_response}")
                continue

            guessed_coord = response.guess
            confidence = response.score
            message = response.message
            votes[guessed_coord] += 1
            confidence_scores[guessed_coord].append(confidence)

            print(
                f"[{model}] Message: {message}\nGuess: {guessed_coord} (Confidence: {confidence}/10)"
            )

            # Early stopping if strong consensus (e.g., 4 of last 5 agree & avg confidence ≥ 7)
            top_coord, count = max(votes.items(), key=lambda x: x[1])
            avg_conf = sum(confidence_scores[top_coord]) / len(
                confidence_scores[top_coord]
            )
            if count >= 4 and avg_conf >= 7:
                print(
                    f"\nConsensus reached early at {top_coord} (Avg Conf: {avg_conf:.1f})\n"
                )
                return top_coord

        # Select the coordinate with the highest summed confidence if no early consensus
        best_coord = max(confidence_scores, key=lambda x: sum(confidence_scores[x]))
        print(f"\nFinal Guess: {best_coord} (Highest confidence sum)\n")
        return best_coord

    def play_game(self) -> None:
        self._print_grid()

        while len(self.revealed) < len(self.grid):
            clue_giver_model = random.choice(self.models)
            coord = random.choice(
                [c for c in self.grid.keys() if c not in self.revealed]
            )

            clue = self.clue_giver(clue_giver_model, coord)
            guess = self.discuss_and_vote(clue_giver_model, clue)

            was_correct = guess == coord

            if was_correct:
                print(f"✅ Correct! {coord} was guessed correctly.")
            else:
                print(f"❌ Incorrect. {coord} was the right answer.")

            self.revealed[coord] = (clue, was_correct)
            self.history.append((clue_giver_model, clue, coord, guess))
            print("\n--- Next Round ---\n")
            self._print_grid()

        print("🎉 Game Over! Final Revealed Grid:")
        for k, v in self.revealed.items():
            print(f"{k}: {v}")
