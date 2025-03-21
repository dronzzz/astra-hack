import { useState, useEffect } from "react";
import { apiPost } from "../lib/api";
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

// Define types for YouTube upload response
interface YouTubeUploadResponse {
  success: boolean;
  youtubeUrl?: string;
  youtubeId?: string;
  error?: string;
}

// New interface for YouTube upload modal
interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  segment: any;
  segmentId: string;
  onConfirm: (title: string, description: string) => void;
}

// YouTube upload modal component
const YouTubeUploadModal = ({
  isOpen,
  onClose,
  segment,
  segmentId,
  onConfirm,
}: UploadModalProps) => {
  const [title, setTitle] = useState(
    segment?.title || `Short Video ${segmentId}`
  );
  const [description, setDescription] = useState(
    segment?.description || "AI-generated short video"
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload to YouTube</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="title" className="text-right">
              Title
            </Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="col-span-3"
              maxLength={100}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="description" className="text-right">
              Description
            </Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="col-span-3"
              rows={4}
              maxLength={5000}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => onConfirm(title, description)}>Upload</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// In your VideoShorts component, add:
const [uploadModalOpen, setUploadModalOpen] = useState(false);
const [currentSegmentId, setCurrentSegmentId] = useState("");

// Modify your handleUploadToYouTube function:
const handleUploadToYouTube = async (segmentId: string) => {
  if (!jobId) {
    console.error("No jobId provided for YouTube upload");
    return;
  }

  // Set current segment and open modal
  setCurrentSegmentId(segmentId);
  setUploadModalOpen(true);
};

// Add a new function to handle the upload after modal confirmation
const confirmUpload = async (title: string, description: string) => {
  // Close modal
  setUploadModalOpen(false);

  if (!currentSegmentId) return;

  console.log(`Uploading segment ${currentSegmentId} to YouTube`);
  setUploadingStatus((prev) => ({ ...prev, [currentSegmentId]: "uploading" }));

  const segment = shorts.find((s) => s.id === currentSegmentId);
  if (!segment) {
    setUploadingStatus((prev) => ({ ...prev, [currentSegmentId]: "error" }));
    return;
  }

  const requestData = {
    jobId,
    segmentId: currentSegmentId,
    title: title,
    description: description,
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
    setUploadingStatus((prev) => ({ ...prev, [currentSegmentId]: "success" }));
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

// Add this to your JSX, just before the closing tag of your component
{
  uploadModalOpen && currentSegmentId && (
    <YouTubeUploadModal
      isOpen={uploadModalOpen}
      onClose={() => setUploadModalOpen(false)}
      segment={shorts.find((s) => s.id === currentSegmentId)}
      segmentId={currentSegmentId}
      onConfirm={confirmUpload}
    />
  );
}
