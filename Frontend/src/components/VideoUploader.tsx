
import { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { 
  YoutubeIcon, 
  UploadCloud, 
  AlertCircle, 
  Loader2,
  FileVideo,
  CheckCircle2
} from 'lucide-react';
import { processYoutubeLink, uploadVideoFile } from '@/lib/videoService';
import { 
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';

interface VideoUploaderProps {
  isProcessing: boolean;
  setIsProcessing: (isProcessing: boolean) => void;
  onUploadComplete: (success: boolean, message: string) => void;
}

const VideoUploader = ({ 
  isProcessing, 
  setIsProcessing, 
  onUploadComplete 
}: VideoUploaderProps) => {
  const [youtubeLink, setYoutubeLink] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isValidLink, setIsValidLink] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadMethod, setUploadMethod] = useState<'file' | 'link' | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // YouTube link validation
  const validateYoutubeLink = (link: string) => {
    const regex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})$/;
    return regex.test(link);
  };

  // Handle YouTube link input change
  const handleLinkChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const link = e.target.value;
    setYoutubeLink(link);
    if (link && !validateYoutubeLink(link)) {
      setIsValidLink(false);
      setErrorMessage('Please enter a valid YouTube video URL');
    } else {
      setIsValidLink(true);
      setErrorMessage('');
    }
  };

  // Handle YouTube link submission
  const handleLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeLink) {
      setIsValidLink(false);
      setErrorMessage('Please enter a YouTube link');
      return;
    }
    
    if (!validateYoutubeLink(youtubeLink)) {
      setIsValidLink(false);
      setErrorMessage('Please enter a valid YouTube video URL');
      return;
    }
    
    setIsProcessing(true);
    setUploadMethod('link');
    try {
      const result = await processYoutubeLink(youtubeLink);
      onUploadComplete(true, 'YouTube video processed successfully');
    } catch (error) {
      let message = 'Failed to process YouTube video';
      if (error instanceof Error) message = error.message;
      onUploadComplete(false, message);
    }
  };

  // Handle file upload via dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      // Check if file is a video
      if (!file.type.startsWith('video/')) {
        setErrorMessage('Please upload a video file');
        return;
      }
      
      // Check if file size is less than 500MB
      if (file.size > 500 * 1024 * 1024) {
        setErrorMessage('File size should be less than 500MB');
        return;
      }
      
      setSelectedFile(file);
      setErrorMessage('');
      setUploadMethod('file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'video/*': []
    }
  });

  // Handle file upload submission
  const handleFileUpload = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a file to upload');
      return;
    }
    
    setIsProcessing(true);
    setUploadProgress(0);
    
    try {
      await uploadVideoFile(selectedFile, (progress) => {
        setUploadProgress(progress);
      });
      onUploadComplete(true, 'Video uploaded and processed successfully');
    } catch (error) {
      let message = 'Failed to upload video';
      if (error instanceof Error) message = error.message;
      onUploadComplete(false, message);
    }
  };

  // Reset everything
  const handleReset = () => {
    setSelectedFile(null);
    setYoutubeLink('');
    setErrorMessage('');
    setUploadProgress(0);
    setUploadMethod(null);
  };

  return (
    <Card className="glass-card">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl text-ai-blue">Upload Your Content</CardTitle>
        <CardDescription>Drop your video file or paste a YouTube link</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Error message */}
        {errorMessage && (
          <div className="mb-6 flex items-center gap-2 text-red-400 text-sm p-3 bg-red-400/10 rounded-md">
            <AlertCircle size={16} />
            <span>{errorMessage}</span>
          </div>
        )}
        
        <div className="space-y-6">
          {/* Unified upload interface */}
          {!uploadMethod && !isProcessing ? (
            <div className="space-y-6">
              {/* File dropzone area */}
              <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive ? 'border-ai-blue bg-ai-blue/5' : 'border-ai-lighter'
                }`}
              >
                <input {...getInputProps()} ref={fileInputRef} />
                
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 bg-ai-light rounded-full flex items-center justify-center mb-4">
                    <UploadCloud className="text-ai-blue h-8 w-8" />
                  </div>
                  
                  <h3 className="text-lg font-medium mb-2">
                    {isDragActive ? 'Drop your video here' : 'Drag & drop your video file'}
                  </h3>
                  
                  <p className="text-ai-muted mb-4">
                    Support for MP4, MOV, AVI videos up to 500MB
                  </p>
                  
                  <span className="px-4 py-2 rounded-md bg-ai-lighter text-ai-text text-sm inline-block">
                    or browse from your device
                  </span>
                </div>
              </div>

              {/* Separator */}
              <div className="relative flex py-4 items-center">
                <div className="flex-grow border-t border-ai-lighter"></div>
                <span className="flex-shrink mx-4 text-ai-muted">OR</span>
                <div className="flex-grow border-t border-ai-lighter"></div>
              </div>

              {/* YouTube link input */}
              <form onSubmit={handleLinkSubmit} className="space-y-4">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <YoutubeIcon className="text-ai-muted h-5 w-5" />
                  </div>
                  <Input
                    type="text"
                    placeholder="Paste YouTube video URL"
                    className={`pl-10 ${!isValidLink ? 'border-red-400 focus:ring-red-400' : ''}`}
                    value={youtubeLink}
                    onChange={handleLinkChange}
                  />
                </div>
                <p className="text-ai-muted text-xs">
                  Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
                </p>
                
                {/* Submit button */}
                <Button 
                  type="submit"
                  className="ai-btn-primary w-full"
                  disabled={!youtubeLink || !isValidLink}
                >
                  Process YouTube Video
                </Button>
              </form>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Show file details or link being processed */}
              <div className="bg-ai-lighter/30 rounded-lg p-6">
                {uploadMethod === 'file' && selectedFile && (
                  <div className="flex items-center gap-3">
                    <div className="bg-ai-light p-3 rounded-full">
                      <FileVideo className="text-ai-blue h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{selectedFile.name}</p>
                      <p className="text-xs text-ai-muted">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                    {!isProcessing && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={handleReset}
                        className="text-ai-muted hover:text-white"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                )}

                {uploadMethod === 'link' && (
                  <div className="flex items-center gap-3">
                    <div className="bg-ai-light p-3 rounded-full">
                      <YoutubeIcon className="text-ai-blue h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{youtubeLink}</p>
                      <p className="text-xs text-ai-muted">
                        YouTube Video
                      </p>
                    </div>
                    {!isProcessing && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={handleReset}
                        className="text-ai-muted hover:text-white"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                )}

                {/* Processing indicators */}
                {isProcessing && (
                  <div className="mt-6">
                    {uploadMethod === 'file' ? (
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span>Uploading video...</span>
                          <span>{uploadProgress}%</span>
                        </div>
                        <Progress value={uploadProgress} className="h-2 bg-ai-lighter">
                          <div className="h-full bg-gradient-to-r from-ai-accent to-ai-accent2 rounded-full" />
                        </Progress>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3 p-3 bg-ai-light rounded-md">
                        <Loader2 className="h-4 w-4 animate-spin text-ai-blue" />
                        <span className="text-sm">Processing YouTube video...</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Action buttons */}
              {!isProcessing && uploadMethod === 'file' && (
                <Button 
                  onClick={handleFileUpload}
                  className="ai-btn-primary w-full"
                >
                  Upload & Process Video
                </Button>
              )}

              {/* Reset button when not processing */}
              {!isProcessing && (
                <Button 
                  variant="outline" 
                  onClick={handleReset}
                  className="w-full border-ai-lighter text-ai-muted hover:text-white"
                >
                  Try a different upload
                </Button>
              )}
            </div>
          )}

          {/* Info message */}
          <div className="text-center text-sm text-ai-muted">
            <p>We'll process your video and generate AI-optimized shorts and ad creatives</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default VideoUploader;
