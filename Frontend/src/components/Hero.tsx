
import { ArrowRight, Zap } from 'lucide-react';
import { useState, useEffect } from 'react';

const Hero = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="min-h-screen flex items-center justify-center pt-16 overflow-hidden relative">
      {/* Background elements */}
      <div className="absolute top-1/3 left-1/4 w-64 h-64 bg-ai-accent/5 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-ai-purple/5 rounded-full blur-3xl"></div>
      
      <div className="section-container">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div 
            className={`transition-all duration-1000 transform ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`}
          >
            <div className="inline-flex items-center bg-ai-lighter/70 rounded-full pl-2 pr-4 py-1 mb-6 border border-ai-blue/20">
              <span className="bg-ai-blue/20 rounded-full p-1 mr-2">
                <Zap size={16} className="text-ai-blue" />
              </span>
              <span className="text-sm font-medium">AI-Powered Content Automation</span>
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6 leading-tight">
              <span className="gradient-heading">Transform</span> Long Videos into <span className="gradient-heading">Engaging Shorts & Ads</span>
            </h1>
            <p className="text-xl mb-8 text-ai-muted">
              Our AI platform automatically identifies key moments in your videos and transforms them into high-performing YouTube Shorts and Google Ads creatives.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="ai-btn-primary flex items-center justify-center">
                Get Started Free
                <ArrowRight size={18} className="ml-2" />
              </button>
              <button className="ai-btn-secondary flex items-center justify-center">
                Watch Demo
              </button>
            </div>
            <div className="mt-8 p-4 border border-ai-blue/10 rounded-lg bg-ai-blue/5 flex items-start">
              <div className="text-ai-blue mr-2 mt-1">
                <Zap size={16} />
              </div>
              <p className="text-sm text-ai-muted">
                <span className="text-ai-text font-medium">Boost engagement by 300%</span> - Our AI technology automatically identifies the most engaging moments from your videos.
              </p>
            </div>
          </div>

          <div 
            className={`relative transition-all duration-1000 delay-300 transform ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`}
          >
            <div className="rounded-xl overflow-hidden border border-ai-blue/20 shadow-xl shadow-ai-blue/5 relative aspect-video">
              <div className="absolute inset-0 bg-gradient-to-br from-ai-purple/20 via-transparent to-ai-blue/20"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="glass-card p-6 w-11/12 h-5/6 overflow-hidden relative">
                  <div className="absolute top-0 left-0 right-0 h-10 bg-ai-darker flex items-center px-4">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <div className="ml-4 text-xs text-ai-muted">AI Content Generator</div>
                  </div>
                  <div className="mt-10 h-[calc(100%-2.5rem)] overflow-y-auto p-2">
                    <div className="space-y-3">
                      <div className="h-8 bg-ai-lighter rounded-md w-3/4 shimmer-effect"></div>
                      <div className="h-8 bg-ai-lighter rounded-md w-1/2 shimmer-effect"></div>
                      <div className="h-24 bg-ai-lighter rounded-md w-full mt-6 shimmer-effect"></div>
                      <div className="grid grid-cols-3 gap-3 mt-6">
                        <div className="h-20 bg-ai-lighter rounded-md shimmer-effect"></div>
                        <div className="h-20 bg-ai-lighter rounded-md shimmer-effect"></div>
                        <div className="h-20 bg-ai-lighter rounded-md shimmer-effect"></div>
                      </div>
                      <div className="h-8 bg-ai-accent/20 rounded-md w-40 mt-6 flex items-center justify-center">
                        <div className="text-ai-blue text-sm font-medium">Processing...</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating elements */}
            <div className="absolute -top-6 -right-6 animate-float">
              <div className="bg-ai-light p-3 rounded-lg shadow-lg border border-ai-blue/20">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-ai-blue rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium">AI Analyzing Video</span>
                </div>
              </div>
            </div>
            <div className="absolute -bottom-4 -left-4 animate-float delay-700">
              <div className="bg-ai-light p-3 rounded-lg shadow-lg border border-ai-purple/20">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-ai-purple rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium">Content Generated</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
