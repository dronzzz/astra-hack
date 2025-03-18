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
                const response = await axios.get(`/status/${jobId}`);
                setStatus(response.data);

                // Update videos when processing is complete
                if (response.data.status === 'completed' && response.data.videos) {
                    setVideos(response.data.videos);
                    clearInterval(interval);
                    setIsLoading(false);
                }

                // Handle errors
                if (response.data.status === 'error') {
                    setError(response.data.message);
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
    }, [jobId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setVideos([]);

        try {
            const response = await axios.post('/api/process-youtube', {
                youtubeUrl,
                aspectRatio,
                wordsPerSubtitle,
                fontSize
            });

            setJobId(response.data.jobId);
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

                <div className="form-group">
                    <label htmlFor="wordsPerSubtitle">Words Per Subtitle:</label>
                    <input
                        type="number"
                        id="wordsPerSubtitle"
                        value={wordsPerSubtitle}
                        onChange={(e) => setWordsPerSubtitle(parseInt(e.target.value))}
                        min="1"
                        max="10"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="fontSize">Font Size:</label>
                    <input
                        type="number"
                        id="fontSize"
                        value={fontSize}
                        onChange={(e) => setFontSize(parseInt(e.target.value))}
                        min="12"
                        max="72"
                    />
                </div>

                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Generate Shorts'}
                </button>
            </form>

            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}

            {status && status.status === 'processing' && (
                <div className="processing-status">
                    <h3>Processing: {status.progress}%</h3>
                    <p>{status.message}</p>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${status.progress}%` }}
                        ></div>
                    </div>
                </div>
            )}

            {videos.length > 0 && (
                <div className="generated-videos">
                    <h3>Generated Shorts</h3>
                    <div className="video-grid">
                        {videos.map((video, index) => (
                            <div key={index} className="video-item">
                                <h4>Short {index + 1}</h4>
                                <p><strong>Reason:</strong> {video.segment.reason}</p>
                                <video
                                    controls
                                    src={video.url}
                                    style={{ width: '100%', maxWidth: '400px' }}
                                />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default YouTubeProcessor;