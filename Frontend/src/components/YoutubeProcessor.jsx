import React, { useState, useEffect } from 'react';
import axios from 'axios';

const YouTubeProcessor = () => {
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [aspectRatio, setAspectRatio] = useState('9:16');
    const [wordsPerSubtitle, setWordsPerSubtitle] = useState(2);
    const [fontSize, setFontSize] = useState(36);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [videos, setVideos] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Poll for status updates when we have a job ID
    useEffect(() => {
        if (!jobId) return;

        const interval = setInterval(async () => {
            try {
                // Updated to use the new API endpoint
                const response = await axios.get(`/status/${jobId}`);
                setStatus(response.data);

                // Update videos when processing is complete
                if (response.data.status === 'completed' && response.data.output_file) {
                    // Create a download link for the processed video
                    setVideos([{
                        url: `/download/${jobId}`,
                        thumbnail: response.data.thumbnail || '',
                        title: `Processed video (${aspectRatio})`,
                        description: response.data.segment_info?.reasoning || 'Video processed successfully'
                    }]);
                    clearInterval(interval);
                    setIsLoading(false);
                }

                // Handle errors
                if (response.data.status === 'failed') {
                    setError(response.data.error || 'Processing failed');
                    clearInterval(interval);
                    setIsLoading(false);
                }
            } catch (err) {
                setError('Error checking job status');
                clearInterval(interval);
                setIsLoading(false);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [jobId, aspectRatio]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setVideos([]);

        try {
            // Updated to use the new API endpoint and parameter names
            const response = await axios.post('/generate-short', {
                youtube_url: youtubeUrl,     // Changed from youtubeUrl to youtube_url
                aspect_ratio: aspectRatio     // Changed from aspectRatio to aspect_ratio
                // Removed unused parameters: wordsPerSubtitle, fontSize
            });

            setJobId(response.data.job_id);   // Changed from jobId to job_id
        } catch (err) {
            setError('Failed to start processing');
            setIsLoading(false);
        }
    };

    return (
        <div className="youtube-processor">
            <h2>YouTube Shorts Generator</h2>

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="youtubeUrl">YouTube URL:</label>
                    <input
                        type="text"
                        id="youtubeUrl"
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                        placeholder="https://www.youtube.com/watch?v=..."
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="aspectRatio">Aspect Ratio:</label>
                    <select
                        id="aspectRatio"
                        value={aspectRatio}
                        onChange={(e) => setAspectRatio(e.target.value)}
                    >
                        <option value="9:16">9:16 (Vertical - Best for Shorts/TikTok/Reels)</option>
                        <option value="1:1">1:1 (Square - Instagram)</option>
                        <option value="4:5">4:5 (Vertical - Instagram)</option>
                    </select>
                </div>

                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Generate Short'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            {status && (
                <div className="status">
                    <h3>Processing Status</h3>
                    <p>Status: {status.status}</p>
                    <p>Progress: {status.progress}%</p>
                    <div className="progress-bar">
                        <div
                            className="progress"
                            style={{ width: `${status.progress}%` }}
                        ></div>
                    </div>
                </div>
            )}

            {videos.length > 0 && (
                <div className="videos">
                    <h3>Generated Videos</h3>
                    <div className="video-list">
                        {videos.map((video, index) => (
                            <div className="video-item" key={index}>
                                {video.thumbnail && (
                                    <img src={video.thumbnail} alt={video.title} />
                                )}
                                <h4>{video.title}</h4>
                                <p>{video.description}</p>
                                <a
                                    href={video.url}
                                    download
                                    className="download-btn"
                                >
                                    Download Video
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default YouTubeProcessor;