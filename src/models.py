from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class MCQ:
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Flashcard:
    front: str
    back: str
    concept: str

    def to_dict(self) -> Dict:
        return asdict(self)
