import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class QuizAttempt:
    timestamp: str
    score: int
    total: int
    accuracy: float

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "score": self.score,
            "total": self.total,
            "accuracy": self.accuracy,
        }


class PerformanceStore:
    def __init__(self, file_path: str = "data/performance.json"):
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"attempts": []}, indent=2), encoding="utf-8")

    def _load(self) -> Dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"attempts": []}

    def _save(self, data: Dict) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_attempt(self, score: int, total: int) -> None:
        accuracy = (score / total) * 100 if total else 0
        attempt = QuizAttempt(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            score=score,
            total=total,
            accuracy=round(accuracy, 2),
        )
        data = self._load()
        data.setdefault("attempts", []).append(attempt.to_dict())
        self._save(data)

    def get_attempts(self) -> List[Dict]:
        return self._load().get("attempts", [])

    def get_summary(self) -> Dict:
        attempts = self.get_attempts()
        if not attempts:
            return {
                "quizzes_taken": 0,
                "avg_accuracy": 0,
                "best_accuracy": 0,
            }

        accuracies = [a["accuracy"] for a in attempts]
        return {
            "quizzes_taken": len(attempts),
            "avg_accuracy": round(sum(accuracies) / len(accuracies), 2),
            "best_accuracy": round(max(accuracies), 2),
        }
