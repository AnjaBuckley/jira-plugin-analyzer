from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ChangeType(str, Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    CONFIGURATION = "configuration"


class Importance(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class ReleaseNote(BaseModel):
    version: str
    changes: List[str]
    change_type: ChangeType
    importance: Importance
    compatibility_warnings: Optional[List[str]] = []

    class Config:
        allow_population_by_field_name = True


class PluginAnalysis(BaseModel):
    plugin_name: str
    current_version: str
    target_version: str
    jira_compatibility: List[str] = []
    admin_notes: List[ReleaseNote] = []
    user_notes: List[ReleaseNote] = []
    compatibility_warnings: List[str] = []

    class Config:
        allow_population_by_field_name = True

    def to_pretty_dict(self) -> dict:
        """Convert the analysis to a pretty formatted dictionary."""
        return {
            "Plugin": self.plugin_name,
            "Versions": f"{self.current_version} → {self.target_version}",
            "Jira Compatibility": "\n".join(f"• {note}" for note in self.jira_compatibility),
            "Admin Notes": "\n".join(
                f"[{note.version}] ({note.importance.upper()})\n"
                f"Type: {note.change_type.title()}\n"
                f"Changes:\n" + "\n".join(f"• {change}" for change in note.changes)
                for note in self.admin_notes
            ),
            "User Notes": "\n".join(
                f"[{note.version}] ({note.importance.upper()})\n"
                f"Type: {note.change_type.title()}\n"
                f"Changes:\n" + "\n".join(f"• {change}" for change in note.changes)
                for note in self.user_notes
            ),
            "Compatibility Warnings": "\n".join(f"⚠️ {warning}" for warning in self.compatibility_warnings),
        }
