
import { useState, useEffect } from 'react';
import { Zap, Video, BarChart3, Clock, Search, PenTool } from 'lucide-react';

const Features = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  const features = [
    {
      title: 'AI Video Analysis',
      description: 'Our advanced algorithms analyze your videos to identify the most engaging moments and key content.',
      icon: <Search className="h-6 w-6 text-ai-blue" />,
      details: [
        'Speech recognition and text analysis',
        'Visual scene detection and classification',
        'Engagement prediction algorithms',
        'Automatic content summarization'
      ]
    },
    {
      title: 'Automatic Short Generation',
      description: 'Transform your long-form videos into attention-grabbing shorts optimized for social media.',
      icon: <Video className="h-6 w-6 text-ai-blue" />,
      details: [
        'YouTube Shorts optimization',
        'TikTok-ready aspect ratios',
        'Auto-caption generation',
        'Engagement-focused edits'
      ]
    },
    {
      title: 'Ad Creative Generator',
      description: 'Create compelling ad creatives that drive conversions and maximize your marketing ROI.',
      icon: <PenTool className="h-6 w-6 text-ai-blue" />,
      details: [
        'Google Ads optimized creatives',
        'A/B testing variations',
        'Call-to-action optimization',
        'Custom branding options'
      ]
    },
    {
      title: 'Performance Prediction',
      description: 'Leverage AI to predict how your content will perform before you publish it.',
      icon: <BarChart3 className="h-6 w-6 text-ai-blue" />,
      details: [
        'Engagement rate prediction',
        'Audience retention analytics',
        'CTR and conversion forecasting',
        'Performance benchmarking'
      ]
    },
    {
      title: 'Time-Saving Automation',
      description: 'Cut your content creation time by up to 90% with our automated workflows.',
      icon: <Clock className="h-6 w-6 text-ai-blue" />,
      details: [
        'Batch processing capabilities',
        'Scheduled content generation',
        'Template-based workflows',
        'One-click publishing integrations'
      ]
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

    const element = document.getElementById('features');
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
      setActiveFeature((prev) => (prev + 1) % features.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [features.length]);

  return (
    <section id="features" className="py-20 relative">
      <div className="absolute top-1/2 left-1/2 w-96 h-96 -translate-x-1/2 -translate-y-1/2 bg-ai-accent/5 rounded-full blur-3xl"></div>
      
      <div className="section-container">
        <div className="mb-12 text-center">
          <div className="inline-flex items-center bg-ai-lighter/70 rounded-full pl-2 pr-4 py-1 mb-6 border border-ai-blue/20">
            <span className="bg-ai-blue/20 rounded-full p-1 mr-2">
              <Zap size={16} className="text-ai-blue" />
            </span>
            <span className="text-sm font-medium">Powerful Features</span>
          </div>
          <h2 className="section-title">
            <span className="gradient-heading">Smart Features</span> for Modern Content Creators
          </h2>
          <p className="section-subtitle">
            Our AI-powered platform streamlines your workflow with cutting-edge features that transform how you create content.
          </p>
        </div>

        <div 
          id="features"
          className={`grid grid-cols-1 lg:grid-cols-12 gap-8 transition-all duration-1000 transform ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="lg:col-span-5 space-y-4">
            {features.map((feature, index) => (
              <div 
                key={index}
                className={`ai-card cursor-pointer transition-all duration-300 ${
                  activeFeature === index 
                    ? 'border-ai-blue/50 bg-gradient-to-r from-ai-light to-ai-blue/5 shadow-lg shadow-ai-blue/10' 
                    : ''
                }`}
                onClick={() => setActiveFeature(index)}
              >
                <div className="flex items-start">
                  <div className="ai-icon-container">
                    {feature.icon}
                  </div>
                  <div className="ml-4 flex-1">
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-ai-muted text-sm">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="lg:col-span-7">
            <div className="glass-card p-8 h-full border border-ai-blue/20 shadow-lg shadow-ai-blue/5">
              <div className="flex flex-col h-full">
                <div className="mb-6">
                  <h3 className="text-2xl font-bold mb-3 gradient-heading">
                    {features[activeFeature].title}
                  </h3>
                  <p className="text-ai-muted">
                    {features[activeFeature].description}
                  </p>
                </div>
                
                <div className="flex-1 bg-ai-darker rounded-xl p-6 border border-ai-lighter/20">
                  <h4 className="text-lg font-medium mb-4 text-ai-text">Key Capabilities</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {features[activeFeature].details.map((detail, idx) => (
                      <div 
                        key={idx} 
                        className="flex items-center p-3 bg-ai-light/70 rounded-lg border border-ai-blue/10"
                      >
                        <div className="mr-3 bg-ai-blue/10 p-1.5 rounded-full">
                          <Zap size={14} className="text-ai-blue" />
                        </div>
                        <span className="text-sm">{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <button className="ai-btn-primary">
                    Try {features[activeFeature].title}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
