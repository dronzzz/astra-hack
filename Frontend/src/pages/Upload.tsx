import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import VideoUploader from "@/components/VideoUploader";
import VideoShorts from "@/components/VideoShorts";
import ProcessingProgress from "@/components/ProcessingProgress";

const Upload = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessed, setIsProcessed] = useState(false);
  const [processMessage, setProcessMessage] = useState("");
  const [shorts, setShorts] = useState<any[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState("");

  // Poll for job status and update shorts as they become available
  useEffect(() => {
    if (!jobId || !isProcessing) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/status/${jobId}`);
        if (!response.ok) throw new Error("Failed to get status");

        const data = await response.json();
        console.log("Status update:", data);

        // Update progress and message
        if (data.progress) setProgress(data.progress);
        if (data.message) setCurrentStage(data.message);

        // Check if any videos are available
        if (data.videos && data.videos.length > 0) {
          // Update shorts with available videos
          setShorts(data.videos);
        }

        // Check if processing is complete
        if (data.status === "completed") {
          setIsProcessing(false);
          setIsProcessed(true);
          clearInterval(interval);
        } else if (data.status === "error") {
          setIsProcessing(false);
          setProcessMessage(data.message || "An error occurred");
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Error polling for status:", error);
      }
    }, 1000); // Poll every second for quicker updates

    return () => clearInterval(interval);
  }, [jobId, isProcessing]);

  const handleUploadComplete = (
    success: boolean,
    message: string,
    data?: any
  ) => {
    if (success && data && data.length > 0 && data[0].jobId) {
      setJobId(data[0].jobId);
      setIsProcessing(true);
      setProgress(0);
      setCurrentStage("Starting video processing");
    } else {
      setProcessMessage(message);
    }
  };

  return (
    <div className="min-h-screen bg-ai-dark overflow-x-hidden">
      <Navbar />
      <main className="section-container pb-20">
        <div className="max-w-6xl mx-auto">
          <h1 className="section-title mb-6">
            <span className="gradient-heading">Transform Long Videos</span>
          </h1>
          <p className="section-subtitle mb-10">
            Paste a YouTube link to generate AI-optimized shorts
          </p>

          <VideoUploader
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
            onUploadComplete={handleUploadComplete}
            setProgress={setProgress}
            setCurrentStage={setCurrentStage}
          />

          {/* Show the cool processing card when processing */}
          {isProcessing && jobId && (
            <ProcessingProgress
              progress={progress}
              currentStage={currentStage}
              jobId={jobId}
            />
          )}

          {/* Show shorts as they become available */}
          {shorts.length > 0 && (
            <div className="mt-12 animate-in fade-in duration-500">
              <div className="mb-4 flex items-center">
                <h2 className="text-xl font-semibold text-ai-blue">
                  Generated Shorts
                </h2>
                {isProcessing && shorts.length > 0 && (
                  <span className="ml-3 text-sm text-ai-accent-light bg-ai-accent-light/10 py-1 px-3 rounded-full">
                    {shorts.length} ready • more processing...
                  </span>
                )}
              </div>
              <VideoShorts shorts={shorts} isProcessing={isProcessing} />
            </div>
          )}

          {/* Show error message if any */}
          {!isProcessing && processMessage && (
            <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              {processMessage}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Upload;
