// UPDATED: Added voice transcription, image upload, and Gita weight slider
import React, { useState } from "react";
import { DecisionRequest, DecisionWeights, AGENT_NAMES } from "../types.ts";
import { transcribeAudio, uploadImage } from "../api.ts";
import "../styles/DecisionInput.css";

interface DecisionInputProps {
  onSubmit: (request: DecisionRequest & { gita_weight?: number; image_summaries?: string[] }) => void;
  isLoading: boolean;
}

export const DecisionInput: React.FC<DecisionInputProps> = ({
  onSubmit,
  isLoading,
}) => {
  const [dilemma, setDilemma] = useState("");
  const [context, setContext] = useState("");
  const [weights, setWeights] = useState<DecisionWeights>({
    risk: 40,
    eq: 20,
    values: 30,
    red_team: 10,
  });
  const [gitaWeight, setGitaWeight] = useState(0);
  const [imageSummaries, setImageSummaries] = useState<string[]>([]);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleWeightChange = (agent: keyof DecisionWeights, value: number) => {
    setWeights((prev) => ({
      ...prev,
      [agent]: value,
    }));
  };

  const handleVoiceUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;

    setUploadError(null);
    const file = e.target.files[0];

    try {
      const { transcript } = await transcribeAudio(file);
      setDilemma((prev) => (prev ? `${prev}\n\n[Transcribed: ${transcript}]` : transcript));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to transcribe audio";
      setUploadError(message);
      console.error("Transcription error:", err);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;

    setUploadError(null);
    const file = e.target.files[0];

    try {
      const { vision_summary } = await uploadImage(
        file,
        "Decision context"
      );
      setImageSummaries((prev) => [...prev, vision_summary]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to analyze image";
      setUploadError(message);
      console.error("Image upload error:", err);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!dilemma.trim()) {
      alert("Please enter a decision dilemma");
      return;
    }

    // Normalize weights
    const total = weights.risk + weights.eq + weights.values + weights.red_team;
    const normalizedWeights: DecisionWeights = {
      risk: weights.risk / total,
      eq: weights.eq / total,
      values: weights.values / total,
      red_team: weights.red_team / total,
    };

    onSubmit({
      dilemma: dilemma.trim(),
      context: context.trim() || undefined,
      weights: normalizedWeights,
      gita_weight: gitaWeight > 0 ? gitaWeight / 100 : 0,
      image_summaries: imageSummaries.length > 0 ? imageSummaries : undefined,
    });
  };

  const agentWeights = [
    { key: "risk" as const, label: AGENT_NAMES.risk },
    { key: "eq" as const, label: AGENT_NAMES.eq },
    { key: "values" as const, label: AGENT_NAMES.values },
    { key: "red_team" as const, label: AGENT_NAMES.red_team },
  ];

  return (
    <div className="decision-input-container">
      <div className="input-panel">
        <h2>Submit Your Dilemma</h2>

        {uploadError && <div className="error-message">{uploadError}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="dilemma">Decision Dilemma *</label>
            <textarea
              id="dilemma"
              value={dilemma}
              onChange={(e) => setDilemma(e.target.value)}
              placeholder="Describe your decision dilemma in detail. What are you trying to decide?"
              rows={5}
              disabled={isLoading}
            />
            <div className="input-helpers">
              <label className="file-input-label">
                🎤 Record Voice
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleVoiceUpload}
                  disabled={isLoading}
                  style={{ display: "none" }}
                />
              </label>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="context">Additional Context (Optional)</label>
            <textarea
              id="context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Any additional information that might be relevant?"
              rows={3}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label>📸 Upload Context Images</label>
            <div className="image-uploads">
              {imageSummaries.map((summary, i) => (
                <div key={i} className="image-summary">
                  <p>{summary.substring(0, 100)}...</p>
                  <button
                    type="button"
                    onClick={() =>
                      setImageSummaries((prev) => prev.filter((_, idx) => idx !== i))
                    }
                    className="remove-image"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <label className="file-input-label">
                📷 Upload Image
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isLoading}
                  style={{ display: "none" }}
                />
              </label>
            </div>
          </div>

          <div className="weights-section">
            <h3>Agent Weights</h3>
            <p className="weights-hint">
              Adjust how much each agent influences the final recommendation.
            </p>

            {agentWeights.map(({ key, label }) => (
              <div key={key} className="weight-control">
                <div className="weight-label-row">
                  <label>{label}</label>
                  <span className="weight-value">
                    {Math.round(
                      (weights[key] / (weights.risk + weights.eq + weights.values + weights.red_team)) * 100
                    )}
                    %
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights[key]}
                  onChange={(e) => handleWeightChange(key, parseInt(e.target.value))}
                  disabled={isLoading}
                  className="weight-slider"
                />
              </div>
            ))}

            {/* Gita Weight Slider */}
            <div className="weight-control gita-weight">
              <div className="weight-label-row">
                <label>🙏 Gita Guide (Optional)</label>
                <span className="weight-value">{gitaWeight}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="50"
                value={gitaWeight}
                onChange={(e) => setGitaWeight(parseInt(e.target.value))}
                disabled={isLoading}
                className="weight-slider gita-slider"
              />
              <small>Add dharmic wisdom from the Bhagavad Gita to your decision</small>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !dilemma.trim()}
            className="submit-button"
          >
            {isLoading ? "Council Debating..." : "Start Council Debate"}
          </button>
        </form>
      </div>
    </div>
  );
};