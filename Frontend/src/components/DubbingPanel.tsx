import { useState, useEffect } from "react";
import { getResourceUrl } from "../lib/api";

// Define language options with flag emojis
export const LANGUAGE_OPTIONS = [
  { value: "english", label: "🇺🇸 English" },
  { value: "hindi", label: "🇮🇳 Hindi" },
  { value: "portuguese", label: "🇵🇹 Portuguese" },
  { value: "chinese", label: "🇨🇳 Mandarin (Chinese)" },
  { value: "spanish", label: "🇪🇸 Spanish" },
  { value: "french", label: "🇫🇷 French" },
  { value: "german", label: "🇩🇪 German" },
  { value: "japanese", label: "🇯🇵 Japanese" },
  { value: "arabic", label: "🇦🇪 Arabic" },
  { value: "russian", label: "🇷🇺 Russian" },
  { value: "korean", label: "🇰🇷 Korean" },
  { value: "indonesian", label: "🇮🇩 Indonesian" },
  { value: "italian", label: "🇮🇹 Italian" },
  { value: "dutch", label: "🇳🇱 Dutch" },
  { value: "turkish", label: "🇹🇷 Turkish" },
  { value: "polish", label: "🇵🇱 Polish" },
  { value: "swedish", label: "🇸🇪 Swedish" },
  { value: "tagalog", label: "🇵🇭 Tagalog (Filipino)" },
  { value: "malay", label: "🇲🇾 Malay" },
  { value: "romanian", label: "🇷🇴 Romanian" },
  { value: "ukrainian", label: "🇺🇦 Ukrainian" },
  { value: "greek", label: "🇬🇷 Greek" },
  { value: "czech", label: "🇨🇿 Czech" },
  { value: "danish", label: "🇩🇰 Danish" },
  { value: "finnish", label: "🇫🇮 Finnish" },
  { value: "bulgarian", label: "🇧🇬 Bulgarian" },
  { value: "croatian", label: "🇭🇷 Croatian" },
  { value: "slovak", label: "🇸🇰 Slovak" },
  { value: "tamil", label: "🇮🇳 Tamil" },
];

export interface DubbingStatus {
  [language: string]: "idle" | "processing" | "completed" | "failed";
}

interface DubbingPanelProps {
  videoId: string;
  jobId: string | null;
  onDubbingComplete?: (language: string, url: string) => void;
}

const DubbingPanel: React.FC<DubbingPanelProps> = ({
  videoId,
  jobId,
  onDubbingComplete,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dubbingStatus, setDubbingStatus] = useState<DubbingStatus>({});
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
  const [dubbedUrls, setDubbedUrls] = useState<{ [language: string]: string }>(
    {}
  );
  const [pollTimers, setPollTimers] = useState<{
    [language: string]: NodeJS.Timeout;
  }>({});

  // Clean up timers when component unmounts
  useEffect(() => {
    return () => {
      Object.values(pollTimers).forEach((timer) => clearInterval(timer));
    };
  }, [pollTimers]);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  const startDubbing = async (languageCode: string) => {
    if (!videoId || !jobId) {
      console.error("Missing videoId or jobId");
      return;
    }

    // Get language display name for UI
    const languageObj = LANGUAGE_OPTIONS.find(
      (lang) => lang.value === languageCode
    );

    // Update state to show processing
    setDubbingStatus((prev) => ({
      ...prev,
      [languageCode]: "processing",
    }));

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";
      const response = await fetch(`${API_URL}/api/dub-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jobId,
          segmentId: videoId,
          language: languageCode,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Dubbing request sent:", data);

      // Check if we got an immediate success response with dubbed video URLs
      if (data.success && data.dubbed_videos && data.dubbed_videos.length > 0) {
        console.log("Dubbed videos received:", data.dubbed_videos);

        // Update status to completed
        setDubbingStatus((prev) => ({
          ...prev,
          [languageCode]: "completed",
        }));

        // Store the URL for the dubbed video
        const dubbedVideoUrl = data.dubbed_videos[0];
        setDubbedUrls((prev) => ({
          ...prev,
          [languageCode]: dubbedVideoUrl,
        }));

        // Notify parent component
        if (onDubbingComplete) {
          onDubbingComplete(languageCode, dubbedVideoUrl);
        }

        // No need to poll since we already got the result
        return;
      }

      // Start polling for status if we didn't get immediate results
      startPolling(languageCode);
    } catch (error) {
      console.error("Error starting dubbing:", error);
      setDubbingStatus((prev) => ({
        ...prev,
        [languageCode]: "failed",
      }));
    }
  };

  const startPolling = (languageCode: string) => {
    // Clear any existing timer for this language
    if (pollTimers[languageCode]) {
      clearInterval(pollTimers[languageCode]);
    }

    // Create a new polling timer
    const timer = setInterval(() => {
      checkDubbingStatus(languageCode);
    }, 5000); // Check every 5 seconds

    setPollTimers((prev) => ({
      ...prev,
      [languageCode]: timer,
    }));
  };

  const checkDubbingStatus = async (languageCode: string) => {
    if (!jobId) return;

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";
      const response = await fetch(`${API_URL}/status/${jobId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const jobStatus = await response.json();

      // Find our video in the job status
      const video = jobStatus.videos?.find((v: any) => v.id === videoId);

      if (video && video.dubbing) {
        // Check the status of our specific language
        const dubbingInfo = video.dubbing[languageCode.toLowerCase()];

        if (dubbingInfo) {
          if (dubbingInfo.status === "completed") {
            // Dubbing is complete!
            clearInterval(pollTimers[languageCode]);

            // Update our state
            setDubbingStatus((prev) => ({
              ...prev,
              [languageCode]: "completed",
            }));

            // Store the URL
            setDubbedUrls((prev) => ({
              ...prev,
              [languageCode]: dubbingInfo.url,
            }));

            // Notify parent component
            if (onDubbingComplete) {
              onDubbingComplete(languageCode, dubbingInfo.url);
            }
          } else if (dubbingInfo.status === "failed") {
            // Dubbing failed
            clearInterval(pollTimers[languageCode]);
            setDubbingStatus((prev) => ({
              ...prev,
              [languageCode]: "failed",
            }));
          }
          // If still processing, we just continue polling
        }
      }
    } catch (error) {
      console.error("Error checking dubbing status:", error);
    }
  };

  const handleSelectLanguage = (languageCode: string) => {
    setSelectedLanguage(languageCode);

    // If already dubbed, just select it
    if (dubbingStatus[languageCode] === "completed") {
      return;
    }

    // If not already dubbing, start the process
    if (
      !dubbingStatus[languageCode] ||
      dubbingStatus[languageCode] === "failed"
    ) {
      startDubbing(languageCode);
    }
  };

  const getLanguageStatus = (languageCode: string) => {
    return dubbingStatus[languageCode] || "idle";
  };

  return (
    <div className="mt-2">
      {/* Toggle button */}
      <button
        onClick={togglePanel}
        className="text-xs px-3 py-1.5 rounded bg-ai-accent/20 text-ai-accent hover:bg-ai-accent/30 transition-all"
      >
        {isOpen ? "Hide Languages" : "Translate Video"}
      </button>

      {/* Language selection panel */}
      {isOpen && (
        <div className="mt-2 bg-ai-darker border border-ai-lighter rounded-md p-3 animate-in fade-in duration-200">
          <p className="text-xs text-white mb-2">
            Select a language for dubbing:
          </p>

          <div className="grid grid-cols-2 gap-2 max-h-[200px] overflow-y-auto">
            {LANGUAGE_OPTIONS.map((lang) => {
              if (lang.value === "english") return null; // Skip English as it's the original

              const status = getLanguageStatus(lang.value);
              const isSelected = selectedLanguage === lang.value;

              return (
                <button
                  key={lang.value}
                  onClick={() => handleSelectLanguage(lang.value)}
                  disabled={status === "processing"}
                  className={`text-xs px-2 py-1.5 rounded flex items-center justify-between
                    ${
                      status === "processing"
                        ? "bg-blue-500/30 text-blue-300 cursor-wait"
                        : status === "completed"
                        ? "bg-green-500/30 text-green-300"
                        : status === "failed"
                        ? "bg-red-500/30 text-red-300"
                        : isSelected
                        ? "bg-ai-accent text-white"
                        : "bg-ai-accent/50 text-white hover:bg-ai-accent/80"
                    }
                  `}
                >
                  <span>{lang.label}</span>

                  {status === "processing" && (
                    <div className="h-3 w-3 rounded-full border-2 border-blue-400 border-t-transparent animate-spin ml-1"></div>
                  )}

                  {status === "completed" && (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3 w-3 text-green-400 ml-1"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}

                  {status === "failed" && (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3 w-3 text-red-400 ml-1"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>

          {/* Status messages and download links */}
          {selectedLanguage && (
            <div className="mt-3">
              {dubbingStatus[selectedLanguage] === "processing" && (
                <div className="bg-blue-900/30 border border-blue-700/30 rounded-md p-2 text-xs text-blue-400 flex items-center">
                  <div className="h-3 w-3 rounded-full border-2 border-blue-400 border-t-transparent animate-spin mr-2"></div>
                  Creating dubbed version... This may take a few minutes.
                </div>
              )}

              {dubbingStatus[selectedLanguage] === "completed" && (
                <div className="bg-green-900/30 border border-green-700/30 rounded-md p-2 text-xs">
                  <p className="text-green-400 mb-1">Dubbing complete!</p>
                  <a
                    href={getResourceUrl(dubbedUrls[selectedLanguage])}
                    download
                    className="inline-block px-2 py-1 bg-green-700/50 text-green-300 rounded hover:bg-green-700/70"
                  >
                    Download Dubbed Version
                  </a>
                </div>
              )}

              {dubbingStatus[selectedLanguage] === "failed" && (
                <div className="bg-red-900/30 border border-red-700/30 rounded-md p-2 text-xs text-red-400">
                  Error creating dubbed version. Please try again.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DubbingPanel;
