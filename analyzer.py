from typing import List, Dict, Any
import re
from transformers import pipeline


class ReleaseNotesAnalyzer:
    def __init__(self):
        # Initialize the sentiment analysis pipeline for importance classification
        self.classifier = pipeline("zero-shot-classification")

        # Keywords for categorization
        self.admin_keywords = [
            "admin",
            "configuration",
            "security",
            "performance",
            "database",
            "server",
            "installation",
            "upgrade",
            "migration",
            "compatibility",
            "permission",
            "access",
            "authentication",
            "authorization",
        ]

        self.user_keywords = [
            "feature",
            "improvement",
            "bug fix",
            "ui",
            "interface",
            "workflow",
            "user experience",
            "usability",
            "functionality",
            "new",
            "enhancement",
        ]

        self.compatibility_keywords = [
            "compatibility",
            "requires",
            "supported",
            "version",
            "jira",
            "breaking change",
            "deprecated",
            "removed",
            "upgrade",
            "migration",
        ]

    def analyze_release_notes(
        self,
        release_notes: List[Dict[str, Any]],
        current_jira_version: str,
        target_jira_version: str,
    ) -> Dict[str, str]:
        """
        Analyze release notes and categorize them into admin and user relevant sections.

        Args:
            release_notes: List of release note dictionaries
            current_jira_version: Current Jira version
            target_jira_version: Target Jira version

        Returns:
            Dictionary containing categorized release notes
        """
        admin_notes = []
        user_notes = []
        compatibility_warnings = []

        for note in release_notes:
            version = note["version"]
            content = note["notes"]

            # Check for compatibility issues
            compatibility_issues = self._check_compatibility(
                content, current_jira_version, target_jira_version
            )
            if compatibility_issues:
                compatibility_warnings.extend(compatibility_issues)

            # Categorize the note
            if self._is_admin_relevant(content):
                admin_notes.append(f"**Version {version}:**\n{content}")
            if self._is_user_relevant(content):
                user_notes.append(f"**Version {version}:**\n{content}")

        return {
            "admin_notes": "\n\n".join(admin_notes)
            if admin_notes
            else "No admin-relevant changes found.",
            "user_notes": "\n\n".join(user_notes)
            if user_notes
            else "No user-relevant changes found.",
            "compatibility_warnings": "\n\n".join(compatibility_warnings)
            if compatibility_warnings
            else "",
        }

    def _is_admin_relevant(self, content: str) -> bool:
        """Check if content is relevant for administrators."""
        return any(
            keyword.lower() in content.lower() for keyword in self.admin_keywords
        )

    def _is_user_relevant(self, content: str) -> bool:
        """Check if content is relevant for end users."""
        return any(keyword.lower() in content.lower() for keyword in self.user_keywords)

    def _check_compatibility(
        self, content: str, current_jira_version: str, target_jira_version: str
    ) -> List[str]:
        """Check for compatibility issues in the content."""
        warnings = []

        # Look for version requirements
        version_pattern = r"requires\s+Jira\s+(\d+\.\d+\.\d+)"
        matches = re.finditer(version_pattern, content, re.IGNORECASE)

        for match in matches:
            required_version = match.group(1)
            if self._compare_versions(required_version, target_jira_version) > 0:
                warnings.append(
                    f"⚠️ Warning: This version requires Jira {required_version} or higher"
                )

        # Look for breaking changes
        if "breaking change" in content.lower():
            warnings.append("⚠️ Warning: Contains breaking changes")

        # Look for deprecation notices
        if "deprecated" in content.lower():
            warnings.append("⚠️ Warning: Contains deprecated features")

        return warnings

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings."""

        def parse_version(v: str) -> List[int]:
            return [int(x) for x in v.split(".")]

        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1

        return 0
