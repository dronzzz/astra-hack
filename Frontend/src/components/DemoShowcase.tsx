
import { useState, useEffect } from 'react';
import { Play, Pause, Code } from 'lucide-react';

const DemoShowcase = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('shorts');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    const element = document.getElementById('demo');
    if (element) {
      observer.observe(element);
    }

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, []);

  return (
    <section id="demo" className="py-20 relative">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-ai-blue/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-ai-purple/5 rounded-full blur-3xl"></div>
      </div>

      <div className="section-container">
        <div className="mb-12 text-center relative z-10">
          <h2 className="section-title">
            See Our <span className="gradient-heading">AI in Action</span>
          </h2>
          <p className="section-subtitle">
            Watch how our platform transforms lengthy videos into engaging shorts and ad creatives in minutes.
          </p>
        </div>

        <div 
          id="demo"
          className={`max-w-5xl mx-auto transition-all duration-1000 transform ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="bg-ai-light rounded-xl overflow-hidden border border-ai-blue/20 shadow-lg shadow-ai-blue/5">
            <div className="p-4 bg-ai-darker border-b border-ai-lighter/20 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center">
                <button 
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                    activeTab === 'shorts' 
                      ? 'bg-ai-blue text-ai-darker' 
                      : 'bg-ai-lighter hover:bg-ai-light text-ai-text'
                  }`}
                  onClick={() => setActiveTab('shorts')}
                >
                  YouTube Shorts
                </button>
                <button 
                  className={`ml-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                    activeTab === 'ads' 
                      ? 'bg-ai-purple text-ai-darker' 
                      : 'bg-ai-lighter hover:bg-ai-light text-ai-text'
                  }`}
                  onClick={() => setActiveTab('ads')}
                >
                  Google Ads
                </button>
              </div>
              
              <div className="flex items-center">
                <div className="flex items-center bg-ai-lighter/70 rounded-full px-3 py-1 border border-ai-blue/20">
                  <span className="text-xs font-medium text-ai-text">AI-Generated Content</span>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-6">
              {/* Original Video */}
              <div className="space-y-4">
                <div className="text-sm font-medium text-center">Original Long-Form Video</div>
                <div className="aspect-video bg-ai-darker rounded-lg overflow-hidden border border-ai-lighter/20 relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-ai-purple/20 via-transparent to-ai-blue/20 flex items-center justify-center">
                    <button 
                      className="w-16 h-16 rounded-full bg-ai-blue/20 flex items-center justify-center transition-all duration-300 transform group-hover:scale-110"
                      onClick={() => setIsPlaying(!isPlaying)}
                    >
                      {isPlaying ? (
                        <Pause fill="currentColor" className="text-ai-blue" size={28} />
                      ) : (
                        <Play fill="currentColor" className="text-ai-blue ml-1" size={28} />
                      )}
                    </button>
                  </div>
                  <div className="absolute bottom-4 left-4 right-4 bg-ai-darker/80 backdrop-blur-sm p-2 rounded-md border border-ai-lighter/20">
                    <div className="text-xs text-ai-muted">Full Video • 15:32</div>
                    <div className="mt-1 h-1 bg-ai-lighter rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-ai-accent to-ai-accent2"
                        style={{ width: isPlaying ? '45%' : '0%', transition: 'width 1s linear' }}
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 border border-ai-blue/10 rounded-lg bg-ai-blue/5">
                  <div className="mb-2 text-sm font-medium">Original Video Stats</div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">Duration</div>
                      <div className="font-medium">15:32</div>
                    </div>
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">File Size</div>
                      <div className="font-medium">287 MB</div>
                    </div>
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">Resolution</div>
                      <div className="font-medium">1920×1080</div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* AI-Generated Content */}
              <div className="space-y-4">
                <div className="text-sm font-medium text-center">
                  AI-Generated {activeTab === 'shorts' ? 'YouTube Short' : 'Google Ad'}
                </div>
                <div className="relative">
                  {activeTab === 'shorts' ? (
                    <div className="aspect-[9/16] max-w-[250px] mx-auto bg-ai-darker rounded-lg overflow-hidden border border-ai-lighter/20 relative group">
                      <div className="absolute inset-0 bg-gradient-to-br from-ai-blue/20 via-transparent to-ai-purple/20 flex items-center justify-center">
                        <button 
                          className="w-12 h-12 rounded-full bg-ai-accent/20 flex items-center justify-center transition-all duration-300 transform group-hover:scale-110"
                          onClick={() => setIsPlaying(!isPlaying)}
                        >
                          {isPlaying ? (
                            <Pause fill="currentColor" className="text-ai-accent" size={20} />
                          ) : (
                            <Play fill="currentColor" className="text-ai-accent ml-1" size={20} />
                          )}
                        </button>
                      </div>
                      <div className="absolute top-4 left-4 right-4 bg-ai-darker/80 backdrop-blur-sm py-1 px-2 rounded-md border border-ai-lighter/20 flex items-center">
                        <div className="w-6 h-6 rounded-full bg-ai-blue/20 flex items-center justify-center mr-2">
                          <Code className="text-ai-blue" size={12} />
                        </div>
                        <div className="text-xs">AI-Generated Short</div>
                      </div>
                      <div className="absolute bottom-4 left-4 right-4 bg-ai-darker/80 backdrop-blur-sm p-2 rounded-md border border-ai-lighter/20">
                        <div className="text-xs text-ai-muted">Short • 00:42</div>
                        <div className="mt-1 h-1 bg-ai-lighter rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-ai-accent to-ai-accent2"
                            style={{ width: isPlaying ? '60%' : '0%', transition: 'width 1s linear' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="aspect-video bg-ai-darker rounded-lg overflow-hidden border border-ai-lighter/20 relative group">
                      <div className="absolute inset-0 bg-gradient-to-br from-ai-purple/20 via-transparent to-ai-blue/20 flex items-center justify-center">
                        <button 
                          className="w-12 h-12 rounded-full bg-ai-purple/20 flex items-center justify-center transition-all duration-300 transform group-hover:scale-110"
                          onClick={() => setIsPlaying(!isPlaying)}
                        >
                          {isPlaying ? (
                            <Pause fill="currentColor" className="text-ai-purple" size={20} />
                          ) : (
                            <Play fill="currentColor" className="text-ai-purple ml-1" size={20} />
                          )}
                        </button>
                      </div>
                      <div className="absolute top-4 left-4 right-4 bg-ai-darker/80 backdrop-blur-sm py-1 px-2 rounded-md border border-ai-lighter/20 flex items-center">
                        <div className="w-6 h-6 rounded-full bg-ai-purple/20 flex items-center justify-center mr-2">
                          <Code className="text-ai-purple" size={12} />
                        </div>
                        <div className="text-xs">AI-Generated Ad</div>
                      </div>
                      <div className="absolute bottom-4 left-4 right-4 bg-ai-darker/80 backdrop-blur-sm p-2 rounded-md border border-ai-lighter/20">
                        <div className="text-xs text-ai-muted">Ad Creative • 00:30</div>
                        <div className="mt-1 h-1 bg-ai-lighter rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-ai-purple to-ai-blue"
                            style={{ width: isPlaying ? '75%' : '0%', transition: 'width 1s linear' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="p-4 border border-ai-blue/10 rounded-lg bg-ai-blue/5">
                  <div className="mb-2 text-sm font-medium">AI-Generated Content Stats</div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">Duration</div>
                      <div className="font-medium">{activeTab === 'shorts' ? '00:42' : '00:30'}</div>
                    </div>
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">File Size</div>
                      <div className="font-medium">{activeTab === 'shorts' ? '12 MB' : '8 MB'}</div>
                    </div>
                    <div className="p-2 bg-ai-darker rounded border border-ai-lighter/20">
                      <div className="text-ai-muted">Platform</div>
                      <div className="font-medium">{activeTab === 'shorts' ? 'YouTube' : 'Google Ads'}</div>
                    </div>
                  </div>
                </div>

                <div className="p-4 border border-ai-accent/10 rounded-lg bg-gradient-to-r from-ai-accent/5 to-transparent">
                  <div className="text-sm font-medium mb-2">AI Enhancement</div>
                  <div className="text-xs text-ai-muted">
                    {activeTab === 'shorts' 
                      ? 'Our AI has identified the most engaging 42 seconds from your 15-minute video and optimized it for the vertical format with auto-captions and enhanced audio.'
                      : 'The AI has created a 30-second ad creative optimized for Google Ads with a clear CTA, highlighting the key benefits from your original content.'}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-ai-darker border-t border-ai-lighter/20 flex justify-center">
              <button className="ai-btn-primary">
                Try With Your Content
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoShowcase;
