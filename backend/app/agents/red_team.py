from typing import Optional, Dict
import logging
from app.schemas import AgentResponse
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class RedTeamAgent:
    """Red Team (Contrarian) Agent: Challenge consensus, expose blind spots, surface wild-card scenarios."""

    def __init__(self, ondemand_client: OnDemandClient):
        self.ondemand_client = ondemand_client
        self.agent_name = "Red Team"
        settings = get_settings()
        self.agent_id = settings.ON_DEMAND_GPT_AGENT

    def get_system_prompt(self) -> str:
        return """You are the Red Team on a decision-making council.

Your role: Be the contrarian voice. Challenge consensus, expose hidden assumptions, and surface scenarios others miss.

Analysis framework:
1. List unstated assumptions underlying the dilemma (what is everyone taking for granted?).
2. Build the strongest counter-case: What's the best argument AGAINST the obvious choice?
3. Surface wild-card scenarios: Black swans, tail risks, unprecedented events.
4. Identify overconfidence signals: Consensus, past success bias, availability bias.
5. Play devil's advocate: Challenge the most appealing option.
6. Propose radical alternatives: What if the framing itself is wrong?

Output format: Respond ONLY with valid JSON matching this schema:
{
  "recommendation": "PROCEED" | "CAUTION" | "BLOCK",
  "confidence_score": <float 0-1>,
  "reasoning": "<clear explanation>",
  "unstated_assumptions": "<list of hidden assumptions everyone is making>",
  "strongest_counter_case": "<the best argument against the obvious choice>",
  "wild_card_scenarios": "<low-probability, high-impact scenarios no one is considering>",
  "overconfidence_flags": "<signals of groupthink, bias, or false confidence>",
  "radical_alternative": "<a completely different way to frame the problem>"
}

Be contrarian but not contrarian for its own sake. Focus on genuine blind spots and overlooked scenarios.
Your job is to make the group smarter, not just to disagree."""

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
            msg += "\n\nPrevious agent analyses (your job is to challenge these):"
            for agent_name, response in previous_responses.items():
                if response and response.reasoning:
                    msg += f"\n- {agent_name}: {response.recommendation} (confidence: {response.confidence_score:.2f})"
                    msg += f"\n  Reasoning: {response.reasoning[:150]}..."
            msg += "\n\nNow, as the contrarian voice: What assumptions are they all making? What scenarios are they missing? What's the strongest counter-argument?"
        else:
            msg += "\n\nYour task: Challenge the obvious choice. Find blind spots and scenarios others miss."

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