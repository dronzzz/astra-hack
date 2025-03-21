import { useState, useEffect } from "react";

interface ProcessingProgressProps {
  progress: number;
  currentStage: string;
  jobId: string | null;
}

const ProcessingProgress = ({
  progress,
  currentStage,
  jobId,
}: ProcessingProgressProps) => {
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const [currentStageState, setCurrentStageState] = useState(currentStage);
  const [jobIdState, setJobIdState] = useState(jobId);
  const [isComplete, setIsComplete] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [additionalInfo, setAdditionalInfo] = useState({
    startTime: "",
    endTime: "",
    reason: "",
  });
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Smoothly animate the progress bar
  useEffect(() => {
    const animationDuration = 500; // ms
    const frameDuration = 16; // ms (roughly 60fps)
    const framesCount = animationDuration / frameDuration;
    const progressIncrement = (progress - animatedProgress) / framesCount;

    if (Math.abs(progress - animatedProgress) < 0.1) {
      setAnimatedProgress(progress);
      return;
    }

    const timer = setTimeout(() => {
      setAnimatedProgress((prev) =>
        Math.min(prev + progressIncrement, progress)
      );
    }, frameDuration);

    return () => clearTimeout(timer);
  }, [progress, animatedProgress]);

  // Map progress to AI-related steps for fun
  const getAiStepDescription = (progress: number) => {
    if (progress < 20) return "Neural activation initializing...";
    if (progress < 40) return "Training computer vision models...";
    if (progress < 60) return "Analyzing semantic content...";
    if (progress < 80) return "Optimizing frames for maximum engagement...";
    return "Finalizing content transformation...";
  };

  // Random tech words for the animated background
  const techWords = [
    "AI",
    "ML",
    "Tensor",
    "Neural",
    "Video",
    "Shorts",
    "Analysis",
    "Content",
    "Pixels",
    "Frames",
    "Encoding",
    "Processing",
  ];

  // When fetching the job status
  useEffect(() => {
    if (!jobIdState) return;

    const checkStatus = async () => {
      try {
        const response = await fetch(`/status/${jobIdState}`);
        if (!response.ok) throw new Error("Failed to get status");

        const data = await response.json();

        // Update progress from the new API format
        if (typeof data.progress === "number") {
          setAnimatedProgress(data.progress);
        }

        // Update stage from the new API format
        if (data.status) {
          // Convert status like "processing_video" to "Processing Video"
          const formattedStage = data.status
            .replace(/_/g, " ")
            .split(" ")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
          setCurrentStageState(formattedStage);
        }

        // Check if processing is complete
        if (data.status === "completed") {
          setIsComplete(true);
          // Create a download link
          setDownloadUrl(`/download/${jobIdState}`);

          // If segment info is available, show it
          if (data.segment_info) {
            setAdditionalInfo({
              startTime: formatTime(data.segment_info.start_time),
              endTime: formatTime(data.segment_info.end_time),
              reason:
                data.segment_info.reason ||
                "This segment was identified as the most engaging portion of the video.",
            });
          }

          clearInterval(statusCheckInterval);
        }
        // Check for errors
        else if (data.status === "failed") {
          setIsError(true);
          setErrorMessage(data.error || "An unknown error occurred");
          clearInterval(statusCheckInterval);
        }
      } catch (error) {
        console.error("Error checking job status:", error);
        setIsError(true);
        setErrorMessage("Failed to check processing status");
        clearInterval(statusCheckInterval);
      }
    };

    // Initial check
    checkStatus();

    // Set up interval for checking
    const statusCheckInterval = setInterval(checkStatus, 2000);

    return () => clearInterval(statusCheckInterval);
  }, [jobIdState]);

  // Helper function to format time
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="mt-8 p-6 bg-ai-light rounded-lg border border-ai-lighter relative overflow-hidden animate-in fade-in duration-300">
      {/* Animated background with tech words */}
      <div className="absolute inset-0 opacity-5 overflow-hidden pointer-events-none">
        {techWords.map((word, index) => (
          <div
            key={index}
            className="absolute text-ai-accent text-opacity-20 font-mono"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              transform: `rotate(${Math.random() * 360}deg)`,
              fontSize: `${Math.random() * 1 + 0.5}rem`,
              animation: `float ${Math.random() * 10 + 10}s linear infinite`,
            }}
          >
            {word}
          </div>
        ))}
      </div>

      <div className="relative z-10">
        <h3 className="text-lg font-medium text-white mb-4 flex items-center">
          <div className="w-4 h-4 mr-2 relative">
            <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-30"></div>
            <div className="absolute inset-0.5 bg-green-500 rounded-full"></div>
          </div>
          AI Processing Your Video
        </h3>

        <div className="space-y-6">
          <div>
            <p className="text-sm text-ai-muted mb-1">Current Operation:</p>
            <div className="flex items-center bg-ai-darker p-2 rounded-md border border-ai-lighter">
              <div className="flex-shrink-0 w-8 h-8 bg-ai-accent/30 rounded-full flex items-center justify-center mr-3">
                <div className="w-5 h-5 text-ai-accent animate-spin border-2 border-ai-accent border-t-transparent rounded-full"></div>
              </div>
              <div>
                <p className="text-white font-medium">
                  {currentStageState || "Initializing..."}
                </p>
                <p className="text-xs text-ai-muted">
                  {getAiStepDescription(animatedProgress)}
                </p>
              </div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-ai-muted mb-1">
              <span>Processing Progress</span>
              <span>{Math.round(animatedProgress)}%</span>
            </div>
            <div className="w-full bg-ai-darker rounded-full h-3 overflow-hidden relative">
              <div
                className="bg-gradient-to-r from-ai-accent to-ai-accent2 h-3 rounded-full transition-all duration-300 ease-in-out"
                style={{ width: `${animatedProgress}%` }}
              ></div>

              {/* Animated pulse effect */}
              {animatedProgress < 100 && (
                <div
                  className="absolute h-full top-0 bg-white opacity-20 w-20 filter blur-sm"
                  style={{
                    left: `${animatedProgress - 5}%`,
                    animation: "pulse 1.5s ease-in-out infinite",
                  }}
                ></div>
              )}
            </div>
          </div>

          <div className="bg-ai-darker/50 rounded-md p-3 border border-ai-lighter">
            <p className="text-xs text-ai-muted flex flex-col sm:flex-row sm:justify-between">
              <span>
                Job ID:{" "}
                <span className="font-mono text-ai-accent">{jobIdState}</span>
              </span>
              <span className="mt-1 sm:mt-0">
                Videos will appear below as they're processed
              </span>
            </p>

            {isComplete ? (
              <div className="mt-2 text-xs text-green-500 flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                Processing complete!
              </div>
            ) : (
              <div className="mt-2 text-xs text-ai-accent flex items-center">
                <div className="w-3 h-3 bg-ai-accent animate-pulse rounded-full mr-2"></div>
                Processing in progress - this may take a few minutes
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingProgress;
