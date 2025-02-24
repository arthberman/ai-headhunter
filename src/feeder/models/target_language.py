from enum import Enum


class TargetLanguage(str, Enum):
    """Enum for the target language to generate the query keywords in."""

    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GREEK = "el"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
