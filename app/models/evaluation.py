"""
Data models for software evaluation results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

class SeverityLevel(str, Enum):
    """Severity levels for code issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class CodeIssue:
    """Represents an issue found in the code."""
    message: str
    severity: SeverityLevel
    line: Optional[int] = None
    column: Optional[int] = None
    file_path: Optional[str] = None
    category: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class CodeQualityReport:
    """Comprehensive report on code quality."""
    score: float  # 0.0 to 1.0
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    language: str = ""
    summary: str = ""

@dataclass
class ProjectEvaluation:
    """Comprehensive evaluation of a software project."""
    overall_score: float  # 0.0 to 1.0
    code_quality: CodeQualityReport
    documentation_quality: float  # 0.0 to 1.0
    test_coverage: float  # 0.0 to 1.0
    performance_metrics: Dict[str, Any]
    security_issues: List[CodeIssue]
    dependencies: Dict[str, str] = field(default_factory=dict)
    maintainability_index: Optional[float] = None
    technical_debt: Optional[float] = None
    
    @property
    def grade(self) -> str:
        """Convert score to letter grade."""
        if self.overall_score >= 0.9:
            return "A"
        elif self.overall_score >= 0.8:
            return "B"
        elif self.overall_score >= 0.7:
            return "C"
        elif self.overall_score >= 0.6:
            return "D"
        else:
            return "F"

@dataclass
@dataclass
class IdeaEvaluation:
    """Evaluation results for a software idea/pitch."""
    originality: float  # 0.0 - 1.0
    functional_value: float  # 0.0 - 1.0
    scalability: float  # 0.0 - 1.0
    competition: float  # 0.0 - 1.0

    @property
    def overall_score(self) -> float:
        return round((self.originality + self.functional_value + self.scalability + self.competition) / 4, 3)

    @property
    def grade(self) -> str:
        score = self.overall_score
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

class ComparisonResult:
    """Results of comparing multiple projects."""
    projects: Dict[str, ProjectEvaluation]
    ranked_projects: List[str]  # Sorted by overall_score
    comparison_metrics: Dict[str, Any]
