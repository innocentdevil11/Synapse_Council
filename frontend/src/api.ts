/**
 * UPDATED: HTTP client for Synapse Council v2.0 with on-demand API keys.
 * Centralized API calls with error handling and type safety.
 */

import {
  DecisionRequest,
  RecommendationResponse,
  ApiError,
} from "./types";

// Get API base URL from environment or default
const API_BASE_URL = 
  (typeof window !== 'undefined' && (window as any).REACT_APP_API_URL) ||
  "http://localhost:8000";

/**
 * Parse API error response
 */
function parseApiError(response: Response, data: unknown): ApiError {
  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {
    return {
      detail: (data as Record<string, unknown>).detail as string,
      status_code: response.status,
    };
  }
  return {
    detail: `HTTP ${response.status}: ${response.statusText}`,
    status_code: response.status,
  };
}

/**
 * Main API call: Submit a decision dilemma to the council
 */
export async function submitDecision(
  request: DecisionRequest & { user_api_key?: string; session_id?: string }
): Promise<RecommendationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/decide`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    const data = await response.json();

    if (!response.ok) {
      const error = parseApiError(response, data);
      throw new Error(error.detail);
    }

    return data as RecommendationResponse;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to submit decision: ${error.message}`);
    }
    throw new Error("Failed to submit decision: Unknown error");
  }
}

/**
 * Transcribe audio file to text
 */
export async function transcribeAudio(
  file: File
): Promise<{ transcript: string }> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      const error = parseApiError(response, data);
      throw new Error(error.detail);
    }

    return data as { transcript: string };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to transcribe audio: ${error.message}`);
    }
    throw new Error("Failed to transcribe audio: Unknown error");
  }
}

/**
 * Upload and analyze an image
 */
export async function uploadImage(
  file: File,
  context?: string
): Promise<{ image_url: string; vision_summary: string }> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (context) {
      formData.append("context", context);
    }

    const response = await fetch(`${API_BASE_URL}/api/upload-image`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      const error = parseApiError(response, data);
      throw new Error(error.detail);
    }

    return data as { image_url: string; vision_summary: string };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to upload image: ${error.message}`);
    }
    throw new Error("Failed to upload image: Unknown error");
  }
}

/**
 * Chat with the counsellor in session-aware mode
 */
export async function counsellorChat(
  sessionId: string,
  message: string
): Promise<{ reply: string; memory_summary: string; session_id: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/counsellor/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const error = parseApiError(response, data);
      throw new Error(error.detail);
    }

    return data as { reply: string; memory_summary: string; session_id: string };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to chat with counsellor: ${error.message}`);
    }
    throw new Error("Failed to chat with counsellor: Unknown error");
  }
}

/**
 * Health check: Verify backend is running
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Helper to set API base URL dynamically
 */
export function setApiBaseUrl(url: string): void {
  Object.defineProperty(window, "API_BASE_URL", {
    value: url,
    writable: true,
  });
}