import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Menu, X, Upload, TrendingUpIcon, User } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "@/contexts/AuthContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, signOut } = useAuth();

  // Handle scroll event
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled || mobileMenuOpen
          ? "bg-ai-darker/95 backdrop-blur-md"
          : "bg-transparent"
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
            <Link
              to="/"
              className="text-ai-text hover:text-white transition-colors"
            >
              Home
            </Link>
            <Link
              to="/upload"
              className="text-ai-text hover:text-white transition-colors flex items-center gap-1"
            >
              <Upload size={18} />
              <span>Upload</span>
            </Link>
            <Link
              to="/analyze-trend"
              className="text-ai-text hover:text-white transition-colors flex items-center gap-2"
            >
              <TrendingUpIcon className="h-5 w-5" />
              <span>Trend Analyzer</span>
            </Link>
            <a
              href="#features"
              className="text-ai-text hover:text-white transition-colors"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="text-ai-text hover:text-white transition-colors"
            >
              How It Works
            </a>
          </div>

          {/* CTA Button or User Menu */}
          <div className="hidden md:block">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative rounded-full h-10 w-10 p-0"
                  >
                    {user.user_metadata?.avatar_url ? (
                      <img
                        src={user.user_metadata.avatar_url}
                        alt="User avatar"
                        className="h-full w-full rounded-full object-cover"
                      />
                    ) : (
                      <User className="h-5 w-5 text-ai-accent" />
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="w-56 bg-ai-light border-ai-lighter"
                >
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium text-white">
                        {user.user_metadata?.full_name || user.email}
                      </p>
                      {user.email && (
                        <p className="w-[200px] truncate text-sm text-ai-muted">
                          {user.email}
                        </p>
                      )}
                    </div>
                  </div>
                  <DropdownMenuSeparator className="bg-ai-lighter" />
                  <DropdownMenuItem asChild>
                    <Link
                      to="/dashboard"
                      className="cursor-pointer text-white hover:bg-ai-darker focus:bg-ai-darker"
                    >
                      Dashboard
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="cursor-pointer text-white hover:bg-ai-darker focus:bg-ai-darker"
                    onClick={handleSignOut}
                  >
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link to="/login">
                <Button className="ai-btn-primary">Sign In</Button>
              </Link>
            )}
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
            <Link
              to="/analyze-trend"
              className="text-ai-text hover:text-white transition-colors py-2 flex items-center gap-2"
              onClick={() => setMobileMenuOpen(false)}
            >
              <TrendingUpIcon className="h-5 w-5" />
              <span>Trend Analyzer</span>
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

            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="text-ai-text hover:text-white transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Button
                  className="ai-btn-outline w-full mt-2"
                  onClick={() => {
                    handleSignOut();
                    setMobileMenuOpen(false);
                  }}
                >
                  Sign Out
                </Button>
              </>
            ) : (
              <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                <Button className="ai-btn-primary w-full mt-2">Sign In</Button>
              </Link>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;
