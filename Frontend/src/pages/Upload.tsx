import { useState } from "react";
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

  const handleUploadComplete = (
    success: boolean,
    message: string,
    videos?: any[]
  ) => {
    if (success && videos && videos.length > 0) {
      setShorts(videos);
      setIsProcessed(true);
    } else if (success && videos && videos.length === 0) {
      // This is just the initial "processing started" response
      // Don't set isProcessed yet, we're just starting
      setJobId(message.jobId);
    }
    setProcessMessage(message);
  };

  return (
    <div className="min-h-screen bg-ai-dark overflow-x-hidden">
      <Navbar />
      <main className="section-container pb-20">
        <div className="max-w-4xl mx-auto">
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

          {/* Use the new ProcessingProgress component */}
          {isProcessing && jobId && (
            <ProcessingProgress
              progress={progress}
              currentStage={currentStage}
              jobId={jobId}
            />
          )}

          {/* Only show real shorts from backend */}
          {isProcessed && shorts.length > 0 && (
            <div className="mt-16">
              <VideoShorts shorts={shorts} />
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Upload;
