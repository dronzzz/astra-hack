import { useState, useEffect } from "react";

interface VideoShortsProps {
  shorts: any[];
  isProcessing?: boolean;
}

const VideoShorts = ({ shorts, isProcessing = false }: VideoShortsProps) => {
  // Log the shorts data when it changes
  useEffect(() => {
    if (shorts && shorts.length > 0) {
      console.log("Shorts data:", shorts);
    }
  }, [shorts]);

  if (!shorts || shorts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Use a 3-column grid on larger screens to make cards smaller */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {shorts.map((short, index) => (
          <div
            key={short.id || index}
            className="bg-ai-light rounded-lg overflow-hidden border border-ai-lighter shadow-md"
          >
            {/* Constrain max-width for individual cards */}
            <div className="max-w-[300px] mx-auto w-full">
              {/* Keep aspect ratio but with smaller height */}
              <div className="relative aspect-[9/16] bg-ai-dark overflow-hidden">
                <video
                  src={short.url}
                  poster={short.thumbnailUrl}
                  controls
                  playsInline
                  className="w-full h-full object-cover"
                  onError={(e) =>
                    console.error(`Video error for ${short.id}:`, e)
                  }
                />
              </div>

              <div className="p-2">
                <h3 className="font-medium text-white text-sm truncate">
                  {short.title}
                </h3>
                <p className="text-xs text-ai-muted mt-0.5">{short.duration}</p>

                <div className="flex justify-between items-center mt-2">
                  <a
                    href={short.url}
                    download={`short-${index + 1}.mp4`}
                    className="text-xs px-2 py-1 bg-ai-accent text-white rounded hover:bg-ai-accent/80"
                  >
                    Download
                  </a>

                  <a
                    href={short.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-ai-accent hover:underline"
                  >
                    Direct link
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Placeholder for processing */}
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
                <div className="h-4 bg-ai-darker rounded w-1/2 mt-2"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoShorts;
