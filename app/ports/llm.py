from typing import Protocol

from app.domain.models import Chunk


class LanguageModel(Protocol):
    def answer(self, question: str, context: list[Chunk]) -> str: ...
