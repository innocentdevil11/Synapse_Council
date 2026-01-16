from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator


class DecisionWeights(BaseModel):
    """User-provided weights for each agent, normalized to sum to 1.0."""
    risk: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for Risk & Logic agent")
    eq: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for EQ Advocate agent")
    values: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for Values Guard agent")
    red_team: float = Field(default=0.1, ge=0.0, le=1.0, description="Weight for Red Team agent")

    @field_validator("*", mode="before")
    @classmethod
    def validate_weight(cls, v: Any) -> float:
        """Coerce to float if needed."""
        return float(v)

    def normalize(self) -> "DecisionWeights":
        """Normalize weights to sum to 1.0."""
        total = self.risk + self.eq + self.values + self.red_team
        if total == 0:
            # Fallback to equal weights
            return DecisionWeights(risk=0.25, eq=0.25, values=0.25, red_team=0.25)
        return DecisionWeights(
            risk=self.risk / total,
            eq=self.eq / total,
            values=self.values / total,
            red_team=self.red_team / total,
        )

    def to_dict(self) -> Dict[str, float]:
        return {"risk": self.risk, "eq": self.eq, "values": self.values, "red_team": self.red_team}


class DecisionRequest(BaseModel):
    """User input for a decision to be analyzed by the council."""
    dilemma: str = Field(..., min_length=10, description="The main decision dilemma")
    context: Optional[str] = Field(default=None, description="Additional context")
    weights: Optional[DecisionWeights] = Field(default_factory=DecisionWeights)


class AgentResponse(BaseModel):
    """Structured output from a single agent."""
    recommendation: Literal["PROCEED", "CAUTION", "BLOCK"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    # Role-specific fields (optional, populated by agent)
    risk_level: Optional[str] = None
    burnout_risk: Optional[str] = None
    stakeholder_impact: Optional[str] = None
    unstated_assumptions: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class ConflictMatrix(BaseModel):
    """Pairwise conflict scores between agents (0 = aligned, 1 = opposed)."""
    risk_eq: float
    risk_values: float
    risk_red_team: float
    eq_values: float
    eq_red_team: float
    values_red_team: float

    def average(self) -> float:
        """Average conflict across all pairs."""
        return (
            self.risk_eq
            + self.risk_values
            + self.risk_red_team
            + self.eq_values
            + self.eq_red_team
            + self.values_red_team
        ) / 6


class AuditEntry(BaseModel):
    """Record of a debate round."""
    round: int
    responses: Dict[str, AgentResponse]
    conflict_matrix: Optional[ConflictMatrix] = None


class RecommendationResponse(BaseModel):
    """Final output from the council."""
    recommendation: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    conflict_heatmap: ConflictMatrix
    agent_responses: Dict[str, AgentResponse]
    debate_rounds: int
    audit_trail: List[AuditEntry]
    execution_time_ms: float
    head_council_verdict: Optional[Dict[str, Any]] = None  # HeadCouncilResponse data
    numeric_score: Optional[float] = None  # Raw numeric aggregation
    numeric_confidence: Optional[float] = None  # Confidence from numeric aggregation