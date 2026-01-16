from typing import Optional, Dict
import logging
from app.schemas import AgentResponse
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class EQAdvocateAgent:
    """EQ Advocate Agent: Focus on emotional, relational, and social intelligence factors."""

    def __init__(self, ondemand_client: OnDemandClient):
        self.ondemand_client = ondemand_client
        self.agent_name = "EQ Advocate"
        settings = get_settings()
        self.agent_id = settings.ON_DEMAND_GPT_AGENT

    def get_system_prompt(self) -> str:
        return """You are the EQ Advocate on a decision-making council.

Your role: Analyze decisions through the lens of emotional, psychological, relational, and identity impacts.

Analysis framework:
1. Assess burnout and stress risk (workload, autonomy, purpose alignment).
2. Evaluate impact on key relationships (family, friends, colleagues, community).
3. Consider identity alignment: Does this choice strengthen or undermine the person's sense of self?
4. Examine long-term wellbeing and life satisfaction (not just short-term mood).
5. Identify growth potential: Does this challenge them in healthy ways or break them?
6. Flag emotional red flags: desperation, avoidance, external pressure vs. intrinsic motivation.

Output format: Respond ONLY with valid JSON matching this schema:
{
  "recommendation": "PROCEED" | "CAUTION" | "BLOCK",
  "confidence_score": <float 0-1>,
  "reasoning": "<clear explanation>",
  "burnout_risk": "Low" | "Medium" | "High",
  "relationship_impact": "<summary of impact on key relationships>",
  "identity_alignment": "<how well does this align with who they are or want to be>",
  "growth_potential": "<positive learning/development opportunities>",
  "wellbeing_trajectory": "<long-term impact on happiness and fulfillment>"
}

Prioritize long-term psychological health and relational integrity over short-term gains.
Flag decisions driven by external pressure or desperation."""

    def build_user_message(
        self,
        dilemma: str,
        context: Optional[str] = None,
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> str:
        msg = f"Decision dilemma:\n{dilemma}"

        if context:
            msg += f"\n\nAdditional context:\n{context}"

        if previous_responses:
            msg += "\n\nPrevious agent analyses:"
            for agent_name, response in previous_responses.items():
                msg += f"\n- {agent_name}: {response.recommendation} (confidence: {response.confidence_score:.2f})"
                msg += f"\n  Reasoning: {response.reasoning[:200]}..."
            msg += "\n\nReview these perspectives. Do you maintain your assessment or refine it based on new insights?"

        return msg
    
    async def analyze(
        self,
        dilemma: str,
        context: Optional[str] = None,
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> AgentResponse:
        """Analyze using On-Demand client."""
        try:
            system_prompt = self.get_system_prompt()
            user_message = self.build_user_message(dilemma, context, previous_responses)
            full_query = f"{system_prompt}\n\n{user_message}"
            
            # Call On-Demand
            response_text = await self.ondemand_client.chat(
                query=full_query,
                agent_ids=[self.agent_id],
                model_config={
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
            )
            
            # Parse response
            response = AgentResponse.parse_response(response_text, self.agent_name)
            logger.info(f"{self.agent_name} analysis complete: {response.recommendation}")
            return response
            
        except Exception as e:
            logger.error(f"Error in {self.agent_name} analysis: {e}", exc_info=True)
            return AgentResponse(
                recommendation="CAUTION",
                confidence_score=0.0,
                reasoning=f"Error during analysis: {str(e)}",
            )