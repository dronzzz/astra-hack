import { ArrowRight } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-ai-darker relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-ai-purple via-ai-blue to-ai-accent"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <div>
            <div className="flex items-center mb-6">
              <span className="text-ai-blue font-bold text-2xl">AI</span>
              <span className="text-white font-bold text-2xl">Creator</span>
            </div>
            <p className="text-ai-muted text-sm mb-6">
              Transform your long-form videos into engaging shorts and
              high-converting ads with our AI-powered platform.
            </p>
            <div className="flex items-center space-x-4">
              <a
                href="#"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-ai-lighter hover:bg-ai-light transition-colors"
              >
                <svg
                  className="h-4 w-4 text-ai-text"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M22.675 0h-21.35c-.732 0-1.325.593-1.325 1.325v21.351c0 .731.593 1.324 1.325 1.324h11.495v-9.294h-3.128v-3.622h3.128v-2.671c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12v9.293h6.116c.73 0 1.323-.593 1.323-1.325v-21.35c0-.732-.593-1.325-1.325-1.325z" />
                </svg>
              </a>
              <a
                href="#"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-ai-lighter hover:bg-ai-light transition-colors"
              >
                <svg
                  className="h-4 w-4 text-ai-text"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M23.954 4.569c-.885.389-1.83.654-2.825.775 1.014-.611 1.794-1.574 2.163-2.723-.951.555-2.005.959-3.127 1.184-.896-.959-2.173-1.559-3.591-1.559-2.717 0-4.92 2.203-4.92 4.917 0 .39.045.765.127 1.124-4.09-.193-7.715-2.157-10.141-5.126-.427.722-.666 1.561-.666 2.475 0 1.71.87 3.213 2.188 4.096-.807-.026-1.566-.248-2.228-.616v.061c0 2.385 1.693 4.374 3.946 4.827-.413.111-.849.171-1.296.171-.314 0-.615-.03-.916-.086.631 1.953 2.445 3.377 4.604 3.417-1.68 1.319-3.809 2.105-6.102 2.105-.39 0-.779-.023-1.17-.067 2.189 1.394 4.768 2.209 7.557 2.209 9.054 0 14-7.503 14-14 0-.21-.007-.429-.018-.639.961-.689 1.8-1.56 2.46-2.548l-.047-.02z" />
                </svg>
              </a>
              <a
                href="#"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-ai-lighter hover:bg-ai-light transition-colors"
              >
                <svg
                  className="h-4 w-4 text-ai-text"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
              </a>
              <a
                href="#"
                className="w-8 h-8 flex items-center justify-center rounded-full bg-ai-lighter hover:bg-ai-light transition-colors"
              >
                <svg
                  className="h-4 w-4 text-ai-text"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z" />
                </svg>
              </a>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-6">Product</h3>
            <ul className="space-y-4">
              <li>
                <a
                  href="#features"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Features
                </a>
              </li>
              <li>
                <a
                  href="#how-it-works"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  How It Works
                </a>
              </li>
              <li>
                <a
                  href="#demo"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Demo
                </a>
              </li>
              <li>
                <a
                  href="#tech-stack"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Technology
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Pricing
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-6">Resources</h3>
            <ul className="space-y-4">
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Documentation
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  API Reference
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Blog
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Tutorials
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
                >
                  Support
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-6">Subscribe</h3>
            <p className="text-ai-muted text-sm mb-4">
              Stay updated with the latest features and releases.
            </p>
            <div className="relative">
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full bg-ai-light border border-ai-lighter/50 text-ai-text rounded-lg pl-4 pr-12 py-3 focus:outline-none focus:border-ai-blue/50 text-sm"
              />
              <button className="absolute right-2 top-1/2 transform -translate-y-1/2 text-ai-blue hover:text-ai-accent transition-colors">
                <ArrowRight size={18} />
              </button>
            </div>
            <p className="text-xs text-ai-muted mt-2">
              By subscribing, you agree to our Privacy Policy.
            </p>
          </div>
        </div>

        <div className="pt-8 border-t border-ai-lighter/20 flex flex-col md:flex-row justify-between items-center">
          <p className="text-ai-muted text-sm mb-4 md:mb-0">
            © 2023 AICreator. All rights reserved.
          </p>
          <div className="flex space-x-6">
            <a
              href="#"
              className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
            >
              Privacy Policy
            </a>
            <a
              href="#"
              className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
            >
              Terms of Service
            </a>
            <a
              href="#"
              className="text-ai-muted hover:text-ai-blue transition-colors text-sm"
            >
              Cookie Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
