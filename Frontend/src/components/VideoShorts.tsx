import { useState, useEffect } from "react";
import { apiPost, getResourceUrl } from "../lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import DubbingService, { VideoSegment } from "./DubbingService";

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
  const [dubbedVideos, setDubbedVideos] = useState<{
    [segmentId: string]: { [language: string]: string };
  }>({});
  // YouTube upload states
  const [uploadingStatus, setUploadingStatus] = useState<{
    [key: string]: string;
  }>({});
  const [uploadResults, setUploadResults] = useState<{ [key: string]: any }>(
    {}
  );
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [currentSegmentId, setCurrentSegmentId] = useState("");

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

  const handleDubbingComplete = (
    segmentId: string,
    language: string,
    url: string
  ) => {
    // Update the dubbed videos state
    setDubbedVideos((prev) => ({
      ...prev,
      [segmentId]: {
        ...(prev[segmentId] || {}),
        [language]: url,
      },
    }));
  };

  const handleUploadToYouTube = async (segmentId: string) => {
    if (!jobId) {
      console.error("No jobId provided for YouTube upload");
      return;
    }

    // Instead of immediately uploading, just set the current segment ID and open the modal
    setCurrentSegmentId(segmentId);
    setUploadModalOpen(true);
  };

  const confirmUpload = async (title: string, description: string) => {
    // Close modal
    setUploadModalOpen(false);

    if (!currentSegmentId) return;

    console.log(
      `Uploading segment ${currentSegmentId} to YouTube with title: ${title}`
    );
    setUploadingStatus((prev) => ({
      ...prev,
      [currentSegmentId]: "uploading",
    }));

    const segment = shorts.find((s) => s.id === currentSegmentId);
    if (!segment) {
      setUploadingStatus((prev) => ({ ...prev, [currentSegmentId]: "error" }));
      return;
    }

    const requestData = {
      jobId,
      segmentId: currentSegmentId,
      title,
      description,
      tags: ["shorts", "ai-generated", "video"],
      privacyStatus: "public",
    };

    try {
      // Using fetch directly with full URL to bypass proxy
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";
      const response = await fetch(`${API_URL}/api/youtube-upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Upload failed:", response.status, errorText);
        setUploadingStatus((prev) => ({
          ...prev,
          [currentSegmentId]: "error",
        }));
        return;
      }

      const data = await response.json();
      console.log("Upload succeeded:", data);
      setUploadingStatus((prev) => ({
        ...prev,
        [currentSegmentId]: "success",
      }));
      setUploadResults((prev) => ({
        ...prev,
        [currentSegmentId]: {
          videoId: data.youtubeId,
          youtubeUrl: data.youtubeUrl,
        },
      }));
    } catch (error) {
      console.error("Error uploading to YouTube:", error);
      setUploadingStatus((prev) => ({ ...prev, [currentSegmentId]: "error" }));
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

          // Prepare segment for DubbingService
          const segment: VideoSegment = {
            id: short.id,
            url: short.url,
            thumbnailUrl: short.thumbnailUrl,
            title: short.title,
            dubbedVideos: dubbedVideos[short.id],
          };

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
                          src={getResourceUrl(short.url)}
                          poster={
                            short.thumbnailUrl
                              ? getResourceUrl(short.thumbnailUrl)
                              : undefined
                          }
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

                  {/* Display available translations */}
                  {hasTranslations && (
                    <div className="mt-2 bg-ai-darker border border-ai-lighter rounded-md p-2">
                      <p className="text-xs text-white mb-1">
                        Available languages:
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {translations.map((translation) => (
                          <a
                            key={translation.id}
                            href={getResourceUrl(translation.url)}
                            className="text-xs px-2 py-1 bg-ai-accent/20 text-ai-accent rounded hover:bg-ai-accent/30"
                          >
                            {translation.language || "Unknown"}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center mt-2">
                    <a
                      href={getResourceUrl(short.url)}
                      download
                      className="text-xs px-2 py-1 bg-ai-accent text-white rounded hover:bg-ai-accent/80"
                    >
                      Download
                    </a>

                    {/* YouTube upload button */}
                    <button
                      onClick={() => handleUploadToYouTube(short.id)}
                      disabled={uploadingStatus[short.id] === "uploading"}
                      className={`text-xs px-2 py-1 rounded 
                        ${
                          uploadingStatus[short.id] === "uploading"
                            ? "bg-gray-500 text-gray-300 cursor-not-allowed"
                            : uploadingStatus[short.id] === "success"
                            ? "bg-green-500/80 text-white"
                            : uploadingStatus[short.id] === "error"
                            ? "bg-red-500/80 text-white"
                            : "bg-blue-500/80 text-white hover:bg-blue-600/80"
                        }`}
                    >
                      {uploadingStatus[short.id] === "uploading"
                        ? "Uploading..."
                        : uploadingStatus[short.id] === "success"
                        ? "Uploaded to YouTube"
                        : uploadingStatus[short.id] === "error"
                        ? "Upload Failed"
                        : "Upload to YouTube"}
                    </button>
                  </div>

                  {/* New DubbingService component */}
                  <div className="mt-2">
                    <DubbingService
                      segment={segment}
                      jobId={jobId}
                      onDubbingComplete={handleDubbingComplete}
                    />
                  </div>

                  {/* Display YouTube link if available */}
                  {uploadingStatus[short.id] === "success" &&
                    uploadResults[short.id]?.youtubeUrl && (
                      <div className="mt-2 p-2 bg-ai-darker border border-ai-lighter rounded-md">
                        <p className="text-xs text-white mb-1">YouTube link:</p>
                        <a
                          href={uploadResults[short.id].youtubeUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-400 hover:underline break-all"
                        >
                          {uploadResults[short.id].youtubeUrl}
                        </a>
                      </div>
                    )}

                  {/* Display error message if upload failed */}
                  {uploadingStatus[short.id] === "error" && (
                    <div className="mt-2 p-2 bg-red-900/30 border border-red-700/30 rounded-md">
                      <p className="text-xs text-red-400">
                        Failed to upload to YouTube. Please try again.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Upload dialog */}
      <Dialog open={uploadModalOpen} onOpenChange={setUploadModalOpen}>
        <DialogContent className="bg-ai-dark border border-ai-lighter text-white">
          <DialogHeader>
            <DialogTitle>Upload to YouTube</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Video Title</Label>
                <Input
                  id="title"
                  placeholder="Enter title for YouTube video"
                  className="bg-ai-darker border-ai-lighter text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Video Description</Label>
                <Textarea
                  id="description"
                  placeholder="Enter description for YouTube video"
                  className="bg-ai-darker border-ai-lighter text-white h-24"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setUploadModalOpen(false)}
              className="bg-transparent border-ai-lighter text-white hover:bg-ai-lighter"
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                const titleInput = document.getElementById(
                  "title"
                ) as HTMLInputElement;
                const descInput = document.getElementById(
                  "description"
                ) as HTMLTextAreaElement;
                confirmUpload(
                  titleInput?.value || "AI Generated Short",
                  descInput?.value ||
                    "This video was generated using AI technology."
                );
              }}
              className="bg-ai-accent text-white hover:bg-ai-accent/80"
            >
              Upload
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default VideoShorts;
