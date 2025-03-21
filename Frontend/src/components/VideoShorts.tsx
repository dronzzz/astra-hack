import { useState, useEffect } from "react";
import { apiPost } from "../lib/api";

// Define language options
const LANGUAGE_OPTIONS = [
  { value: "EN", label: "English" },
  { value: "ES", label: "Spanish" },
  { value: "FR", label: "French" },
  { value: "JP", label: "Japanese" },
  { value: "KR", label: "Korean" },
  { value: "ZH", label: "Chinese" },
];

// Define types for YouTube upload response
interface YouTubeUploadResponse {
  success: boolean;
  youtubeUrl?: string;
  youtubeId?: string;
  error?: string;
}

interface VideoShortsProps {
  shorts: any[];
  isProcessing?: boolean;
  jobId?: string | null;
}

const VideoShorts = ({
  shorts,
  isProcessing = false,
  jobId = null,
}: VideoShortsProps) => {
  const [videoErrors, setVideoErrors] = useState<{ [key: string]: boolean }>(
    {}
  );
  const [dubbingStatus, setDubbingStatus] = useState<{ [key: string]: string }>(
    {}
  );
  const [showLanguageSelector, setShowLanguageSelector] = useState<{
    [key: string]: boolean;
  }>({});
  // YouTube upload states
  const [uploadingStatus, setUploadingStatus] = useState<{
    [key: string]: string;
  }>({});
  const [uploadResults, setUploadResults] = useState<{ [key: string]: any }>(
    {}
  );

  // Group videos by their original segment ID
  const groupedShorts = shorts.reduce(
    (acc: { [key: string]: any[] }, short) => {
      // Extract the base ID (without language suffix)
      const baseId = short.id.split("_")[0];
      if (!acc[baseId]) {
        acc[baseId] = [];
      }
      acc[baseId].push(short);
      return acc;
    },
    {}
  );

  // Filter out any translated versions for the main display
  const originalShorts = shorts.filter((short) => !short.isTranslated);

  useEffect(() => {
    if (shorts && shorts.length > 0) {
      console.log("Shorts data:", shorts);
    }
  }, [shorts]);

  const handleVideoError = (id: string) => {
    console.error(`Video error for ${id}`);
    setVideoErrors((prev) => ({ ...prev, [id]: true }));
  };

  const toggleLanguageSelector = (id: string) => {
    setShowLanguageSelector((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const requestDubbing = async (segmentId: string, language: string) => {
    if (!jobId) {
      console.error("Cannot request dubbing: jobId is null or undefined");
      setDubbingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
      return;
    }

    console.log(
      `Requesting dubbing for segment ${segmentId} in language ${language}, jobId: ${jobId}`
    );
    setDubbingStatus((prev) => ({ ...prev, [segmentId]: "loading" }));
    setShowLanguageSelector((prev) => ({ ...prev, [segmentId]: false }));

    const requestData = {
      jobId,
      segmentId,
      language,
      // Add Sieve-specific parameters
      voiceEngine: "elevenlabs (voice cloning)",
      enableLipsyncing: false,
      preserveBackgroundAudio: true,
    };

    console.log("Sending request data:", requestData);

    try {
      // *** CHANGED TO USE THE NEW SIEVE ENDPOINT ***
      const url = new URL("/api/sieve-dub", window.location.origin);
      console.log(`Sending POST to ${url.toString()} with data:`, requestData);

      const response = await fetch(url.toString(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      // Get the full text response regardless of status
      const responseText = await response.text();
      console.log(`Raw response (${response.status}): ${responseText}`);

      // Try to parse the response as JSON
      let responseData;
      try {
        responseData = JSON.parse(responseText);
      } catch (e) {
        console.error("Failed to parse response as JSON:", e);
        responseData = { error: "Invalid JSON response" };
      }

      if (!response.ok) {
        console.error("Dubbing failed with response:", {
          status: response.status,
          statusText: response.statusText,
          data: responseData,
        });

        throw new Error(responseData?.error || "Failed to dub video");
      }

      console.log("Dubbing submitted successfully:", responseData);

      // Begin polling for status
      if (responseData.dubbingId) {
        pollDubbingStatus(segmentId, responseData.dubbingId, language);
      } else {
        setDubbingStatus((prev) => ({ ...prev, [segmentId]: "success" }));
      }
    } catch (error) {
      console.error("Error dubbing video:", error);
      setDubbingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
    }
  };

  // Add a polling function for the dubbing status that works with your component's structure
  const pollDubbingStatus = async (
    segmentId: string,
    dubbingId: string,
    language: string
  ) => {
    try {
      const response = await fetch(`/api/sieve-dub-status/${dubbingId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to check dubbing status");
      }

      console.log(`Dubbing status for ${segmentId}:`, data);

      if (data.status === "completed") {
        // Dubbing is complete, update the UI
        setDubbingStatus((prev) => ({ ...prev, [segmentId]: "success" }));

        // If there's a videoUrl in the response, update the video sources
        if (data.videoUrl) {
          console.log(
            `Updating video source for ${segmentId} to: ${data.videoUrl}`
          );

          // Add the new video to the shorts array
          const dubbedShort = shorts.find((short) => short.id === segmentId);

          if (dubbedShort) {
            const dubbedVideo = {
              ...dubbedShort,
              id: `${segmentId}-${language}`, // Create a new ID for the dubbed version
              url: data.videoUrl,
              thumbnailUrl: data.thumbnailUrl || dubbedShort.thumbnailUrl,
              isDubbed: true,
              originalId: segmentId,
              language: language,
            };

            // NOTE: We can't add to shorts directly since setShorts is not available here
            // This would require the parent component to pass setShorts as a prop
            // setShorts((prev) => [...prev, dubbedVideo]);

            // Show a simple console log instead of toast
            console.log(`Dubbing complete for ${segmentId} in ${language}`);
          }
        }
      } else if (data.status === "error") {
        // Error occurred during dubbing
        setDubbingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
        console.error("Dubbing error:", data.message);
      } else {
        // Still processing, poll again after a delay
        setTimeout(
          () => pollDubbingStatus(segmentId, dubbingId, language),
          5000
        );
      }
    } catch (error) {
      console.error("Error checking dubbing status:", error);
      setDubbingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
    }
  };

  const handleUploadToYouTube = async (segmentId: string) => {
    if (!jobId) {
      console.error("No jobId provided for YouTube upload");
      return;
    }

    console.log(`Uploading segment ${segmentId} to YouTube`);
    setUploadingStatus((prev) => ({ ...prev, [segmentId]: "uploading" }));

    const segment = shorts.find((s) => s.id === segmentId);
    if (!segment) {
      setUploadingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
      return;
    }

    const requestData = {
      jobId,
      segmentId,
      title: segment.title || `Short Video ${segmentId}`,
      description: segment.description || "AI-generated short video",
      tags: ["shorts", "ai-generated", "video"],
      privacyStatus: "public",
    };

    try {
      // Use apiPost with the correct type annotation
      const data = await apiPost<YouTubeUploadResponse>(
        "api/youtube-upload",
        requestData
      );

      console.log("Upload succeeded:", data);
      setUploadingStatus((prev) => ({ ...prev, [segmentId]: "success" }));
      setUploadResults((prev) => ({
        ...prev,
        [segmentId]: {
          videoId: data.youtubeId,
          youtubeUrl: data.youtubeUrl,
        },
      }));
    } catch (error) {
      console.error("Error uploading to YouTube:", error);
      setUploadingStatus((prev) => ({ ...prev, [segmentId]: "error" }));
    }
  };

  if (!shorts || shorts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {originalShorts.map((short, index) => {
          // Get any translated versions for this short
          const translations =
            groupedShorts[short.id]?.filter((s) => s.id !== short.id) || [];
          const hasTranslations = translations.length > 0;

          return (
            <div
              key={short.id}
              className="bg-ai-light rounded-lg overflow-hidden border border-ai-lighter shadow-md"
            >
              <div className="max-w-[300px] mx-auto w-full">
                <div className="relative aspect-[9/16] bg-ai-dark overflow-hidden">
                  {videoErrors[short.id] ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-4 bg-ai-darker text-ai-muted">
                      <span className="text-sm text-center">
                        Video playback error
                      </span>
                      <button
                        onClick={() =>
                          setVideoErrors((prev) => ({
                            ...prev,
                            [short.id]: false,
                          }))
                        }
                        className="mt-2 px-3 py-1 bg-ai-accent text-white text-xs rounded hover:bg-ai-accent/80"
                      >
                        Try Again
                      </button>
                    </div>
                  ) : (
                    // Log outside of the JSX to avoid the void type error
                    (() => {
                      console.log(
                        `Loading video for ${short.id} from ${short.url}`
                      );
                      return (
                        <video
                          src={short.url}
                          poster={short.thumbnailUrl}
                          controls
                          playsInline
                          autoPlay={false}
                          onError={() => handleVideoError(short.id)}
                          className="w-full h-full object-contain"
                        />
                      );
                    })()
                  )}
                </div>

                <div className="p-2">
                  <h3 className="font-medium text-white text-sm truncate">
                    {short.title}
                  </h3>
                  <p className="text-xs text-ai-muted mt-0.5">
                    {short.duration}
                  </p>

                  {/* Translations selector and status */}
                  <div className="mt-2 space-y-2">
                    {/* Language selector dropdown */}
                    {showLanguageSelector[short.id] && (
                      <div className="bg-ai-darker border border-ai-lighter rounded-md p-2 animate-in fade-in zoom-in duration-200">
                        <p className="text-xs text-white mb-1">
                          Select language:
                        </p>
                        <div className="grid grid-cols-2 gap-1">
                          {LANGUAGE_OPTIONS.map((lang) => (
                            <button
                              key={lang.value}
                              onClick={() =>
                                requestDubbing(short.id, lang.value)
                              }
                              className={`text-xs px-2 py-1 rounded 
                                ${
                                  lang.value === "EN"
                                    ? "bg-ai-lighter text-ai-muted cursor-not-allowed"
                                    : "bg-ai-accent text-white hover:bg-ai-accent/80"
                                }`}
                              disabled={lang.value === "EN"}
                            >
                              {lang.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Dubbing status */}
                    {dubbingStatus[short.id] === "loading" && (
                      <div className="bg-ai-darker border border-ai-lighter rounded-md p-2 text-xs text-white flex items-center">
                        <div className="h-3 w-3 rounded-full border-2 border-ai-accent border-t-transparent animate-spin mr-2"></div>
                        Creating dubbed version...
                      </div>
                    )}

                    {dubbingStatus[short.id] === "error" && (
                      <div className="bg-red-900/30 border border-red-700/30 rounded-md p-2 text-xs text-red-400">
                        Error creating dubbed version. Please try again.
                      </div>
                    )}

                    {/* Available translations */}
                    {hasTranslations && (
                      <div className="bg-ai-darker border border-ai-lighter rounded-md p-2">
                        <p className="text-xs text-white mb-1">
                          Available languages:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {translations.map((translation) => (
                            <a
                              key={translation.id}
                              href={translation.url}
                              className="text-xs px-2 py-1 bg-ai-accent/20 text-ai-accent rounded hover:bg-ai-accent/30"
                            >
                              {translation.language || "Unknown"}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between items-center mt-2">
                    <a
                      href={short.url}
                      download
                      className="text-xs px-2 py-1 bg-ai-accent text-white rounded hover:bg-ai-accent/80"
                    >
                      Download
                    </a>

                    {/* Language dubbing button */}
                    <button
                      onClick={() => toggleLanguageSelector(short.id)}
                      className={`text-xs px-2 py-1 rounded bg-ai-accent/20 text-ai-accent ${
                        dubbingStatus[short.id] === "success"
                          ? "bg-green-500/20 text-green-500"
                          : ""
                      }`}
                    >
                      {dubbingStatus[short.id] === "success"
                        ? "Dub Created"
                        : "Dub to Other Languages"}
                    </button>

                    {/* YouTube upload button */}
                    <button
                      onClick={() => handleUploadToYouTube(short.id)}
                      disabled={
                        uploadingStatus[short.id] === "uploading" ||
                        uploadingStatus[short.id] === "success"
                      }
                      className={`text-xs px-2 py-1 rounded flex items-center gap-1
                        ${
                          uploadingStatus[short.id] === "success"
                            ? "bg-green-500/20 text-green-500"
                            : uploadingStatus[short.id] === "error"
                            ? "bg-red-500/20 text-red-400"
                            : "bg-red-600/80 text-white hover:bg-red-600"
                        }`}
                    >
                      {uploadingStatus[short.id] === "uploading" ? (
                        <>
                          <div className="h-2 w-2 rounded-full border-2 border-white border-t-transparent animate-spin mr-1"></div>
                          Uploading...
                        </>
                      ) : uploadingStatus[short.id] === "success" ? (
                        "Uploaded to YouTube"
                      ) : uploadingStatus[short.id] === "error" ? (
                        "Upload Failed"
                      ) : (
                        "Upload to YouTube"
                      )}
                    </button>
                  </div>

                  {/* Display YouTube link when upload is successful */}
                  {uploadingStatus[short.id] === "success" &&
                    uploadResults[short.id] && (
                      <div className="mt-2 bg-ai-darker border border-ai-lighter rounded-md p-2">
                        <p className="text-xs text-white mb-1">YouTube link:</p>
                        <a
                          href={uploadResults[short.id].youtubeUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-ai-accent hover:underline break-all"
                        >
                          {uploadResults[short.id].youtubeUrl}
                        </a>
                      </div>
                    )}

                  {/* Display error message */}
                  {uploadingStatus[short.id] === "error" && (
                    <div className="mt-2 bg-red-900/30 border border-red-700/30 rounded-md p-2 text-xs text-red-400">
                      Failed to upload to YouTube. Please try again.
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {isProcessing && (
          <div className="bg-ai-light rounded-lg overflow-hidden border border-ai-lighter animate-pulse">
            <div className="max-w-[300px] mx-auto w-full">
              <div className="relative aspect-[9/16] bg-ai-darker">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-6 w-6 rounded-full border-2 border-ai-accent border-t-transparent animate-spin"></div>
                </div>
              </div>
              <div className="p-2">
                <div className="h-3 bg-ai-darker rounded w-3/4"></div>
                <div className="h-2 bg-ai-darker rounded w-1/4 mt-1"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoShorts;
