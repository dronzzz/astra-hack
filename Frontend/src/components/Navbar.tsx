
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, Upload } from 'lucide-react';
import { Button } from './ui/button';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle scroll event
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled || mobileMenuOpen ? 'bg-ai-darker/95 backdrop-blur-md' : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-gradient-to-br from-ai-accent to-ai-accent2 flex items-center justify-center text-ai-darker font-bold text-xl">
              A
            </div>
            <span className="text-white font-semibold text-xl">AI Creator</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/" className="text-ai-text hover:text-white transition-colors">
              Home
            </Link>
            <Link to="/upload" className="text-ai-text hover:text-white transition-colors flex items-center gap-1">
              <Upload size={18} />
              <span>Upload</span>
            </Link>
            <a href="#features" className="text-ai-text hover:text-white transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-ai-text hover:text-white transition-colors">
              How It Works
            </a>
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Link to="/upload">
              <Button className="ai-btn-primary">
                Get Started
              </Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-ai-text hover:text-white transition-colors"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden pt-4 pb-6 space-y-4 flex flex-col">
            <Link
              to="/"
              className="text-ai-text hover:text-white transition-colors py-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/upload"
              className="text-ai-text hover:text-white transition-colors py-2 flex items-center gap-1"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Upload size={18} />
              <span>Upload</span>
            </Link>
            <a
              href="#features"
              className="text-ai-text hover:text-white transition-colors py-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-ai-text hover:text-white transition-colors py-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              How It Works
            </a>
            <Link to="/upload" onClick={() => setMobileMenuOpen(false)}>
              <Button className="ai-btn-primary w-full mt-2">
                Get Started
              </Button>
            </Link>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;
