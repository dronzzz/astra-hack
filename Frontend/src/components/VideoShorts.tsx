import { useState, useEffect } from "react";

interface VideoShortsProps {
  shorts: any[];
  isProcessing?: boolean;
}

// Fallback thumbnail image
const FALLBACK_THUMBNAIL = "/fallback-thumbnail.jpg";

const VideoShorts = ({ shorts, isProcessing = false }: VideoShortsProps) => {
  const [thumbnailErrors, setThumbnailErrors] = useState<{
    [key: string]: boolean;
  }>({});
  const [videoErrors, setVideoErrors] = useState<{ [key: string]: boolean }>(
    {}
  );

  useEffect(() => {
    if (shorts && shorts.length > 0) {
      console.log("Shorts data:", shorts);
      shorts.forEach((short) => {
        // Preload the thumbnails to check availability
        const img = new Image();
        img.onload = () =>
          console.log(`Thumbnail loaded: ${short.thumbnailUrl}`);
        img.onerror = () => {
          console.error(`Failed to load thumbnail: ${short.thumbnailUrl}`);
          setThumbnailErrors((prev) => ({ ...prev, [short.id]: true }));
        };
        img.src = short.thumbnailUrl;

        // Log the video URL
        console.log(`Video URL: ${short.url}`);
      });
    }
  }, [shorts]);

  if (!shorts || shorts.length === 0) {
    return null;
  }

  const handleThumbnailError = (id: string) => {
    console.error(`Thumbnail load error for ${id}`);
    setThumbnailErrors((prev) => ({ ...prev, [id]: true }));
  };

  const handleVideoError = (id: string) => {
    console.error(`Video error for ${id}`);
    setVideoErrors((prev) => ({ ...prev, [id]: true }));
  };

  // Function to download the video directly
  const downloadVideo = (url: string, filename: string) => {
    // Create a temporary anchor and trigger download
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {shorts.map((short, index) => (
          <div
            key={short.id || index}
            className="bg-ai-light rounded-lg overflow-hidden border border-ai-lighter shadow-md"
          >
            <div className="max-w-[300px] mx-auto w-full">
              <div className="relative aspect-[9/16] bg-ai-dark overflow-hidden">
                {videoErrors[short.id] ? (
                  // Show error state with direct link option
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-3 bg-ai-darker">
                    <div
                      className="w-full h-full bg-cover bg-center opacity-30"
                      style={{
                        backgroundImage: `url(${
                          thumbnailErrors[short.id]
                            ? FALLBACK_THUMBNAIL
                            : short.thumbnailUrl
                        })`,
                      }}
                    />

                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <p className="text-white text-xs mb-2 text-center">
                        Video playback not available in browser
                      </p>

                      <div className="space-y-2">
                        <a
                          href={short.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-xs px-3 py-1 bg-ai-accent text-white rounded text-center"
                        >
                          Watch in new tab
                        </a>

                        <button
                          onClick={() =>
                            downloadVideo(short.url, `short-${index + 1}.mp4`)
                          }
                          className="block w-full text-xs px-3 py-1 bg-ai-accent/80 text-white rounded"
                        >
                          Download video
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Main video player
                  <>
                    <video
                      className="w-full h-full object-cover"
                      controls
                      playsInline
                      preload="metadata"
                      poster={
                        thumbnailErrors[short.id]
                          ? FALLBACK_THUMBNAIL
                          : short.thumbnailUrl
                      }
                      onError={() => handleVideoError(short.id)}
                    >
                      <source src={short.url} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>

                    {/* Debugging URL display */}
                    <div className="absolute top-0 left-0 right-0 bg-black/70 text-[8px] text-white p-1 opacity-0 hover:opacity-100">
                      {short.url}
                    </div>
                  </>
                )}
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
                    Open video
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}

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
