// UPDATED: Added mode toggle (Council/Counsellor), API key input, and multimodal support
import React, { useState, useEffect } from "react";
import { DecisionRequest, RecommendationResponse } from "./types.ts";
import { submitDecision, healthCheck } from "./api.ts";
import { DecisionInput } from "./components/DecisionInput.tsx";
import { ResultsPanel } from "./components/ResultsPanel.tsx";
import { LoadingSpinner } from "./components/LoadingSpinner.tsx";
import { CounsellorChat } from "./components/CounsellorChat.tsx";
// @ts-ignore
import "./App.css";

type AppMode = "council" | "counsellor";

interface AppState {
  mode: AppMode;
  result: RecommendationResponse | null;
  isLoading: boolean;
  error: string | null;
  backendOnline: boolean;
  userApiKey: string;
  sessionId: string;
}

function App() {
  const [state, setState] = useState<AppState>({
    mode: "council",
    result: null,
    isLoading: false,
    error: null,
    backendOnline: false,
    userApiKey: "", // No longer needed but kept for backward compat
    sessionId: `session_${Date.now()}`,
  });

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      const isOnline = await healthCheck();
      setState((prev) => ({ ...prev, backendOnline: isOnline }));
      if (!isOnline) {
        setState((prev) => ({
          ...prev,
          error: "⚠️ Backend not available. Make sure the server is running on http://localhost:8000",
        }));
      }
    };
    checkHealth();
  }, []);

  const handleModeChange = (mode: AppMode) => {
    setState((prev) => ({
      ...prev,
      mode,
      result: null,
      error: null,
    }));
  };

  const handleSubmitDecision = async (request: DecisionRequest & { gita_weight?: number; image_summaries?: string[] }) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await submitDecision({
        ...request,
        session_id: state.sessionId,
      });
      setState((prev) => ({ ...prev, result: response, isLoading: false }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred";
      setState((prev) => ({ ...prev, error: message, isLoading: false }));
      console.error("Decision submission error:", err);
    }
  };

  const handleNewDecision = () => {
    setState((prev) => ({ ...prev, result: null, error: null }));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Synapse Council</h1>
          <p className="app-subtitle">Multi-Agent Personal Decision Copilot v2.0</p>
          {state.backendOnline && (
            <div className="backend-status online">✓ Backend Online</div>
          )}
        </div>

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-button ${state.mode === "council" ? "active" : ""}`}
            onClick={() => handleModeChange("council")}
          >
            Council
          </button>
          <button
            className={`mode-button ${state.mode === "counsellor" ? "active" : ""}`}
            onClick={() => handleModeChange("counsellor")}
          >
            Counsellor
          </button>
        </div>
      </header>

      <main className="app-main">
        {state.error && <div className="error-banner">{state.error}</div>}

        {state.mode === "council" ? (
          <>
            {!state.result ? (
              <>
                <DecisionInput
                  onSubmit={handleSubmitDecision}
                  isLoading={state.isLoading}
                />
                {state.isLoading && <LoadingSpinner />}
              </>
            ) : (
              <ResultsPanel result={state.result} onNewDecision={handleNewDecision} />
            )}
          </>
        ) : (
          <CounsellorChat sessionId={state.sessionId} />
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 Synapse Council | Multi-agent decision analysis powered by AI</p>
      </footer>
    </div>
  );
}

export default App;