from typing import Literal

def get_language_id(language: Literal["java8", "node.js", "python3", "c++17"]) -> int:
    return {
        "java8": 3,
        "node.js": 17,
        "python3": 28,
        "c++17": 84
    }[language]