"""Telegram user entity."""

from collections import namedtuple

User = namedtuple("User", ("name", "user_id"))

EVGSOL = User("Рельс", 44989459)
KAIMIRA = User("Каймира", 1334065889)
PONIK = User("Поник", 372137239)
UNHEILIG = User("Унха", 347438021)
