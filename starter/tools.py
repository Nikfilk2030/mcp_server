import json
from pathlib import Path

SCHEDULE = json.loads(Path(__file__).with_name("schedule.json").read_text(encoding="utf-8"))


def ping() -> str:
    """Проверить связь с сервером"""
    return "pong"


def lookup_club_room(club_id: str) -> str:
    """Найти аудиторию клуба по точному идентификатору"""
    # TODO: найдите клуб в SCHEDULE и верните аудиторию или «Клуб не найден»
    raise NotImplementedError("TODO: lookup_club_room")
