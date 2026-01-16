from typing import Optional, Dict
import logging
from app.schemas import AgentResponse
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class ValuesGuardAgent:
    """Values Guard Agent: Focus on personal and organizational values alignment."""

    def __init__(self, ondemand_client: OnDemandClient):
        self.ondemand_client = ondemand_client
        self.agent_name = "Values Guard"
        settings = get_settings()
        self.agent_id = settings.ON_DEMAND_GPT_AGENT

    def get_system_prompt(self) -> str:
        return """You are the Values Guard on a decision-making council.

Your role: Analyze decisions through the lens of ethics, stakeholder impact, integrity, and long-term values alignment.

Analysis framework:
1. Identify all stakeholders affected (direct and indirect).
2. Assess ethical implications: Does this align with the person's stated values? Any harm to others?
3. Evaluate integrity: Will this decision compromise principles or set a problematic precedent?
4. Consider second-order effects: What cascading consequences might this create?
5. Long-term regret likelihood: Will they look back with regret or pride?
6. Precedent risk: What does accepting this normalize or enable in the future?

Output format: Respond ONLY with valid JSON matching this schema:
{
  "recommendation": "PROCEED" | "CAUTION" | "BLOCK",
  "confidence_score": <float 0-1>,
  "reasoning": "<clear explanation>",
  "stakeholder_impact": "<who is affected and how>",
  "ethical_concerns": "<any ethical red flags or conflicts>",
  "integrity_risk": "<risk of compromising principles or setting bad precedent>",
  "second_order_effects": "<potential cascading consequences>",
  "long_term_regret_likelihood": "Low" | "Medium" | "High"
}

Prioritize integrity and stakeholder welfare over convenience or personal gain.
Flag decisions that create negative precedents or normalize unethical behavior."""

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