import React, { useState } from "react";
import { AgentResponse, AGENT_NAMES, AGENT_COLORS } from "../types.ts";
import "../styles/AgentCard.css";

interface AgentCardProps {
  agentKey: string;
  response: AgentResponse;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agentKey, response }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const agentName =
    AGENT_NAMES[agentKey as keyof typeof AGENT_NAMES] || agentKey;
  const agentColor =
    AGENT_COLORS[agentKey as keyof typeof AGENT_COLORS] || "#666";

  const getRecommendationClass = (rec: string) => {
    if (rec === "PROCEED") return "rec-proceed";
    if (rec === "BLOCK") return "rec-block";
    return "rec-caution";
  };

  const getRecommendationIcon = (rec: string) => {
    if (rec === "PROCEED") return "✓";
    if (rec === "BLOCK") return "✕";
    return "⚠";
  };

  return (
    <div className="agent-card" style={{ borderLeftColor: agentColor }}>
      <div className="card-header">
        <div className="agent-info">
          <h3 className="agent-name">{agentName}</h3>
          <div
            className={`recommendation ${getRecommendationClass(
              response.recommendation
            )}`}
          >
            <span className="rec-icon">
              {getRecommendationIcon(response.recommendation)}
            </span>
            <span className="rec-text">{response.recommendation}</span>
          </div>
        </div>
        <div className="confidence">
          <div className="confidence-label">Confidence</div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${response.confidence_score * 100}%`,
                backgroundColor: agentColor,
              }}
            />
          </div>
          <div className="confidence-value">
            {Math.round(response.confidence_score * 100)}%
          </div>
        </div>
      </div>

      <div className="card-body">
        <p className="reasoning">{response.reasoning}</p>

        {!isExpanded && (
          <button
            className="expand-button"
            onClick={() => setIsExpanded(true)}
          >
            View Details
          </button>
        )}

        {isExpanded && (
          <div className="details">
            <div className="details-grid">
              {response.risk_level && (
                <div className="detail-item">
                  <div className="detail-label">Risk Level</div>
                  <div className="detail-value">{response.risk_level}</div>
                </div>
              )}
              {response.burnout_risk && (
                <div className="detail-item">
                  <div className="detail-label">Burnout Risk</div>
                  <div className="detail-value">{response.burnout_risk}</div>
                </div>
              )}
              {response.relationship_impact && (
                <div className="detail-item">
                  <div className="detail-label">Relationship Impact</div>
                  <div className="detail-value">
                    {response.relationship_impact}
                  </div>
                </div>
              )}
              {response.identity_alignment && (
                <div className="detail-item">
                  <div className="detail-label">Identity Alignment</div>
                  <div className="detail-value">
                    {response.identity_alignment}
                  </div>
                </div>
              )}
              {response.ethical_concerns && (
                <div className="detail-item">
                  <div className="detail-label">Ethical Concerns</div>
                  <div className="detail-value">{response.ethical_concerns}</div>
                </div>
              )}
              {response.stakeholder_impact && (
                <div className="detail-item">
                  <div className="detail-label">Stakeholder Impact</div>
                  <div className="detail-value">
                    {response.stakeholder_impact}
                  </div>
                </div>
              )}
              {response.unstated_assumptions && (
                <div className="detail-item">
                  <div className="detail-label">Unstated Assumptions</div>
                  <div className="detail-value">
                    {response.unstated_assumptions}
                  </div>
                </div>
              )}
              {response.wild_card_scenarios && (
                <div className="detail-item">
                  <div className="detail-label">Wild Card Scenarios</div>
                  <div className="detail-value">
                    {response.wild_card_scenarios}
                  </div>
                </div>
              )}
            </div>

            <button
              className="collapse-button"
              onClick={() => setIsExpanded(false)}
            >
              Hide Details
            </button>
          </div>
        )}
      </div>
    </div>
  );
};