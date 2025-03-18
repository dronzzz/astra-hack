import { useState, useRef } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Loader2 } from "lucide-react";

interface VideoUploaderProps {
  isProcessing: boolean;
  setIsProcessing: (isProcessing: boolean) => void;
  onUploadComplete: (success: boolean, message: string, videos?: any[]) => void;
  setProgress: (progress: number) => void;
  setCurrentStage: (stage: string) => void;
}

const VideoUploader = ({
  isProcessing,
  setIsProcessing,
  onUploadComplete,
  setProgress,
  setCurrentStage,
}: VideoUploaderProps) => {
  const [youtubeLink, setYoutubeLink] = useState("");
  const [isValidLink, setIsValidLink] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  // YouTube link validation
  const validateYoutubeLink = (link: string) => {
    const regex =
      /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})$/;
    return regex.test(link);
  };

  // Handle YouTube link input change
  const handleLinkChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const link = e.target.value;
    setYoutubeLink(link);
    if (link && !validateYoutubeLink(link)) {
      setIsValidLink(false);
      setErrorMessage("Please enter a valid YouTube video URL");
    } else {
      setIsValidLink(true);
      setErrorMessage("");
    }
  };

  // Handle YouTube link submission
  const handleLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!youtubeLink) {
      setIsValidLink(false);
      setErrorMessage("Please enter a YouTube link");
      return;
    }

    if (!validateYoutubeLink(youtubeLink)) {
      setIsValidLink(false);
      setErrorMessage("Please enter a valid YouTube video URL");
      return;
    }

    setIsProcessing(true);

    try {
      console.log("Processing YouTube link:", youtubeLink);

      // Make API call to process the YouTube link
      const response = await fetch("/api/process-youtube", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          youtubeUrl: youtubeLink,
          aspectRatio: "9:16",
          wordsPerSubtitle: 2,
          fontSize: 36,
        }),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Process result:", data);

      if (data.jobId) {
        // Set the jobId so we can show progress
        onUploadComplete(true, "Processing started", [{ jobId: data.jobId }]);
        // Start polling for status
        startStatusPolling(data.jobId);
      } else {
        throw new Error("No job ID returned from server");
      }
    } catch (error) {
      console.error("Error processing video:", error);
      setIsProcessing(false);
      onUploadComplete(
        false,
        error instanceof Error
          ? error.message
          : "Failed to process YouTube video"
      );
    }
  };

  // Enhanced polling with progress updates
  const startStatusPolling = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/status/${jobId}`);

        if (!response.ok) {
          throw new Error(`Failed to get status: ${response.status}`);
        }

        const status = await response.json();
        console.log("Job status:", status);

        // Update progress and stage in parent component
        if (status.progress) {
          setProgress(status.progress);
        }

        if (status.message) {
          setCurrentStage(status.message);
        }

        if (status.status === "completed") {
          clearInterval(interval);
          setIsProcessing(false);
          onUploadComplete(
            true,
            "Video processing completed",
            status.videos || []
          );
        } else if (status.status === "error") {
          clearInterval(interval);
          setIsProcessing(false);
          onUploadComplete(
            false,
            status.message || "An error occurred during processing"
          );
        }
        // Continue polling if still processing
      } catch (error) {
        console.error("Error checking status:", error);
        clearInterval(interval);
        setIsProcessing(false);
        onUploadComplete(false, "Failed to check processing status");
      }
    }, 2000); // Check every 2 seconds
  };

  return (
    <Card className="bg-ai-light border-ai-lighter">
      <CardContent className="p-6">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">
            Generate Shorts from YouTube
          </h2>

          {/* YouTube Link Input */}
          <form onSubmit={handleLinkSubmit} className="space-y-4">
            <div className="space-y-2">
              <label
                htmlFor="youtube-link"
                className="block text-sm text-ai-muted"
              >
                YouTube Video URL
              </label>
              <Input
                id="youtube-link"
                type="text"
                placeholder="https://www.youtube.com/watch?v=..."
                className={`bg-ai-dark border-ai-lighter ${
                  !isValidLink ? "border-red-500" : ""
                }`}
                value={youtubeLink}
                onChange={handleLinkChange}
                disabled={isProcessing}
              />
              {!isValidLink && (
                <p className="text-red-500 text-xs">{errorMessage}</p>
              )}
            </div>

            {!isProcessing ? (
              <Button
                type="submit"
                className="ai-btn-primary w-full"
                disabled={!youtubeLink || !isValidLink}
              >
                Process YouTube Video
              </Button>
            ) : (
              <div className="flex items-center justify-center gap-3 p-3 bg-ai-darker rounded-md">
                <Loader2 className="h-4 w-4 animate-spin text-ai-blue" />
                <span className="text-sm">Processing YouTube video...</span>
              </div>
            )}
          </form>

          <div className="text-center text-sm text-ai-muted">
            <p>
              We'll process your YouTube video and generate AI-optimized shorts
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default VideoUploader;
