import React, { useState } from "react";
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { YouTube } from "lucide-react";

const TrendAnalysis = () => {
  const [youtubeLink, setYoutubeLink] = useState("");
  const [isValidLink, setIsValidLink] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const validateYoutubeLink = (link: string) => {
    const regex =
      /^(https?\:\/\/)?(www\.youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/|www\.youtube\.com\/shorts\/|youtube\.com\/embed\/|www\.youtube\.com\/embed\/)([a-zA-Z0-9\-_]{11})(.*)$/;
    return regex.test(link);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!youtubeLink) {
      setIsValidLink(false);
      setErrorMessage("Please enter a YouTube link");
      return;
    }

    if (!validateYoutubeLink(youtubeLink)) {
      setIsValidLink(false);
      setErrorMessage("Please enter a valid YouTube video URL");
      return;
    }

    setIsValidLink(true);
    setErrorMessage("");
    setIsProcessing(true);

    try {
      const response = await fetch("/api/analyze-trend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ youtubeUrl: youtubeLink }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to analyze trend");
      }

      setResult(data);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "An error occurred"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-ai-dark flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-6">
            YouTube Trend Analysis
          </h1>
          <p className="text-ai-muted mb-8">
            Analyze YouTube videos to determine if they're trending based on
            content and keywords.
          </p>

          <div className="p-6 rounded-lg bg-ai-light/20 border border-ai-border mb-10">
            <form onSubmit={handleSubmit}>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-grow">
                  <label htmlFor="youtubeLink" className="sr-only">
                    YouTube Link
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <YouTube className="h-5 w-5 text-ai-muted" />
                    </div>
                    <input
                      type="text"
                      id="youtubeLink"
                      className={`block w-full pl-10 rounded-lg border ${
                        !isValidLink ? "border-red-500" : "border-ai-border"
                      } bg-ai-light/30 p-3 text-white placeholder:text-ai-muted focus:outline-none focus:ring-2 focus:ring-ai-accent`}
                      placeholder="Paste YouTube link here"
                      value={youtubeLink}
                      onChange={(e) => setYoutubeLink(e.target.value)}
                    />
                  </div>
                  {!isValidLink && (
                    <p className="mt-2 text-sm text-red-400">{errorMessage}</p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="px-5 py-3 text-white bg-ai-accent hover:bg-ai-accent/80 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <span className="flex items-center">
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    "Analyze"
                  )}
                </button>
              </div>
            </form>
          </div>

          {errorMessage && !isValidLink && (
            <div className="p-4 mb-8 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
              {errorMessage}
            </div>
          )}

          {result && (
            <div className="animate-in fade-in duration-300">
              <div className="p-6 rounded-lg bg-ai-light/20 border border-ai-border mb-6">
                <h2 className="text-xl font-semibold text-white mb-2">
                  {result.title}
                </h2>
                <p className="text-ai-muted mb-4">{result.description}</p>

                <div className="mt-6 p-4 rounded-lg bg-ai-dark/50">
                  <div className="flex items-center mb-3">
                    <h3 className="text-lg font-medium text-white">
                      Trend Analysis
                    </h3>
                    <span className="ml-3 text-lg font-bold text-ai-accent">
                      {result.trendRating}
                    </span>
                  </div>
                  <p className="text-ai-muted">{result.reason}</p>
                </div>

                <div className="mt-6">
                  <iframe
                    width="100%"
                    height="315"
                    src={`https://www.youtube.com/embed/${result.videoId}`}
                    title="YouTube video player"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="rounded-lg"
                  ></iframe>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default TrendAnalysis;
