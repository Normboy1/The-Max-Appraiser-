"""
AI Software Appraiser - A tool for evaluating software quality and value using AI.
"""

__version__ = "0.1.0"

from .core.appraiser import SoftwareAppraiser
from .models.evaluation import CodeQualityReport, ProjectEvaluation

__all__ = ["SoftwareAppraiser", "CodeQualityReport", "ProjectEvaluation"]
