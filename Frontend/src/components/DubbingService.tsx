import { useState, useEffect } from "react";
import LanguageSelector, {
  DubbingStatus,
  LANGUAGE_OPTIONS,
} from "./LanguageSelector";
import { getResourceUrl } from "../lib/api";

interface DubbedVideo {
  [languageCode: string]: string; // URL paths
}

export interface VideoSegment {
  id: string;
  url: string;
  thumbnailUrl?: string;
  title?: string;
  dubbedVideos?: DubbedVideo;
}

interface DubbingServiceProps {
  segment: VideoSegment;
  jobId: string | null;
  onDubbingComplete?: (
    segmentId: string,
    languageCode: string,
    url: string
  ) => void;
}

const DubbingService: React.FC<DubbingServiceProps> = ({
  segment,
  jobId,
  onDubbingComplete,
}) => {
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [dubbingStatus, setDubbingStatus] = useState<DubbingStatus>({});
  const [selectedLanguage, setSelectedLanguage] = useState<
    string | undefined
  >();
  const [currentUrl, setCurrentUrl] = useState<string>(segment.url);

  // Poll for dubbing status if there's an active job
  useEffect(() => {
    let intervals: { [key: string]: NodeJS.Timeout } = {};

    // For each language that is processing, set up polling
    Object.keys(dubbingStatus).forEach((segmentId) => {
      Object.keys(dubbingStatus[segmentId] || {}).forEach((language) => {
        if (dubbingStatus[segmentId][language] === "processing") {
          // Set up polling for this language
          intervals[`${segmentId}-${language}`] = setInterval(() => {
            pollDubbingStatus(segmentId, language);
          }, 5000);
        }
      });
    });

    // Cleanup intervals on unmount
    return () => {
      Object.values(intervals).forEach(clearInterval);
    };
  }, [dubbingStatus, jobId]);

  // Update the current URL when selected language changes
  useEffect(() => {
    if (
      selectedLanguage &&
      segment.dubbedVideos?.[selectedLanguage] &&
      dubbingStatus[segment.id]?.[selectedLanguage] === "completed"
    ) {
      setCurrentUrl(segment.dubbedVideos[selectedLanguage]);
    } else {
      setCurrentUrl(segment.url);
    }
  }, [selectedLanguage, segment, dubbingStatus]);

  const handleLanguageChange = async (segmentId: string, language: string) => {
    if (!jobId) {
      console.error("No jobId provided for dubbing");
      return;
    }

    // Skip if already dubbed in this language or currently dubbing
    if (
      dubbingStatus[segmentId]?.[language] === "processing" ||
      dubbingStatus[segmentId]?.[language] === "completed"
    ) {
      // Just update the selected language
      setSelectedLanguage(language);
      return;
    }

    // Set the selected language
    setSelectedLanguage(language);

    // Update dubbing status
    setDubbingStatus((prev) => ({
      ...prev,
      [segmentId]: {
        ...(prev[segmentId] || {}),
        [language]: "processing",
      },
    }));

    try {
      // Get the language code (e.g., "es" from "🇪🇸 Spanish")
      const languageCode =
        LANGUAGE_OPTIONS.find((l) => l.label === language)?.value || "";

      if (!languageCode) {
        throw new Error(`Could not find language code for ${language}`);
      }

      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";
      const response = await fetch(`${API_URL}/api/dub-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jobId,
          segmentId,
          language: languageCode,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Dubbing failed:", response.status, errorText);
        setDubbingStatus((prev) => ({
          ...prev,
          [segmentId]: {
            ...(prev[segmentId] || {}),
            [language]: "failed",
          },
        }));
        return;
      }

      const data = await response.json();
      console.log("Dubbing request succeeded:", data);

      // Start polling for dubbing status
      pollDubbingStatus(segmentId, language);
    } catch (error) {
      console.error("Error requesting dubbing:", error);
      setDubbingStatus((prev) => ({
        ...prev,
        [segmentId]: {
          ...(prev[segmentId] || {}),
          [language]: "failed",
        },
      }));
    }
  };

  const pollDubbingStatus = async (segmentId: string, language: string) => {
    if (!jobId) return;

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";
      const response = await fetch(`${API_URL}/status/${jobId}`);

      if (!response.ok) {
        console.error("Error polling job status:", response.status);
        return;
      }

      const status = await response.json();

      // Find the segment and check dubbing status
      const videos = status.videos || [];
      const segment = videos.find((v: any) => v.id === segmentId);

      if (segment && segment.dubbing) {
        // Get language code from display name
        const languageObj = LANGUAGE_OPTIONS.find((l) => l.label === language);
        if (!languageObj) return;

        const languageCode = languageObj.value.toLowerCase();
        const dubbingInfo = segment.dubbing[languageCode];

        if (dubbingInfo) {
          if (dubbingInfo.status === "completed") {
            // Dubbing completed
            setDubbingStatus((prev) => ({
              ...prev,
              [segmentId]: {
                ...(prev[segmentId] || {}),
                [language]: "completed",
              },
            }));

            // Update the current URL if this is the selected language
            if (selectedLanguage === language) {
              setCurrentUrl(dubbingInfo.url);
            }

            // Notify parent component
            if (onDubbingComplete) {
              onDubbingComplete(segmentId, language, dubbingInfo.url);
            }

            console.log(
              `Dubbed video available for ${segmentId} in ${language}: ${dubbingInfo.url}`
            );
          } else if (dubbingInfo.status === "failed") {
            // Dubbing failed
            setDubbingStatus((prev) => ({
              ...prev,
              [segmentId]: {
                ...(prev[segmentId] || {}),
                [language]: "failed",
              },
            }));
          }
        }
      }
    } catch (error) {
      console.error("Error polling dubbing status:", error);
    }
  };

  const toggleLanguageSelector = () => {
    setShowLanguageSelector(!showLanguageSelector);
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <button
          onClick={toggleLanguageSelector}
          className={`text-xs px-2 py-1 rounded
            ${
              selectedLanguage &&
              dubbingStatus[segment.id]?.[selectedLanguage] === "completed"
                ? "bg-green-500/20 text-green-500"
                : "bg-ai-accent/20 text-ai-accent hover:bg-ai-accent/30"
            }`}
        >
          {selectedLanguage &&
          dubbingStatus[segment.id]?.[selectedLanguage] === "completed"
            ? `Dubbed: ${selectedLanguage}`
            : "Translate"}
        </button>

        {/* URL for the current language */}
        {selectedLanguage &&
          dubbingStatus[segment.id]?.[selectedLanguage] === "completed" && (
            <a
              href={getResourceUrl(currentUrl)}
              download
              className="text-xs px-2 py-1 bg-green-500/20 text-green-500 rounded hover:bg-green-500/30"
            >
              Download Dubbed
            </a>
          )}
      </div>

      {/* Language selector */}
      {showLanguageSelector && (
        <LanguageSelector
          segmentId={segment.id}
          onSelectLanguage={handleLanguageChange}
          dubbingStatus={dubbingStatus}
          selectedLanguage={selectedLanguage}
        />
      )}

      {/* Processing status */}
      {selectedLanguage &&
        dubbingStatus[segment.id]?.[selectedLanguage] === "processing" && (
          <div className="bg-ai-darker border border-ai-lighter rounded-md p-2 text-xs text-white flex items-center">
            <div className="h-3 w-3 rounded-full border-2 border-ai-accent border-t-transparent animate-spin mr-2"></div>
            Creating dubbed version in {selectedLanguage}...
          </div>
        )}

      {/* Error status */}
      {selectedLanguage &&
        dubbingStatus[segment.id]?.[selectedLanguage] === "failed" && (
          <div className="bg-red-900/30 border border-red-700/30 rounded-md p-2 text-xs text-red-400">
            Error creating dubbed version in {selectedLanguage}. Please try
            again.
          </div>
        )}
    </div>
  );
};

export default DubbingService;
