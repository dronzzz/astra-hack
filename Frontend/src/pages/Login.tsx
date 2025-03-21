import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FaGoogle, FaGithub } from "react-icons/fa";

const Login = () => {
  const { user, signInWithGoogle, signInWithGitHub, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }
  }, [user, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-ai-dark p-4">
      <Card className="w-full max-w-md border-ai-accent/20 bg-ai-light/5 text-white">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center text-ai-accent">
            Welcome Back
          </CardTitle>
          <CardDescription className="text-center text-gray-400">
            Sign in to your account to create and manage your video shorts
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <Button
            variant="outline"
            className="flex items-center gap-2 bg-transparent border-ai-accent-light/50 hover:bg-ai-accent/10 hover:text-ai-accent-light transition-all"
            onClick={() => signInWithGoogle()}
            disabled={loading}
          >
            <FaGoogle className="h-4 w-4" />
            <span>Sign in with Google</span>
          </Button>
          <Button
            variant="outline"
            className="flex items-center gap-2 bg-transparent border-ai-accent-light/50 hover:bg-ai-accent/10 hover:text-ai-accent-light transition-all"
            onClick={() => signInWithGitHub()}
            disabled={loading}
          >
            <FaGithub className="h-4 w-4" />
            <span>Sign in with GitHub</span>
          </Button>
        </CardContent>
        <CardFooter className="flex flex-col items-center justify-center text-center text-xs text-gray-500">
          <p>
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Login;
