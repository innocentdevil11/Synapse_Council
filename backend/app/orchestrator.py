# UPDATED: On-Demand only - all agents use On-Demand platform
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from app.config import get_settings
from app.ondemand_client import OnDemandClient
from app.schemas import (
    DecisionWeights,
    AgentResponse,
    ConflictMatrix,
    AuditEntry,
    RecommendationResponse,
)
from app.agents.risk_logic import RiskLogicAgent
from app.agents.eq_advocate import EQAdvocateAgent
from app.agents.values_guard import ValuesGuardAgent
from app.agents.red_team import RedTeamAgent
from app.agents.gita_guide import GitaGuideAgent
from app.agents.head_council import HeadCouncil, HeadCouncilResponse

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the multi-agent debate using On-Demand platform for all agents."""

    def __init__(
        self,
        conflict_threshold: float = 0.2,
        max_debate_rounds: int = 2,
    ):
        settings = get_settings()
        
        if not settings.ON_DEMAND_API_KEY:
            raise ValueError("ON_DEMAND_API_KEY is required - On-Demand only mode")
        
        # Initialize On-Demand client for all agents
        self.ondemand_client = OnDemandClient(api_key=settings.ON_DEMAND_API_KEY)
        self.conflict_threshold = conflict_threshold
        self.max_debate_rounds = max_debate_rounds

        # Initialize base agents with On-Demand client
        self.base_agents = {
            "risk": RiskLogicAgent(self.ondemand_client),
            "eq": EQAdvocateAgent(self.ondemand_client),
            "values": ValuesGuardAgent(self.ondemand_client),
            "red_team": RedTeamAgent(self.ondemand_client),
        }
        
        # Gita agent with On-Demand client
        self.gita_agent = GitaGuideAgent(self.ondemand_client)
        
        # Head Council with On-Demand client
        self.head_council = HeadCouncil(self.ondemand_client)

    async def run(
        self,
        dilemma: str,
        context: str = None,
        weights: DecisionWeights = None,
        gita_weight: float = 0.0,
    ) -> RecommendationResponse:
        """
        Run the full decision council process with optional Gita agent and Head Council final verdict.
        
        Args:
            dilemma: The decision dilemma
            context: Additional context
            weights: Weights for base 4 agents
            gita_weight: Weight for Gita agent (0 = disabled, >0 = enabled)
            
        Returns:
            RecommendationResponse with Head Council verdict and underlying agent data
        """
        if weights is None:
            weights = DecisionWeights()

        # Determine which agents to use
        active_agents = dict(self.base_agents)
        extended_weights = weights.to_dict()
        
        if gita_weight > 0:
            active_agents["gita"] = self.gita_agent
            extended_weights["gita"] = gita_weight
            # Normalize all weights
            total_weight = sum(extended_weights.values())
            extended_weights = {k: v / total_weight for k, v in extended_weights.items()}
        
        audit_trail: List[AuditEntry] = []
        current_responses: Dict[str, AgentResponse] = {}
        debate_round = 0
        avg_conflict = 1.0

        # ===== ROUND 0: Initial analysis =====
        logger.info(f"Starting Round 0: Initial agent analysis with {len(active_agents)} agents")
        round_0_responses = await self._run_round(
            dilemma=dilemma,
            context=context,
            agents=active_agents,
            previous_responses=None,
        )
        current_responses = round_0_responses
        debate_round = 0

        # Compute conflict matrix (only for base agents, not Gita)
        base_agent_keys = ["risk", "eq", "values", "red_team"]
        base_responses = {k: v for k, v in current_responses.items() if k in base_agent_keys}
        
        conflict_matrix = await self._compute_conflict_matrix(
            dilemma, base_responses
        )
        avg_conflict = conflict_matrix.average()
        audit_trail.append(
            AuditEntry(round=0, responses=current_responses, conflict_matrix=conflict_matrix)
        )
        logger.info(f"Round 0 complete. Average conflict: {avg_conflict:.2f}")

        # ===== DEBATE ROUNDS =====
        while (
            avg_conflict > self.conflict_threshold
            and debate_round < self.max_debate_rounds
        ):
            debate_round += 1
            logger.info(
                f"Starting Round {debate_round}: Debate (avg conflict: {avg_conflict:.2f})"
            )

            round_responses = await self._run_round(
                dilemma=dilemma,
                context=context,
                agents=active_agents,
                previous_responses=current_responses,
            )
            current_responses = round_responses

            conflict_matrix = await self._compute_conflict_matrix(
                dilemma, base_responses
            )
            avg_conflict = conflict_matrix.average()
            audit_trail.append(
                AuditEntry(
                    round=debate_round,
                    responses=current_responses,
                    conflict_matrix=conflict_matrix,
                )
            )
            logger.info(
                f"Round {debate_round} complete. Average conflict: {avg_conflict:.2f}"
            )

        # ===== NUMERIC AGGREGATION =====
        numeric_score, base_confidence = self._synthesize_numeric_recommendation(
            {k: v for k, v in current_responses.items() if k in base_agent_keys},
            weights,
        )

        # ===== HEAD COUNCIL FINAL VERDICT =====
        logger.info("Calling Head Council for final verdict")
        
        # Convert responses to dicts for Head Council
        agent_responses_dict = {}
        for agent_key, response in current_responses.items():
            agent_responses_dict[agent_key] = response.model_dump() if hasattr(response, 'model_dump') else response

        head_council_verdict = await self.head_council.judge(
            dilemma=dilemma,
            agent_responses=agent_responses_dict,
            weights=extended_weights,
            conflict_matrix={
                "risk_eq": conflict_matrix.risk_eq,
                "risk_values": conflict_matrix.risk_values,
                "risk_red_team": conflict_matrix.risk_red_team,
                "eq_values": conflict_matrix.eq_values,
                "eq_red_team": conflict_matrix.eq_red_team,
                "values_red_team": conflict_matrix.values_red_team,
            },
            numeric_score=numeric_score,
        )

        logger.info(f"Head Council verdict: {head_council_verdict.final_verdict}")

        # Convert agent responses to dicts for response
        agent_responses_dict = {}
        for agent_key, response in current_responses.items():
            agent_responses_dict[agent_key] = response.model_dump() if hasattr(response, 'model_dump') else response

        # ===== BUILD RESPONSE =====
        return RecommendationResponse(
            recommendation=f"{head_council_verdict.final_verdict} ({head_council_verdict.summary.split(chr(10))[0]})",
            confidence_score=head_council_verdict.confidence_score,
            conflict_heatmap=conflict_matrix,
            agent_responses=agent_responses_dict,
            debate_rounds=debate_round,
            audit_trail=audit_trail,
            execution_time_ms=0.0,  # Set by main.py
            head_council_verdict=head_council_verdict.model_dump() if hasattr(head_council_verdict, 'model_dump') else head_council_verdict,
            numeric_score=numeric_score,
            numeric_confidence=base_confidence,
        )

    async def _run_round(
        self,
        dilemma: str,
        context: str,
        agents: Dict[str, any],
        previous_responses: Optional[Dict[str, AgentResponse]] = None,
    ) -> Dict[str, AgentResponse]:
        """Run all active agents in parallel for a single round."""
        tasks = []
        agent_names = []

        for agent_key, agent in agents.items():
            tasks.append(
                agent.analyze(
                    dilemma=dilemma,
                    context=context,
                    previous_responses=previous_responses,
                )
            )
            agent_names.append(agent_key)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        result = {}
        for agent_key, response in zip(agent_names, responses):
            if isinstance(response, Exception):
                logger.error(f"Agent {agent_key} failed: {response}")
                result[agent_key] = AgentResponse(
                    recommendation="CAUTION",
                    confidence_score=0.0,
                    reasoning=f"Agent error: {str(response)}",
                )
            else:
                result[agent_key] = response

        return result

    async def _compute_conflict_matrix(
        self,
        dilemma: str,
        responses: Dict[str, AgentResponse],
    ) -> ConflictMatrix:
        """Compute semantic conflict between base agent pairs."""
        agent_keys = list(responses.keys())
        pairs = [
            (agent_keys[i], agent_keys[j])
            for i in range(len(agent_keys))
            for j in range(i + 1, len(agent_keys))
        ]

        conflict_tasks = [
            self._compute_pair_conflict(dilemma, responses[a], responses[b])
            for a, b in pairs
        ]
        conflict_scores = await asyncio.gather(*conflict_tasks)

        conflict_map = {f"{a}_{b}": 1 - score for (a, b), score in zip(pairs, conflict_scores)}

        return ConflictMatrix(
            risk_eq=conflict_map.get("risk_eq", 0.5),
            risk_values=conflict_map.get("risk_values", 0.5),
            risk_red_team=conflict_map.get("risk_red_team", 0.5),
            eq_values=conflict_map.get("eq_values", 0.5),
            eq_red_team=conflict_map.get("eq_red_team", 0.5),
            values_red_team=conflict_map.get("values_red_team", 0.5),
        )

    async def _compute_pair_conflict(
        self,
        dilemma: str,
        response_a: AgentResponse,
        response_b: AgentResponse,
    ) -> float:
        """Use LLM to assess agreement between two agent responses."""
        prompt = f"""Given these two agent analyses, rate their agreement on a 0-1 scale.
0 = completely opposed
1 = fully aligned

Agent A recommendation: {response_a.recommendation}
Agent A reasoning: {response_a.reasoning[:300]}

Agent B recommendation: {response_b.recommendation}
Agent B reasoning: {response_b.reasoning[:300]}

Respond with a single float value (e.g., 0.75), nothing else."""

        try:
            result = await self.llm_client.call_plain(
                system_prompt="You are an expert at assessing semantic agreement between two positions.",
                user_message=prompt,
            )
            similarity = float(result.strip())
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error computing pair conflict: {e}")
            return 0.5

    def _synthesize_numeric_recommendation(
        self,
        responses: Dict[str, AgentResponse],
        weights: DecisionWeights,
    ) -> Tuple[float, float]:
        """
        Compute numeric weighted score and confidence (for reference/UI).
        Head Council verdict is the primary decision output.
        """
        rec_scores = {
            "PROCEED": 1.0,
            "CAUTION": 0.5,
            "BLOCK": 0.0,
        }

        weight_dict = weights.to_dict()
        weighted_score = 0.0
        total_confidence = 0.0
        
        for agent_key, response in responses.items():
            if agent_key in weight_dict:
                weight = weight_dict[agent_key]
                rec_score = rec_scores.get(response.recommendation, 0.5)
                confidence = max(0.3, response.confidence_score)
                
                weighted_score += weight * rec_score * confidence
                total_confidence += confidence

        if total_confidence > 0:
            weighted_score = weighted_score / total_confidence

        # Confidence based on distance from neutral
        distance_from_neutral = abs(weighted_score - 0.5) * 2
        confidence = max(0.4, min(1.0, distance_from_neutral * 0.8 + 0.2))

        return weighted_score, confidence