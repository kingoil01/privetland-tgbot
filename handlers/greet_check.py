import re
from aiogram.types import Message

ALLOWED_STICKER_SETS: set[str] = {"Privet4956"}
ALLOWED_STICKERS: set[str] = set()

MAX_LEN = 20

_PATTERNS: list[re.Pattern] = [
    re.compile(r"^прив[а-яёa-z]{0,16}$", re.IGNORECASE),
    re.compile(r"^h(i+|ey+|ello+|owdy|iya)$", re.IGNORECASE),
    re.compile(r"^(hallo+|moin+|servus|tach)$", re.IGNORECASE),
    re.compile(r"^(salut+|bonjour+|coucou+|all[oô]+)$", re.IGNORECASE),
    re.compile(r"^(hola+|buenas|ola+)$", re.IGNORECASE),
    re.compile(r"^(konnichiwa|ohayou?|やあ|こんにちは|おはよう|ヤア|コンニチハ)$", re.IGNORECASE),
]


def is_greeting_text(text: str | None) -> bool:
    if not text:
        return False
    word = text.strip()
    if len(word) > MAX_LEN:
        return False
    return any(p.match(word) for p in _PATTERNS)


def is_greeting_sticker(message: Message) -> bool:
    if not message.sticker:
        return False
    return (
        message.sticker.set_name in ALLOWED_STICKER_SETS
        or message.sticker.file_unique_id in ALLOWED_STICKERS
    )


def is_greeting(message: Message) -> bool:
    return is_greeting_text(message.text) or is_greeting_sticker(message)
