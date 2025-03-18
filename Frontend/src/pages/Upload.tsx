
import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import VideoUploader from '@/components/VideoUploader';
import VideoShorts from '@/components/VideoShorts';
import { toast } from '@/hooks/use-toast';
import { getGeneratedShorts } from '@/lib/videoService';
import type { Short } from '@/components/VideoShorts';

const Upload = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessed, setIsProcessed] = useState(false);
  const [shorts, setShorts] = useState<Short[]>([]);
  
  const handleUploadComplete = async (success: boolean, message: string) => {
    if (success) {
      toast({
        title: "Success",
        description: message || "Your video has been successfully processed",
        variant: "default",
      });
      setIsProcessed(true);
      
      try {
        const generatedShorts = await getGeneratedShorts();
        setShorts(generatedShorts as Short[]);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load generated shorts",
          variant: "destructive",
        });
      }
    } else {
      toast({
        title: "Error",
        description: message || "There was an error processing your video",
        variant: "destructive",
      });
      setIsProcessed(false);
    }
    setIsProcessing(false);
  };

  // Reset the state when the component unmounts
  useEffect(() => {
    return () => {
      setIsProcessed(false);
      setShorts([]);
    };
  }, []);

  return (
    <div className="min-h-screen bg-ai-dark overflow-x-hidden">
      <Navbar />
      <main className="section-container pb-20">
        <div className="max-w-4xl mx-auto">
          <h1 className="section-title mb-6">
            <span className="gradient-heading">Transform Long Videos</span>
          </h1>
          <p className="section-subtitle mb-10">
            Upload a video or paste a YouTube link to generate AI-optimized shorts and ads
          </p>
          
          <VideoUploader 
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
            onUploadComplete={handleUploadComplete}
          />
          
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
