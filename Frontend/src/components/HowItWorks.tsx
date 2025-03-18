
import { useEffect, useState } from 'react';
import { ArrowRight, Upload, Sparkles, Play, Download } from 'lucide-react';

const HowItWorks = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  const steps = [
    {
      title: 'Input Your Content',
      description: 'Upload your long-form video or paste a YouTube link for the AI to analyze.',
      icon: <Upload className="h-6 w-6" />
    },
    {
      title: 'AI Identifies Key Moments',
      description: 'Our advanced algorithms analyze your content to find the most engaging moments.',
      icon: <Sparkles className="h-6 w-6" />
    },
    {
      title: 'Generate Optimized Content',
      description: 'Automatically create shorts and ad creatives optimized for each platform.',
      icon: <Play className="h-6 w-6" />
    },
    {
      title: 'Export & Publish',
      description: 'Download your new content or publish directly to your connected platforms.',
      icon: <Download className="h-6 w-6" />
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    const element = document.getElementById('how-it-works');
    if (element) {
      observer.observe(element);
    }

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <section id="how-it-works" className="py-20 bg-ai-darker relative">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
        <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-ai-blue/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/3 left-1/4 w-64 h-64 bg-ai-purple/5 rounded-full blur-3xl"></div>
      </div>

      <div className="section-container">
        <div className="mb-12 text-center relative z-10">
          <h2 className="section-title">
            How It <span className="gradient-heading">Works</span>
          </h2>
          <p className="section-subtitle">
            Our streamlined process makes content creation effortless. Just follow these simple steps to transform your videos.
          </p>
        </div>

        <div 
          id="how-it-works"
          className={`relative z-10 transition-all duration-1000 transform ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          {/* Steps Progress Indicator */}
          <div className="flex justify-between items-center mb-12 max-w-4xl mx-auto px-6">
            {steps.map((step, index) => (
              <div key={index} className="flex flex-col items-center relative">
                <div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center z-10 transition-all duration-500 ${
                    index <= activeStep 
                      ? 'bg-gradient-to-r from-ai-accent to-ai-accent2 shadow-lg shadow-ai-accent/20' 
                      : 'bg-ai-light border border-ai-blue/20'
                  }`}
                >
                  <div 
                    className={`transition-colors duration-500 ${
                      index <= activeStep ? 'text-ai-darker' : 'text-ai-blue'
                    }`}
                  >
                    {step.icon}
                  </div>
                </div>
                
                {/* Step number label */}
                <div className="mt-3 text-xs font-medium text-ai-muted">Step {index + 1}</div>
                
                {/* Progress Line */}
                {index < steps.length - 1 && (
                  <div className="absolute left-[calc(100%+0.75rem)] top-6 w-[calc(100%-3rem)] h-0.5 transform -translate-y-1/2">
                    <div className="h-full bg-ai-light/30 relative">
                      <div 
                        className="absolute top-0 left-0 h-full bg-gradient-to-r from-ai-accent to-ai-accent2 transition-all duration-500"
                        style={{ 
                          width: index < activeStep ? '100%' : index === activeStep ? '50%' : '0%' 
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Active Step Detail */}
          <div className="glass-card max-w-4xl mx-auto border border-ai-blue/20 p-8 shadow-lg shadow-ai-blue/5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-bold mb-4">
                  <span className="gradient-heading">{steps[activeStep].title}</span>
                </h3>
                <p className="text-ai-muted mb-6">
                  {steps[activeStep].description}
                </p>
                
                <div className="bg-ai-darker p-4 rounded-lg border border-ai-lighter/20 mb-6">
                  <h4 className="text-sm font-medium mb-2 text-ai-text">Pro Tip</h4>
                  <p className="text-xs text-ai-muted">
                    {activeStep === 0 && "Videos longer than 10 minutes typically yield the best results for short-form content generation."}
                    {activeStep === 1 && "Our AI can detect patterns in your content that engage viewers the most based on historical performance data."}
                    {activeStep === 2 && "Create multiple variations of the same content to A/B test which format works best for your audience."}
                    {activeStep === 3 && "Schedule your content to be published at optimal times based on your audience's activity patterns."}
                  </p>
                </div>
                
                <button className="ai-btn-primary flex items-center">
                  {activeStep === steps.length - 1 ? 'Get Started Now' : 'Continue to Next Step'}
                  <ArrowRight size={16} className="ml-2" />
                </button>
              </div>
              
              {/* Step Visualization */}
              <div className="relative">
                {activeStep === 0 && (
                  <div className="bg-ai-light rounded-lg p-4 border border-ai-lighter animate-fade-in-up">
                    <div className="flex items-center mb-4">
                      <Upload className="text-ai-blue mr-2" size={18} />
                      <div className="text-sm font-medium">Upload Video or Paste Link</div>
                    </div>
                    <div className="border-dashed border-2 border-ai-blue/30 rounded-lg p-6 flex flex-col items-center justify-center">
                      <div className="w-16 h-16 rounded-full bg-ai-blue/10 flex items-center justify-center mb-4">
                        <Upload className="text-ai-blue" size={24} />
                      </div>
                      <p className="text-sm text-ai-muted text-center mb-3">
                        Drag and drop your video file here or paste a YouTube URL
                      </p>
                      <div className="w-full bg-ai-lighter rounded-lg p-2 text-sm text-ai-muted text-center">
                        https://youtube.com/watch?v=...
                      </div>
                    </div>
                  </div>
                )}
                
                {activeStep === 1 && (
                  <div className="bg-ai-light rounded-lg p-4 border border-ai-lighter animate-fade-in-up">
                    <div className="flex items-center mb-4">
                      <Sparkles className="text-ai-blue mr-2" size={18} />
                      <div className="text-sm font-medium">AI Analyzing Content</div>
                    </div>
                    <div className="space-y-4">
                      <div className="h-3 bg-ai-lighter rounded-full overflow-hidden">
                        <div className="h-full w-3/4 bg-gradient-to-r from-ai-accent to-ai-accent2 shimmer-effect"></div>
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <div className="aspect-video bg-ai-lighter rounded-md overflow-hidden relative">
                          <div className="absolute inset-0 bg-ai-blue/10 flex items-center justify-center">
                            <div className="w-6 h-6 rounded-full bg-ai-accent/20 flex items-center justify-center">
                              <Sparkles className="text-ai-accent" size={12} />
                            </div>
                          </div>
                        </div>
                        <div className="aspect-video bg-ai-lighter rounded-md overflow-hidden relative">
                          <div className="absolute inset-0 bg-ai-purple/10 flex items-center justify-center">
                            <div className="w-6 h-6 rounded-full bg-ai-blue/20 flex items-center justify-center">
                              <Sparkles className="text-ai-blue" size={12} />
                            </div>
                          </div>
                        </div>
                        <div className="aspect-video bg-ai-lighter rounded-md"></div>
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <div className="aspect-video bg-ai-lighter rounded-md"></div>
                        <div className="aspect-video bg-ai-lighter rounded-md overflow-hidden relative">
                          <div className="absolute inset-0 bg-ai-accent/10 flex items-center justify-center">
                            <div className="w-6 h-6 rounded-full bg-ai-blue/20 flex items-center justify-center">
                              <Sparkles className="text-ai-blue" size={12} />
                            </div>
                          </div>
                        </div>
                        <div className="aspect-video bg-ai-lighter rounded-md"></div>
                      </div>
                    </div>
                  </div>
                )}
                
                {activeStep === 2 && (
                  <div className="bg-ai-light rounded-lg p-4 border border-ai-lighter animate-fade-in-up">
                    <div className="flex items-center mb-4">
                      <Play className="text-ai-blue mr-2" size={18} />
                      <div className="text-sm font-medium">Generating Optimized Content</div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="text-xs text-ai-muted">YouTube Shorts</div>
                        <div className="aspect-[9/16] bg-ai-darker rounded-md p-2 border border-ai-lighter/20">
                          <div className="w-full h-full bg-gradient-to-br from-ai-blue/20 to-ai-purple/20 rounded flex items-center justify-center">
                            <div className="w-10 h-10 rounded-full bg-ai-blue/20 flex items-center justify-center animate-pulse-glow">
                              <Play fill="currentColor" className="text-ai-blue" size={20} />
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs text-ai-muted">Google Ad Creative</div>
                        <div className="aspect-video bg-ai-darker rounded-md p-2 border border-ai-lighter/20">
                          <div className="w-full h-full bg-gradient-to-br from-ai-purple/20 to-ai-blue/20 rounded flex items-center justify-center">
                            <div className="w-10 h-10 rounded-full bg-ai-purple/20 flex items-center justify-center animate-pulse-glow">
                              <Play fill="currentColor" className="text-ai-purple" size={20} />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-4 h-3 bg-ai-lighter rounded-full overflow-hidden">
                      <div className="h-full w-2/3 bg-gradient-to-r from-ai-accent to-ai-accent2 shimmer-effect"></div>
                    </div>
                    <div className="mt-2 text-xs text-center text-ai-muted">
                      Finalizing content optimization...
                    </div>
                  </div>
                )}
                
                {activeStep === 3 && (
                  <div className="bg-ai-light rounded-lg p-4 border border-ai-lighter animate-fade-in-up">
                    <div className="flex items-center mb-4">
                      <Download className="text-ai-blue mr-2" size={18} />
                      <div className="text-sm font-medium">Export & Publish</div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between bg-ai-darker p-3 rounded-lg border border-ai-lighter/20">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-ai-blue/10 rounded flex items-center justify-center mr-3">
                            <Play className="text-ai-blue" size={14} />
                          </div>
                          <div>
                            <div className="text-sm">YouTube_Short_1.mp4</div>
                            <div className="text-xs text-ai-muted">12MB · 00:58</div>
                          </div>
                        </div>
                        <button className="bg-ai-blue/10 hover:bg-ai-blue/20 p-2 rounded">
                          <Download className="text-ai-blue" size={14} />
                        </button>
                      </div>
                      
                      <div className="flex items-center justify-between bg-ai-darker p-3 rounded-lg border border-ai-lighter/20">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-ai-purple/10 rounded flex items-center justify-center mr-3">
                            <Play className="text-ai-purple" size={14} />
                          </div>
                          <div>
                            <div className="text-sm">Google_Ad_Creative.mp4</div>
                            <div className="text-xs text-ai-muted">8MB · 00:30</div>
                          </div>
                        </div>
                        <button className="bg-ai-blue/10 hover:bg-ai-blue/20 p-2 rounded">
                          <Download className="text-ai-blue" size={14} />
                        </button>
                      </div>
                      
                      <button className="w-full p-3 bg-ai-lighter hover:bg-ai-light border border-ai-blue/20 rounded-lg flex items-center justify-center">
                        <span className="text-sm font-medium mr-2">Publish Directly to Platforms</span>
                        <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
