import json
import logging
from typing import Type, TypeVar
import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaClient:
    """Wrapper around Ollama API (free, local LLM)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "neural-chat",
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def call_with_schema(
        self,
        system_prompt: str,
        user_message: str,
        response_model: Type[T],
    ) -> T:
        """
        Call Ollama with JSON output enforcement via prompting.
        Returns a parsed Pydantic model instance.
        """
        try:
            # Build JSON schema from Pydantic model
            schema = response_model.model_json_schema()
            schema_str = json.dumps(schema, indent=2)

            # Create a prompt that enforces JSON output
            full_prompt = f"""{system_prompt}

You MUST respond ONLY with valid JSON matching this schema:
```json
{schema_str}
```

User message: {user_message}

Remember: Respond ONLY with the JSON object, no additional text."""

            # Call Ollama API (correct endpoint)
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} {response.text}")
                raise ValueError(f"Ollama API error: {response.status_code}")

            response_data = response.json()
            response_text = response_data.get("response", "").strip()

            if not response_text:
                raise ValueError("Empty response from Ollama")

            # Try to parse JSON from response
            # Handle cases where Ollama wraps JSON in markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            data = json.loads(json_str)
            
            # Clean up data: convert lists to comma-separated strings for fields that expect strings
            string_fields = [
                'unstated_assumptions', 'strongest_counter_case', 'wild_card_scenarios',
                'overconfidence_flags', 'radical_alternative', 'reasoning',
                'risk_level', 'burnout_risk', 'stakeholder_impact', 'relationship_impact',
                'identity_alignment', 'growth_potential', 'wellbeing_trajectory',
                'ethical_concerns', 'integrity_risk', 'second_order_effects',
                'long_term_regret_likelihood', 'worst_case_scenario', 'failure_probability',
                'financial_impact'
            ]
            
            for field in string_fields:
                if field in data and isinstance(data[field], list):
                    # Convert list to comma-separated string
                    data[field] = ", ".join(str(item) for item in data[field])
            
            return response_model(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama response: {response_text}")
            raise ValueError(f"Invalid JSON in LLM response: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama. Make sure it's running on {self.base_url}")
            raise ValueError(
                f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running."
            )
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}", exc_info=True)
            raise

    async def call_plain(self, system_prompt: str, user_message: str) -> str:
        """
        Call Ollama without structured output. Returns raw string response.
        """
        try:
            full_prompt = f"{system_prompt}\n\nUser message: {user_message}"

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code}")
                raise ValueError(f"Ollama API error: {response.status_code}")

            response_data = response.json()
            return response_data.get("response", "").strip()

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ValueError(
                f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running."
            )
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}", exc_info=True)
            raise