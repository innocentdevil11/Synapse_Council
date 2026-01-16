# from abc import ABC, abstractmethod
# from typing import Optional, Dict, Any
# from pydantic import BaseModel
# from app.schemas import AgentResponse
# from app.llm_client import LLMClient


# class Agent(ABC):
#     """Abstract base class for council agents."""

#     def __init__(self, llm_client: LLMClient, agent_name: str):
#         self.llm_client = llm_client
#         self.agent_name = agent_name

#     @abstractmethod
#     def get_system_prompt(self) -> str:
#         """Return the role-specific system prompt."""
#         pass

#     @abstractmethod
#     def build_user_message(
#         self,
#         dilemma: str,
#         context: Optional[str] = None,
#         previous_responses: Optional[Dict[str, AgentResponse]] = None,
#     ) -> str:
#         """Build the user message, optionally including previous debate context."""
#         pass

#     async def analyze(
#         self,
#         dilemma: str,
#         context: Optional[str] = None,
#         previous_responses: Optional[Dict[str, AgentResponse]] = None,
#     ) -> AgentResponse:
#         """
#         Analyze the dilemma and return a structured recommendation.
#         """
#         system_prompt = self.get_system_prompt()
#         user_message = self.build_user_message(dilemma, context, previous_responses)

#         response = await self.llm_client.call_with_schema(
#             system_prompt=system_prompt,
#             user_message=user_message,
#             response_model=AgentResponse,
#         )

#         return response

#comet
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel

# FIXED IMPORTS
from ..schemas import AgentResponse
from ..llm_client import LLMClient


class Agent(ABC):
    """Abstract base class for council agents."""

    def __init__(self, llm_client: LLMClient, agent_name: str):
        self.llm_client = llm_client
        self.agent_name = agent_name

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the role-specific system prompt."""
        pass

    @abstractmethod
    def build_user_message(
        self,
        dilemma: str,
        context: Optional[str] = None,
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> str:
        """Build the user message, optionally including previous debate context."""
        pass

    async def analyze(
        self,
        dilemma: str,
        context: Optional[str] = None,
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> AgentResponse:
        """
        Analyze the dilemma and return a structured recommendation.
        """
        system_prompt = self.get_system_prompt()
        user_message = self.build_user_message(dilemma, context, previous_responses)

        response = await self.llm_client.call_with_schema(
            system_prompt=system_prompt,
            user_message=user_message,
            response_model=AgentResponse,
        )

        return response
