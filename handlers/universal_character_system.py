from enum import Enum

class CharacterType(Enum):
    HERO = "hero"
    VILLAIN = "villain"
    SUPPORT = "support"
    MYSTIC = "mystic"
    AI = "ai"

class CharacterConfig:
    def __init__(self, name: str, traits: dict):
        self.name = name
        self.traits = traits

class UniversalCharacterSystem:
    def __init__(self):
        self.characters = {}

    def add_character(self, name: str, traits: dict):
        self.characters[name] = traits

    def get_character(self, name: str) -> dict:
        return self.characters.get(name, {})

character_manager = UniversalCharacterSystem()

def register_character(name: str, traits: dict):
    character_manager.add_character(name, traits)

def is_character_registered(name: str) -> bool:
    return name in character_manager.characters 