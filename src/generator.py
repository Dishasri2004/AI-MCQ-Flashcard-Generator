import random
import re
from typing import List, Tuple

from src.models import Flashcard, MCQ
from src.nlp_engine import extract_key_concepts, sentence_relevance, split_sentences


def _find_supporting_sentence(concept: str, sentences: List[str]) -> str:
    for sentence in sentences:
        if concept.lower() in sentence.lower():
            return sentence.strip()
    return sentences[0].strip() if sentences else ""


def _create_cloze(sentence: str, concept: str) -> str:
    pattern = re.compile(re.escape(concept), re.IGNORECASE)
    replaced = pattern.sub("_____", sentence, count=1)
    return replaced


def _pick_distractors(concept: str, concepts: List[str], k: int = 3) -> List[str]:
    pool = [c for c in concepts if c.lower() != concept.lower()]
    if len(pool) < k:
        pool += ["none of these", "generalization", "contextual cue"]
    random.shuffle(pool)
    return pool[:k]


def generate_flashcards(text: str, max_cards: int = 15) -> List[Flashcard]:
    sentences = split_sentences(text)
    concepts = extract_key_concepts(text, top_n=max_cards * 2)
    ranked_sentences = [s for s, _ in sentence_relevance(sentences, concepts)]

    cards = []
    used = set()
    for concept in concepts:
        if concept in used:
            continue
        support = _find_supporting_sentence(concept, ranked_sentences)
        if not support:
            continue
        front = f"What is {concept}?"
        back = support
        cards.append(Flashcard(front=front, back=back, concept=concept))
        used.add(concept)
        if len(cards) >= max_cards:
            break

    return cards


def generate_mcqs(text: str, max_questions: int = 10) -> List[MCQ]:
    random.seed(7)
    sentences = split_sentences(text)
    concepts = extract_key_concepts(text, top_n=max_questions * 3)
    ranked_sentences = [s for s, _ in sentence_relevance(sentences, concepts)]

    questions: List[MCQ] = []
    used_clozes = set()

    for concept in concepts:
        support = _find_supporting_sentence(concept, ranked_sentences)
        if not support or len(support) < 40:
            continue

        cloze = _create_cloze(support, concept)
        if cloze == support or cloze in used_clozes:
            continue

        distractors = _pick_distractors(concept, concepts, k=3)
        options = [concept] + distractors
        random.shuffle(options)

        questions.append(
            MCQ(
                question=f"Complete the statement: {cloze}",
                options=options,
                correct_answer=concept,
                explanation=f"The statement describes '{concept}' in the source material.",
            )
        )
        used_clozes.add(cloze)

        if len(questions) >= max_questions:
            break

    return questions


def build_learning_content(text: str, max_questions: int = 10, max_cards: int = 15) -> Tuple[List[MCQ], List[Flashcard], List[str]]:
    mcqs = generate_mcqs(text=text, max_questions=max_questions)
    flashcards = generate_flashcards(text=text, max_cards=max_cards)
    concepts = extract_key_concepts(text=text, top_n=20)
    return mcqs, flashcards, concepts
