import React from "react";
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen bg-ai-dark flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Create Engaging Short Videos with AI
          </h1>
          <p className="text-xl text-ai-muted mb-10">
            Transform long YouTube videos into engaging shorts with AI-powered
            face tracking and subtitles
          </p>

          <div className="flex flex-col md:flex-row gap-4 justify-center mt-10">
            <Link
              to="/upload"
              className="px-8 py-4 bg-ai-accent text-white rounded-lg font-medium hover:bg-ai-accent/80 transition-colors"
            >
              Create Shorts
            </Link>
            <Link
              to="/trend-analysis"
              className="px-8 py-4 bg-ai-light/30 text-white rounded-lg font-medium hover:bg-ai-light/40 transition-colors"
            >
              Analyze Trends
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Home;
