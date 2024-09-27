import re
from abc import ABC, abstractmethod
from typing import Callable, Tuple

import spacy
from faker import Faker
from faker.providers import BaseProvider


# Load default spacy nlp model for English language pattern matching.
nlp_model = spacy.load("en_core_web_sm")

fake = Faker()


class PatternMatcher(ABC):
    patterns: dict[
        str,
        Tuple[list[str], Callable[[str], bool], Callable[[], str]],
    ] = {}

    @abstractmethod
    def __init__(self, text: str) -> None:
        pass

    @staticmethod
    def _do_nothing(text) -> bool:
        return True


class RegexPatternMatcher(PatternMatcher):
    """
    Matches universaly recognized PII data using simple regex patterns.
    """

    def __init__(self, text):
        self.patterns = {
            "email": (
                re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text),
                self._do_nothing,
                lambda: fake.email(),
            ),
            "credit_card": (
                re.findall(r"\b(?:\d[ -]*?){13,16}\b", text),
                self._do_nothing,
                lambda: fake.credit_card_number(card_type=None),
            ),
            # This pattern will only recognize phone numbers in universal format.
            "phone_number": (
                re.findall(
                    r"(?:(?:\+?\d{1,4}[ -]?){1,11}\|?(?:\+?\d{1,4}[ -]?){1,11})", text
                ),
                self._filter_phone_numbers,
                lambda: fake.phone_number(),
            ),
        }

    @staticmethod
    def _filter_phone_numbers(phone_number) -> bool:
        """
        Filters any entries that have more digits than 15. According to the
        (ITU-T E. 164) standard, international phone numbers should not exceed 15 digits.
        """
        return sum(character.isdigit() for character in phone_number) <= 15


class NERPatternMatcher(PatternMatcher):
    """
    Recognizing PII data such as names and organizations using NLP model.
    """

    def __init__(self, text):
        doc = nlp_model(text)
        self.patterns = {
            "name": (
                [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
                self._do_nothing,
                lambda: fake.name(),
            ),
            "organization": (
                [ent.text for ent in doc.ents if ent.label_ == "ORG"],
                self._do_nothing,
                lambda: fake.company(),
            ),
        }


class PII_Mask:
    """
    Class containing methods for masking PII data in text.
    It can find PII by using different pattern matchers and mask it.
    """

    pattern_matchers: tuple[PatternMatcher] = (RegexPatternMatcher, NERPatternMatcher)
    matches_map: dict[str, list[str]] = {}
    masked_map: dict[str, str] = {}

    def __init__(self, text) -> None:
        self.text = text
        self._find_patterns()
        self.masked_text = self._mask()

    def _find_patterns(self) -> None:
        for pattern_matcher in self.pattern_matchers:
            for (
                key,
                pattern_filter_tuple,
            ) in pattern_matcher(self.text).patterns.items():
                matches = pattern_filter_tuple[0]
                matches = list(filter(pattern_filter_tuple[1], matches))
                for match in matches:
                    self.masked_map[match] = pattern_filter_tuple[2]()
                self.matches_map[key] = list(matches)

    def _mask(self) -> str:
        masked_text = self.text
        for match, replacement in self.masked_map.items():
            masked_text = masked_text.replace(match, replacement)
        return masked_text

    def unmask(self, text: str) -> str:
        """
        Public method for unmasking text recevied from the LLM model.
        """
        for match, replacement in self.masked_map.items():
            text = text.replace(replacement, match)
        return text
