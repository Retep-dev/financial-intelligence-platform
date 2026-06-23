from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Base interface for document parsers."""

    supported_extensions: list[str] = []

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Extract raw text from a file."""
        pass
