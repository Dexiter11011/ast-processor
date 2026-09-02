"""Document navigation layer — semantic targets, references, and list fields."""

from md2docx.navigation.kinds import NavigationTargetKind
from md2docx.navigation.model import ListOfFigures, ListOfTables
from md2docx.navigation.reference import ReferenceManager
from md2docx.navigation.registry import NavigationRegistry
from md2docx.navigation.target import NavigationTarget

__all__ = [
    "ListOfFigures",
    "ListOfTables",
    "NavigationRegistry",
    "NavigationTarget",
    "NavigationTargetKind",
    "ReferenceManager",
]
