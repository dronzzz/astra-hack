import React, { useState } from "react";

export function TrendAnalyzer() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [isValidUrl, setIsValidUrl] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const validateYoutubeUrl = (url: string) => {
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return pattern.test(url);
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setYoutubeUrl(url);
    setIsValidUrl(url === "" || validateYoutubeUrl(url));
  };

  const handleAnalyze = async () => {
    if (!validateYoutubeUrl(youtubeUrl)) {
      setIsValidUrl(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/analyze-trend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ youtubeUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to analyze video");
      }

      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6 text-white">
        YouTube Trend Analyzer
      </h1>

      <div className="mb-8">
        <div className="mb-4">
          <label
            htmlFor="youtube-url"
            className="block text-sm font-medium mb-2 text-ai-muted"
          >
            YouTube Video URL
          </label>
          <input
            id="youtube-url"
            type="text"
            className={`w-full p-3 rounded-lg bg-ai-light border ${
              !isValidUrl ? "border-red-500" : "border-ai-border"
            } text-white focus:outline-none focus:ring-2 focus:ring-ai-accent`}
            value={youtubeUrl}
            onChange={handleUrlChange}
            placeholder="https://www.youtube.com/watch?v=..."
          />
          {!isValidUrl && (
            <p className="mt-1 text-sm text-red-500">
              Please enter a valid YouTube URL
            </p>
          )}
        </div>
        <button
          className={`px-4 py-2 rounded-lg font-medium ${
            isLoading
              ? "bg-ai-lighter text-ai-muted"
              : "bg-ai-accent text-white hover:bg-ai-accent/80"
          } transition-colors`}
          onClick={handleAnalyze}
          disabled={isLoading || !youtubeUrl || !isValidUrl}
        >
          {isLoading ? (
            <>
              <span className="inline-block animate-spin mr-2">⟳</span>
              Analyzing...
            </>
          ) : (
            "Analyze Trend Potential"
          )}
        </button>
      </div>

      {error && (
        <div className="p-4 mb-6 rounded-lg bg-red-900/30 border border-red-800 text-red-200">
          <h3 className="font-medium mb-2">Error</h3>
          <p>{error}</p>
        </div>
      )}

      {analysis && (
        <div className="p-6 rounded-lg bg-ai-light/20 border border-ai-border">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            {analysis.thumbnailUrl && (
              <div className="md:w-1/3 lg:w-1/4">
                <img
                  src={analysis.thumbnailUrl}
                  alt={analysis.title}
                  className="w-full rounded-lg"
                />
              </div>
            )}
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-white mb-2">
                {analysis.title}
              </h2>
              <p className="text-ai-muted">{analysis.description}</p>
            </div>
          </div>

          <div className="h-px bg-ai-border my-6"></div>

          <div className="mb-6">
            <h3 className="text-lg font-medium text-white mb-4">
              Trend Analysis: {analysis.trendAnalysis.status}
            </h3>

            <div className="flex items-center mb-4">
              <div className="relative w-16 h-16 mr-4">
                <svg className="w-full h-full" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#444"
                    strokeWidth="3"
                    strokeDasharray="100, 100"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke={
                      analysis.trendAnalysis.rating > 70
                        ? "#22c55e"
                        : analysis.trendAnalysis.rating > 40
                        ? "#eab308"
                        : "#ef4444"
                    }
                    strokeWidth="3"
                    strokeDasharray={`${analysis.trendAnalysis.rating}, 100`}
                  />
                  <text
                    x="18"
                    y="21"
                    textAnchor="middle"
                    fill="#fff"
                    fontSize="8px"
                    fontWeight="bold"
                  >
                    {analysis.trendAnalysis.rating}%
                  </text>
                </svg>
              </div>
              <p className="text-white">{analysis.trendAnalysis.reason}</p>
            </div>
          </div>

          <div className="mb-4">
            <h4 className="text-sm font-medium text-ai-muted mb-2">
              Current Trending Keywords:
            </h4>
            <div className="flex flex-wrap gap-2">
              {analysis.trendAnalysis.keywords.map(
                (keyword: string, index: number) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs rounded-full bg-ai-accent/20 text-ai-accent border border-ai-accent/30"
                  >
                    {keyword}
                  </span>
                )
              )}
            </div>
          </div>

          <div>
            <p className="text-ai-muted mb-1">
              <span className="font-medium">Keyword Matches:</span>{" "}
              {analysis.trendAnalysis.keyword_matches}
            </p>
            <p className="text-ai-muted">
              <span className="font-medium">Sentiment Score:</span>{" "}
              {analysis.trendAnalysis.sentiment_score.toFixed(2)}
              <span className="ml-1">
                {analysis.trendAnalysis.sentiment_score > 0.3
                  ? "(Positive)"
                  : analysis.trendAnalysis.sentiment_score < -0.3
                  ? "(Negative)"
                  : "(Neutral)"}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrendAnalyzer;
