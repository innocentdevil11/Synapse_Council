import React, { useMemo } from "react";
import Plot from "react-plotly.js";
import { ConflictMatrix, AGENT_NAMES } from "../types.ts";
import "../styles/ConflictHeatmap.css";

interface ConflictHeatmapProps {
  conflictMatrix: ConflictMatrix;
}

export const ConflictHeatmap: React.FC<ConflictHeatmapProps> = ({
  conflictMatrix,
}) => {
  const heatmapData = useMemo(() => {
    const agents = ["risk", "eq", "values", "red_team"];
    const agentLabels = agents.map(
      (a) => AGENT_NAMES[a as keyof typeof AGENT_NAMES]
    );

    // Build symmetric conflict matrix
    const matrix = Array(4)
      .fill(0)
      .map(() => Array(4).fill(0));

    // Diagonal is 0 (no conflict with self)
    matrix[0][0] = 0; // risk-risk
    matrix[1][1] = 0; // eq-eq
    matrix[2][2] = 0; // values-values
    matrix[3][3] = 0; // red_team-red_team

    // Fill in the conflict values (symmetric)
    matrix[0][1] = conflictMatrix.risk_eq;
    matrix[1][0] = conflictMatrix.risk_eq;

    matrix[0][2] = conflictMatrix.risk_values;
    matrix[2][0] = conflictMatrix.risk_values;

    matrix[0][3] = conflictMatrix.risk_red_team;
    matrix[3][0] = conflictMatrix.risk_red_team;

    matrix[1][2] = conflictMatrix.eq_values;
    matrix[2][1] = conflictMatrix.eq_values;

    matrix[1][3] = conflictMatrix.eq_red_team;
    matrix[3][1] = conflictMatrix.eq_red_team;

    matrix[2][3] = conflictMatrix.values_red_team;
    matrix[3][2] = conflictMatrix.values_red_team;

    return {
      z: matrix,
      x: agentLabels,
      y: agentLabels,
      type: "heatmap" as const,
      colorscale: "RdYlGn_r" as const, // Red (conflict) to Green (alignment)
      zmin: 0,
      zmax: 1,
      hovertemplate: "%{y} vs %{x}: %{z:.2f}<extra></extra>",
      colorbar: {
        title: "Conflict",
        tickvals: [0, 0.25, 0.5, 0.75, 1.0],
        ticktext: ["Aligned", "Low", "Medium", "High", "Opposed"],
      },
    };
  }, [conflictMatrix]);

  return (
    <div className="heatmap-container">
      <h3>Agent Conflict Matrix</h3>
      <p className="heatmap-description">
        Green = agents agree | Red = agents disagree
      </p>
      <div className="plot-wrapper">
        <Plot
          data={[heatmapData]}
          layout={{
            title: "Agent Agreement/Disagreement",
            xaxis: { title: "Agent" },
            yaxis: { title: "Agent" },
            width: 600,
            height: 600,
            margin: { l: 150, r: 100, t: 80, b: 150 },
          }}
          config={{ responsive: true }}
        />
      </div>
    </div>
  );
};