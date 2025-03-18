// Mock implementation for video processing and upload
// In a real application, this would connect to your backend service

/**
 * Process a YouTube video link
 * @param youtubeLink The YouTube video URL to process
 * @returns Promise that resolves when processing is complete
 */
export const processYoutubeLink = async (youtubeLink: string): Promise<any> => {
  console.log(`Processing YouTube link: ${youtubeLink}`);

  try {
    // Send request to your backend
    const response = await fetch('/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        youtubeUrl: youtubeLink,
        aspectRatio: '9:16',
        wordsPerSubtitle: 2,
        fontSize: 36
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error processing YouTube link:', errorData);
      throw new Error(errorData.error || 'Failed to process YouTube video');
    }

    const data = await response.json();
    console.log('Processing started:', data);

    // Return the job ID for status polling
    return {
      jobId: data.jobId,
      status: 'processing'
    };
  } catch (error) {
    console.error('Error calling backend:', error);
    throw error;
  }
};

/**
 * Poll for job status
 * @param jobId The job ID to check
 * @returns Promise that resolves to the current job status
 */
export const getJobStatus = async (jobId: string): Promise<any> => {
  try {
    const response = await fetch(`/status/${jobId}`);
    if (!response.ok) {
      throw new Error('Failed to get job status');
    }
    return response.json();
  } catch (error) {
    console.error('Error checking job status:', error);
    throw error;
  }
};

/**
 * Upload a video file with progress tracking
 * @param file The video file to upload
 * @param onProgress Callback function to report upload progress
 * @returns Promise that resolves when upload and processing is complete
 */
export const uploadVideoFile = async (
  file: File,
  onProgress: (progress: number) => void
): Promise<boolean> => {
  // This is a mock implementation
  console.log(`Uploading file: ${file.name} (${file.size} bytes)`);

  // Simulate upload with progress updates
  return new Promise((resolve, reject) => {
    let progress = 0;
    const totalSteps = 20;

    const interval = setInterval(() => {
      progress += 5;
      onProgress(progress);

      if (progress >= 100) {
        clearInterval(interval);

        // Simulate processing delay after upload completes
        setTimeout(() => {
          // Randomly succeed or fail for demo purposes
          const success = Math.random() > 0.2; // 80% success rate

          if (success) {
            resolve(true);
          } else {
            reject(new Error('Failed to process uploaded video. Please try again.'));
          }
        }, 1000);
      }
    }, 300); // Update progress every 300ms
  });
};

// Sample data for generated shorts
const sampleShorts = [
  {
    id: "short-1",
    title: "Best moments from your video",
    thumbnailUrl: "https://picsum.photos/id/237/640/360",
    videoUrl: "https://example.com/shorts/1",
    duration: "0:30"
  },
  {
    id: "short-2",
    title: "Highlights and key insights",
    thumbnailUrl: "https://picsum.photos/id/238/640/360",
    videoUrl: "https://example.com/shorts/2",
    duration: "0:45"
  },
  {
    id: "short-3",
    title: "Quick takeaway from your content",
    thumbnailUrl: "https://picsum.photos/id/239/640/360",
    videoUrl: "https://example.com/shorts/3",
    duration: "0:25"
  },
  {
    id: "short-4",
    title: "Focus on this important point",
    thumbnailUrl: "https://picsum.photos/id/240/640/360",
    videoUrl: "https://example.com/shorts/4",
    duration: "0:35"
  }
];

/**
 * Get generated shorts for a processed video
 * This is a mock implementation that would be replaced with an actual API call
 */
export const getGeneratedShorts = async () => {
  // Simulate API call with delay
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(sampleShorts);
    }, 1000);
  });
};
