"""Heurísticas para recusar nomes digitados ao acaso (ex: "aksjhdjagdjs"). Espelha src/lib/nameValidation.ts do frontend.

Apelidos com números, ponto e sublinhado são aceitos (ex: "joao123", "ana.clara"); as heurísticas valem para as letras."""
import re
import unicodedata
from typing import Optional

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 60
MAX_CONSONANT_RUN = 4

VOWELS = re.compile(r"[aeiouyøæœ]")
CONSONANT_RUN = re.compile(rf"[^aeiouyøæœ'-]{{{MAX_CONSONANT_RUN + 1},}}")
REPEATED_CHAR = re.compile(r"(.)\1\1")
REPEATED_CHUNK = re.compile(r"(.{2,})\1\1")
DOUBLED_CHUNK = re.compile(r"(.{3,})\1")
KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
KEYBOARD_SEQUENCE_LENGTH = 5
KEYBOARD_SEQUENCES = tuple(
    row[i:i + KEYBOARD_SEQUENCE_LENGTH]
    for row in KEYBOARD_ROWS
    for i in range(len(row) - KEYBOARD_SEQUENCE_LENGTH + 1)
)


def _strip_accents(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", value) if not unicodedata.category(c).startswith("M"))


def _has_only_allowed_chars(name: str) -> bool:
    return all(unicodedata.category(c).startswith("L") or c.isdigit() or c in " '-._" for c in name)


def _letters_only(word: str) -> str:
    return re.sub(r"[\d._]", "", word)


def _looks_like_gibberish(word: str) -> bool:
    return bool(
        (len(word) > 2 and not VOWELS.search(word))
        or CONSONANT_RUN.search(word)
        or REPEATED_CHAR.search(word)
        or REPEATED_CHUNK.search(word)
        or DOUBLED_CHUNK.search(word)
        or any(sequence in word for sequence in KEYBOARD_SEQUENCES)
    )


def normalize_name(raw_name: str) -> str:
    return " ".join(raw_name.split())


def validate_name(raw_name: str) -> Optional[str]:
    """Retorna a mensagem de erro do nome, ou None se ele parecer um nome real."""
    name = normalize_name(raw_name)

    if len(name) < MIN_NAME_LENGTH:
        return f"O nome deve ter pelo menos {MIN_NAME_LENGTH} letras."

    if len(name) > MAX_NAME_LENGTH:
        return f"O nome deve ter no máximo {MAX_NAME_LENGTH} caracteres."

    if not _has_only_allowed_chars(name):
        return "Use apenas letras, números, espaços, ponto, hífen ou sublinhado."

    words = [_letters_only(word) for word in _strip_accents(name).lower().split(" ")]

    if len(re.sub(r"['-]", "", words[0])) < MIN_NAME_LENGTH:
        return "Digite um nome válido."

    if any(_looks_like_gibberish(word) for word in words if word):
        return "Digite um nome válido."

    return None
