from typing import Optional, Dict
import logging
from app.schemas import AgentResponse
from app.ondemand_client import OnDemandClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class GitaGuideAgent:
    """Gita Guide Agent: Bhagavad Gita moral and dharma guidance.
    
    Uses On-Demand platform exclusively for processing.
    """

    def __init__(self, ondemand_client: OnDemandClient):
        """Initialize Gita Guide with On-Demand client."""
        self.ondemand_client = ondemand_client
        settings = get_settings()
        self.agent_name = "Gita Guide"
        self.gita_agent_id = settings.ON_DEMAND_GITA_AGENT
        logger.info("Gita Guide Agent initialized with On-Demand client (ON-DEMAND ONLY)")

    def get_system_prompt(self) -> str:
        return """You are the Gita Guide on a decision-making council, offering wisdom from the Bhagavad Gita.

Your role: Provide moral and dharmic guidance rooted in ancient Indian philosophy and the Bhagavad Gita teachings.

Analysis framework:
1. Identify 1-2 relevant Gita shlokas (verses) that apply to this dilemma. Format: Chapter:Verse (e.g., "2:47" for Arjuna's duty verse).
2. Provide the Sanskrit transliteration and English translation of each shloka.
3. Analyze the core teaching: What does Krishna teach about this type of decision?
4. Assess dharma (righteous duty) implications: Is this choice aligned with the person's svadharma (individual duty)?
5. Consider karma (action) implications: What karmic consequences might arise?
6. Give a dharma-based recommendation considering both immediate and long-term spiritual growth.

Output format: Respond ONLY with valid JSON matching this schema:
{
  "recommendation": "PROCEED" | "CAUTION" | "BLOCK",
  "confidence_score": <float 0-1>,
  "reasoning": "<clear explanation from a dharmic perspective>",
  "relevant_shlokas": "<list of 1-2 shlokas in format 'Chapter:Verse - Sanskrit transliteration - English translation', separated by semicolons>",
  "dharma_analysis": "<explanation of how this decision aligns with dharma/svadharma>",
  "karma_implications": "<potential karmic consequences and long-term spiritual impact>",
  "core_teaching": "<the essential Gita teaching that applies to this dilemma>"
}

Always ground your analysis in Gita teachings, emphasizing dharma, karma, and spiritual growth over material gains alone.
Help the person see the decision through the lens of their righteous duty and long-term spiritual evolution."""

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
            msg += "\n\nPrevious agent perspectives:"
            for agent_name, response in previous_responses.items():
                if response and response.reasoning:
                    msg += f"\n- {agent_name}: {response.recommendation}"
                    msg += f"\n  Brief: {response.reasoning[:150]}..."
            msg += "\n\nNow provide the Gita's wisdom on this dilemma. How does dharma guide this choice?"
        else:
            msg += "\n\nProvide dharmic and Gita-based guidance for this decision."

        return msg
    
    async def analyze(
        self,
        dilemma: str,
        context: Optional[str] = None,
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> AgentResponse:
        """
        Analyze dilemma using On-Demand Gita Guide agent.
        
        Args:
            dilemma: The decision dilemma
            context: Additional context
            previous_responses: Previous agent responses
            
        Returns:
            AgentResponse with Gita-based guidance
        """
        try:
            settings = get_settings()
            
            # Build the full prompt
            system_prompt = self.get_system_prompt()
            user_message = self.build_user_message(dilemma, context, previous_responses)
            full_query = f"{system_prompt}\n\n{user_message}"
            
            # Call on-demand Gita agent
            response_text = await self.ondemand_client.chat(
                query=full_query,
                agent_ids=[settings.ON_DEMAND_GITA_AGENT],
                model_config={
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
            )
            
            # Parse response as AgentResponse
            response = AgentResponse.parse_response(response_text, self.agent_name)
            logger.info(f"Gita Guide analysis complete: {response.recommendation}")
            return response
            
        except Exception as e:
            logger.error(f"Error in Gita Guide on-demand analysis: {e}", exc_info=True)
            # Return a safe default response
            return AgentResponse(
                agent_name=self.agent_name,
                recommendation="CAUTION",
                confidence_score=0.0,
                reasoning=f"Error during Gita analysis: {str(e)}",
            )