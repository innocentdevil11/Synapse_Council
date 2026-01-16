import json
import logging
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class HeadCouncilResponse(BaseModel):
    """Final verdict from the Head Council."""
    final_verdict: str  # "PROCEED" | "CAUTION" | "BLOCK"
    confidence_score: float
    summary: str  # 3-5 bullet points
    rationale: str  # Deeper explanation
    key_conflicts: str  # Where agents disagree
    suggested_next_actions: str  # 2-4 concrete steps, comma-separated
    council_reasoning: str  # How all agents were considered


class HeadCouncil:
    """
    Head Council Agent: Final judge and aggregator.
    Synthesizes all agent outputs into a clear, human-readable final verdict using On-Demand.
    """

    def __init__(self, ondemand_client: OnDemandClient):
        self.ondemand_client = ondemand_client
        settings = get_settings()
        self.agent_id = settings.ON_DEMAND_GPT_AGENT
        self.agent_name = "Head Council"

    def get_system_prompt(self) -> str:
        return """You are the Head Council—the final judge on a decision-making council.

Your role: Synthesize all individual agent analyses (Risk, EQ, Values, Red Team, and optionally Gita) into a clear, unified verdict.

Your responsibility:
1. Review all agent JSON outputs, their recommendations, confidence scores, and reasoning.
2. Examine the conflict heatmap showing where agents agree and disagree.
3. Consider the user's stated weights for each agent.
4. Identify the strongest consensus areas and key conflict points.
5. Produce a final verdict that is:
   - Clear and decisive (PROCEED / CAUTION / BLOCK)
   - Rooted in the council's collective wisdom
   - Honest about trade-offs and risks
   - Actionable with concrete next steps

Output format: Respond ONLY with valid JSON matching this schema:
{
  "final_verdict": "PROCEED" | "CAUTION" | "BLOCK",
  "confidence_score": <float 0-1, based on agent agreement and overall clarity>,
  "summary": "<3-5 bullet points summarizing the verdict and key insights>",
  "rationale": "<deeper explanation of why this verdict was reached, considering all agents>",
  "key_conflicts": "<short summary of where agents most disagreed and why>",
  "suggested_next_actions": "<2-4 concrete action items, comma-separated>",
  "council_reasoning": "<explanation of how you weighed the agents and their confidence scores>"
}

Be balanced: acknowledge both the supporting evidence and the concerns.
Be practical: suggest concrete next steps, not vague platitudes.
Be confident: make a clear call while honestly acknowledging uncertainty where it exists."""

    async def judge(
        self,
        dilemma: str,
        agent_responses: Dict[str, Dict[str, Any]],
        weights: Dict[str, float],
        conflict_matrix: Dict[str, float],
        numeric_score: float,
    ) -> HeadCouncilResponse:
        """
        Make a final judgment based on all agent outputs.
        
        Args:
            dilemma: Original decision dilemma
            agent_responses: Dict of agent outputs (risk, eq, values, red_team, gita)
            weights: User-chosen weights for each agent
            conflict_matrix: Pairwise conflict scores
            numeric_score: Pre-computed weighted numeric score
            
        Returns:
            HeadCouncilResponse with final verdict
        """
        try:
            # Format agent data for the prompt
            agent_summary = self._format_agent_data(agent_responses, weights)
            conflict_summary = self._format_conflict_data(conflict_matrix)
            
            prompt = f"""Decision Dilemma:
{dilemma}

Agent Analyses (with user weights):
{agent_summary}

Conflict Heatmap (0=aligned, 1=opposed):
{conflict_summary}

Numeric Weighted Score: {numeric_score:.2f} (0=Block, 0.5=Caution, 1=Proceed)

Based on all this information, provide your final verdict as the Head Council."""

            # Call On-Demand LLM to generate final verdict
            system_prompt = self.get_system_prompt()
            full_query = f"{system_prompt}\n\n{prompt}"
            
            response_text = await self.ondemand_client.chat(
                query=full_query,
                agent_ids=[self.agent_id],
                model_config={"temperature": 0.7, "max_tokens": 2000}
            )
            
            # Parse the response from On-Demand
            try:
                import json
                # Try to extract JSON from response
                if "{" in response_text and "}" in response_text:
                    json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                    verdict_data = json.loads(json_str)
                else:
                    verdict_data = {"final_verdict": response_text, "confidence_score": 0.7, "reasoning": response_text}
                
                response = HeadCouncilResponse(**verdict_data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Could not parse structured response from On-Demand, using text: {e}")
                response = HeadCouncilResponse(
                    final_verdict="CAUTION",
                    confidence_score=0.6,
                    reasoning=response_text
                )
            
            return response
        
        except Exception as e:
            logger.error(f"Head Council judgment failed: {e}")
            # Fallback response
            return HeadCouncilResponse(
                final_verdict="CAUTION",
                confidence_score=0.5,
                summary="Unable to process council analysis. Please review agent responses.",
                rationale=f"Error in final judgment: {str(e)}",
                key_conflicts="Unable to compute",
                suggested_next_actions="Review individual agent recommendations",
                council_reasoning="Fallback response due to processing error",
            )

    def _format_agent_data(
        self,
        agent_responses: Dict[str, Dict[str, Any]],
        weights: Dict[str, float],
    ) -> str:
        """Format agent responses for the Head Council's review."""
        lines = []
        
        for agent_key, response in agent_responses.items():
            weight = weights.get(agent_key, 0)
            if isinstance(response, dict):
                rec = response.get("recommendation", "N/A")
                conf = response.get("confidence_score", 0)
                reasoning = response.get("reasoning", "")[:100]
            else:
                rec = getattr(response, "recommendation", "N/A")
                conf = getattr(response, "confidence_score", 0)
                reasoning = getattr(response, "reasoning", "")[:100]
            
            lines.append(
                f"- {agent_key.upper()} (weight: {weight:.0%}, confidence: {conf:.0%}): {rec}\n"
                f"  → {reasoning}..."
            )
        
        return "\n".join(lines)

    def _format_conflict_data(self, conflict_matrix: Dict[str, float]) -> str:
        """Format conflict matrix for readability."""
        lines = []
        for pair, conflict in sorted(conflict_matrix.items()):
            agents = pair.split("_")
            status = "HIGH DISAGREEMENT" if conflict > 0.6 else "MODERATE" if conflict > 0.3 else "ALIGNED"
            lines.append(f"  {agents[0]} ↔ {agents[1]}: {conflict:.2f} ({status})")
        
        return "\n".join(lines) if lines else "  (No conflicts computed)"