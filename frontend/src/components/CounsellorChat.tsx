// NEW: Counsellor Chat mode component for session-aware conversation
import React, { useState, useRef, useEffect } from "react";
import { counsellorChat } from "../api.ts";
import "../styles/CounsellorChat.css";

interface ChatMessage {
  role: "user" | "counsellor";
  content: string;
  timestamp: string;
}

interface CounsellorChatProps {
  sessionId: string;
}

export const CounsellorChat: React.FC<CounsellorChatProps> = ({
  sessionId,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [memorySummary, setMemorySummary] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setError(null);

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);

    setIsLoading(true);

    try {
      const response = await counsellorChat(sessionId, userMessage);

      // Add counsellor reply
      setMessages((prev) => [
        ...prev,
        {
          role: "counsellor",
          content: response.reply,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);

      setMemorySummary(response.memory_summary);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to get counsellor response";
      setError(message);
      console.error("Counsellor chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="counsellor-chat-container">
      <div className="chat-layout">
        {/* Chat Panel */}
        <div className="chat-panel">
          <div className="chat-header">
            <h2>🙏 Synapse Counsellor</h2>
            <p className="chat-subtitle">Session-aware guidance for your decisions</p>
          </div>

          {error && <div className="error-banner">{error}</div>}

          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <h3>Welcome to Synapse Counsellor</h3>
                <p>Share a decision you're facing, or ask about previous decisions in this session.</p>
                <p>The Counsellor remembers your past dilemmas and helps you grow through each decision.</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message message-${msg.role}`}>
                  <div className="message-header">
                    {msg.role === "user" ? "You" : "Counsellor"}
                    <span className="message-time">{msg.timestamp}</span>
                  </div>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="message message-counsellor loading">
                <div className="message-header">Counsellor</div>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Share a dilemma or ask a question..."
              disabled={isLoading}
              className="chat-input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="send-button"
            >
              Send
            </button>
          </form>
        </div>

        {/* Memory Sidebar */}
        <div className="memory-sidebar">
          <h3>Session History</h3>
          <div className="memory-content">
            {memorySummary ? (
              <pre>{memorySummary}</pre>
            ) : (
              <p className="empty-memory">No decisions logged yet in this session.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};