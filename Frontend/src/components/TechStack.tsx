
import { useState, useEffect } from 'react';
import { Code, Terminal, Zap } from 'lucide-react';

const TechStack = () => {
  const [isVisible, setIsVisible] = useState(false);

  const techStack = [
    {
      name: 'OpenAI',
      description: 'Leveraging GPT-4 for intelligent content analysis and summarization',
      category: 'AI Core'
    },
    {
      name: 'LangChain',
      description: 'Framework for developing context-aware applications powered by language models',
      category: 'Framework'
    },
    {
      name: 'MoviePy',
      description: 'Python library for video editing and composition',
      category: 'Video Processing'
    },
    {
      name: 'TensorFlow',
      description: 'Open-source machine learning framework for training neural networks',
      category: 'Machine Learning'
    },
    {
      name: 'PyTorch',
      description: 'Deep learning framework for computer vision and natural language processing',
      category: 'Machine Learning'
    },
    {
      name: 'ffmpeg',
      description: 'Complete solution to record, convert and stream audio and video',
      category: 'Video Processing'
    },
    {
      name: 'Google Cloud',
      description: 'Cloud computing services for scalable and reliable infrastructure',
      category: 'Infrastructure'
    },
    {
      name: 'AWS',
      description: 'Cloud platform offering computing power, storage, and content delivery',
      category: 'Infrastructure'
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

    const element = document.getElementById('tech-stack');
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
    <section id="tech-stack" className="py-20 bg-ai-darker relative">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
        <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-ai-blue/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/3 left-1/4 w-64 h-64 bg-ai-purple/5 rounded-full blur-3xl"></div>
      </div>

      <div className="section-container">
        <div className="mb-12 text-center relative z-10">
          <div className="inline-flex items-center bg-ai-lighter/70 rounded-full pl-2 pr-4 py-1 mb-6 border border-ai-blue/20">
            <span className="bg-ai-blue/20 rounded-full p-1 mr-2">
              <Terminal size={16} className="text-ai-blue" />
            </span>
            <span className="text-sm font-medium">Powered By</span>
          </div>
          <h2 className="section-title">
            Our <span className="gradient-heading">Tech Stack</span>
          </h2>
          <p className="section-subtitle">
            We leverage cutting-edge technologies to deliver a powerful and efficient content creation platform.
          </p>
        </div>

        <div 
          id="tech-stack"
          className={`relative z-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 transition-all duration-1000 transform ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          {techStack.map((tech, index) => (
            <div 
              key={index} 
              className="ai-card flex flex-col justify-between h-full"
              style={{ 
                transitionDelay: `${index * 100}ms` 
              }}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="ai-icon-container">
                    <Code className="h-5 w-5 text-ai-blue" />
                  </div>
                  <span className="text-xs px-2 py-1 bg-ai-blue/10 text-ai-blue rounded-full">
                    {tech.category}
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-2">{tech.name}</h3>
                <p className="text-sm text-ai-muted">{tech.description}</p>
              </div>
              
              <div className="mt-6 pt-4 border-t border-ai-lighter/30">
                <div className="flex items-center text-xs text-ai-muted">
                  <Zap size={12} className="text-ai-blue mr-1" />
                  <span>Powers {tech.category === 'AI Core' ? 'core intelligence' : tech.category === 'Video Processing' ? 'video processing' : tech.category === 'Machine Learning' ? 'ML models' : 'infrastructure'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center relative z-10">
          <div className="glass-card max-w-3xl mx-auto p-8 border border-ai-blue/20">
            <h3 className="text-2xl font-bold mb-4">
              <span className="gradient-heading">Ready to Experience the Power?</span>
            </h3>
            <p className="text-ai-muted mb-8">
              Start transforming your long-form videos into engaging shorts and high-converting ads with our AI-powered platform.
            </p>
            <button className="ai-btn-primary">
              Get Started Now
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TechStack;
