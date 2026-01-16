import React from "react";
import { RecommendationResponse, AGENT_NAMES } from "../types.ts";
import { ConflictHeatmap } from "./ConflictHeatmap.tsx";
import { AgentCard } from "./AgentCard.tsx";
import "../styles/ResultsPanel.css";

interface ResultsPanelProps {
  result: RecommendationResponse;
  onNewDecision: () => void;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({
  result,
  onNewDecision,
}) => {
  const getRecommendationClass = (rec: string) => {
    if (rec.startsWith("PROCEED")) return "rec-proceed";
    if (rec.startsWith("BLOCK")) return "rec-block";
    return "rec-caution";
  };

  const agentOrder = ["risk", "eq", "values", "red_team"];

  return (
    <div className="results-panel">
      <div className="results-header">
        <div
          className={`recommendation-box ${getRecommendationClass(
            result.recommendation
          )}`}
        >
          <h2 className="recommendation-text">{result.recommendation}</h2>
          <div className="confidence-display">
            <span className="confidence-label">Confidence:</span>
            <span className="confidence-score">
              {Math.round(result.confidence_score * 100)}%
            </span>
          </div>
        </div>

        <div className="execution-info">
          <p>
            <strong>Debate Rounds:</strong> {result.debate_rounds}
          </p>
          <p>
            <strong>Execution Time:</strong>{" "}
            {Math.round(result.execution_time_ms)}ms
          </p>
        </div>
      </div>

      <div className="heatmap-section">
        <ConflictHeatmap conflictMatrix={result.conflict_heatmap} />
      </div>

      <div className="agents-section">
        <h3 className="agents-title">Agent Analyses</h3>
        <div className="agents-grid">
          {agentOrder.map((agentKey) => (
            <AgentCard
              key={agentKey}
              agentKey={agentKey}
              response={result.agent_responses[agentKey]}
            />
          ))}
        </div>
      </div>

      <div className="audit-section">
        <details className="audit-details">
          <summary className="audit-summary">View Audit Trail</summary>
          <div className="audit-content">
            {result.audit_trail.map((entry, idx) => (
              <div key={idx} className="audit-entry">
                <h4>Round {entry.round}</h4>
                <div className="audit-responses">
                  {Object.entries(entry.responses).map(([agentKey, response]) => (
                    <div key={agentKey} className="audit-response">
                      <span className="audit-agent">
                        {
                          AGENT_NAMES[
                            agentKey as keyof typeof AGENT_NAMES
                          ]
                        }
                      </span>
                      <span className={`audit-rec audit-${response.recommendation.toLowerCase()}`}>
                        {response.recommendation}
                      </span>
                      <span className="audit-confidence">
                        ({Math.round(response.confidence_score * 100)}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </details>
      </div>

      <button className="new-decision-button" onClick={onNewDecision}>
        Analyze Another Decision
      </button>
    </div>
  );
};