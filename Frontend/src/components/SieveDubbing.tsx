import React, { useState, useEffect } from "react";
import { Button, Spinner, Select } from "../ui";

// Define options for the language dropdown
const LANGUAGE_OPTIONS = [
  { value: "spanish", label: "Spanish" },
  { value: "french", label: "French" },
  { value: "german", label: "German" },
  { value: "italian", label: "Italian" },
  { value: "portuguese", label: "Portuguese" },
  { value: "hindi", label: "Hindi" },
  { value: "japanese", label: "Japanese" },
  { value: "korean", label: "Korean" },
  { value: "chinese", label: "Chinese" },
  { value: "arabic", label: "Arabic" },
  { value: "russian", label: "Russian" },
];

// Define options for the voice engine dropdown
const VOICE_ENGINE_OPTIONS = [
  { value: "elevenlabs (voice cloning)", label: "ElevenLabs (Voice Cloning)" },
  { value: "openai-alloy (no voice cloning)", label: "OpenAI Alloy" },
  { value: "openai-echo (no voice cloning)", label: "OpenAI Echo" },
  { value: "openai-onyx (no voice cloning)", label: "OpenAI Onyx" },
  { value: "openai-nova (no voice cloning)", label: "OpenAI Nova" },
  { value: "openai-shimmer (no voice cloning)", label: "OpenAI Shimmer" },
];

interface SieveDubbingProps {
  jobId: string;
  segmentId: string;
  onDubbingComplete: (videoUrl: string, language: string) => void;
}

const SieveDubbing: React.FC<SieveDubbingProps> = ({
  jobId,
  segmentId,
  onDubbingComplete,
}) => {
  const [language, setLanguage] = useState("spanish");
  const [voiceEngine, setVoiceEngine] = useState("elevenlabs (voice cloning)");
  const [enableLipSync, setEnableLipSync] = useState(true);
  const [dubbingId, setDubbingId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  // Function to submit dubbing job
  const handleSubmitDubbing = async () => {
    setError(null);
    setIsProcessing(true);
    setStatusMessage("Submitting dubbing job...");

    try {
      // Submit the dubbing job
      const response = await fetch("/api/sieve-dub", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jobId,
          segmentId,
          language,
          voiceEngine,
          enableLipsyncing: enableLipSync,
          preserveBackgroundAudio: true,
          apiKey: apiKey || undefined,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to submit dubbing job");
      }

      console.log("Dubbing job submitted:", data);
      setDubbingId(data.dubbingId);
      setStatusMessage("Dubbing job submitted successfully. Processing...");

      // Start polling for status
      pollStatus(data.dubbingId);
    } catch (err) {
      console.error("Error submitting dubbing job:", err);
      setError(
        err instanceof Error ? err.message : "Failed to submit dubbing job"
      );
      setIsProcessing(false);
    }
  };

  // Function to poll dubbing job status
  const pollStatus = async (id: string) => {
    try {
      const response = await fetch(`/api/sieve-dub-status/${id}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to check dubbing status");
      }

      if (data.status === "completed") {
        setIsProcessing(false);
        setStatusMessage("Dubbing completed successfully!");

        // Call the callback with the video URL
        if (data.videoUrl) {
          onDubbingComplete(data.videoUrl, language);
        }
      } else if (data.status === "error") {
        setIsProcessing(false);
        setError(data.message || "An error occurred during dubbing");
      } else {
        // Still processing, poll again in 5 seconds
        setStatusMessage(
          `Dubbing in progress: ${data.message || "Processing..."}`
        );
        setTimeout(() => pollStatus(id), 5000);
      }
    } catch (err) {
      console.error("Error checking dubbing status:", err);
      setError(
        err instanceof Error ? err.message : "Failed to check dubbing status"
      );
      setIsProcessing(false);
    }
  };

  return (
    <div className="mt-4 space-y-4">
      <h3 className="text-lg font-medium text-white">
        Professional Dubbing with Sieve.ai
      </h3>

      {showApiKeyInput ? (
        <div className="space-y-2">
          <label className="block text-sm text-ai-muted">Sieve API Key</label>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="flex-grow bg-ai-lighter border border-ai-border rounded px-3 py-2 text-white"
              placeholder="Enter your Sieve API key"
            />
            <Button
              onClick={() => setShowApiKeyInput(false)}
              variant="subtle"
              size="sm"
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm text-ai-muted">
              Target Language
            </label>
            <Select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              options={LANGUAGE_OPTIONS}
              disabled={isProcessing}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm text-ai-muted">Voice Engine</label>
            <Select
              value={voiceEngine}
              onChange={(e) => setVoiceEngine(e.target.value)}
              options={VOICE_ENGINE_OPTIONS}
              disabled={isProcessing}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="enableLipSync"
              checked={enableLipSync}
              onChange={(e) => setEnableLipSync(e.target.checked)}
              disabled={isProcessing}
              className="rounded border-ai-border bg-ai-lighter"
            />
            <label htmlFor="enableLipSync" className="text-sm text-ai-muted">
              Enable Lip Sync (better visual quality)
            </label>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleSubmitDubbing}
              disabled={isProcessing}
              className="w-full"
            >
              {isProcessing && <Spinner className="w-4 h-4 mr-2" />}
              {isProcessing
                ? "Processing..."
                : "Professional Dub with Sieve.ai"}
            </Button>

            <Button
              onClick={() => setShowApiKeyInput(true)}
              variant="outline"
              size="sm"
              disabled={isProcessing}
            >
              API Key
            </Button>
          </div>
        </div>
      )}

      {statusMessage && (
        <div className="p-3 bg-ai-light/30 border border-ai-border rounded text-ai-muted text-sm">
          {statusMessage}
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default SieveDubbing;
