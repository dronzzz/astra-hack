import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { saveYouTubeCredentials, getYouTubeCredentials } from "@/lib/supabase";

const Dashboard = () => {
  const { user, loading, signOut } = useAuth();
  const [credentials, setCredentials] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Redirect if not logged in
  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  // Fetch existing credentials
  useEffect(() => {
    const fetchCredentials = async () => {
      if (user?.id) {
        try {
          const existingCredentials = await getYouTubeCredentials(user.id);
          if (existingCredentials) {
            setCredentials(JSON.stringify(existingCredentials, null, 2));
          }
        } catch (error) {
          console.error("Error fetching credentials:", error);
        }
      }
    };

    fetchCredentials();
  }, [user]);

  const handleSaveCredentials = async () => {
    if (!user?.id) return;

    try {
      setIsSaving(true);

      // Try to parse the JSON to validate
      let parsedCredentials;
      try {
        parsedCredentials = JSON.parse(credentials);
      } catch (e) {
        toast({
          title: "Invalid JSON",
          description: "Please enter valid JSON for the credentials",
          variant: "destructive",
        });
        setIsSaving(false);
        return;
      }

      // Save to Supabase
      const { error } = await saveYouTubeCredentials(
        user.id,
        parsedCredentials
      );

      if (error) {
        throw error;
      }

      toast({
        title: "Credentials saved",
        description:
          "Your YouTube API credentials have been saved successfully",
      });
    } catch (error) {
      console.error("Error saving credentials:", error);
      toast({
        title: "Error saving credentials",
        description: "There was a problem saving your credentials",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate("/login");
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ai-dark">
        <div className="text-ai-accent-light animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ai-dark">
      <Navbar />

      <main className="section-container py-12 mt-12">
        <div className="max-w-6xl mx-auto">
          <h1 className="section-title mb-6">
            <span className="gradient-heading">Your Dashboard</span>
          </h1>
          <p className="section-subtitle mb-10">
            Manage your account and YouTube API credentials
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* User Profile Card */}
            <Card className="bg-ai-light border-ai-lighter md:col-span-1">
              <CardHeader>
                <CardTitle className="text-white">Profile</CardTitle>
                <CardDescription className="text-ai-muted">
                  Your account information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  {user?.user_metadata?.avatar_url && (
                    <img
                      src={user.user_metadata.avatar_url}
                      alt="Profile"
                      className="h-16 w-16 rounded-full border-2 border-ai-accent"
                    />
                  )}
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {user?.user_metadata?.full_name || user?.email || "User"}
                    </h3>
                    <p className="text-ai-muted text-sm">{user?.email}</p>
                  </div>
                </div>

                <div className="pt-4">
                  <Button
                    onClick={handleSignOut}
                    variant="outline"
                    className="ai-btn-secondary w-full"
                  >
                    Sign Out
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* YouTube Credentials Card */}
            <Card className="bg-ai-light border-ai-lighter md:col-span-2">
              <CardHeader>
                <CardTitle className="text-white">
                  YouTube API Credentials
                </CardTitle>
                <CardDescription className="text-ai-muted">
                  Add your YouTube API credentials to enable video uploads
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="credentials" className="text-ai-muted">
                    Client Credentials JSON
                  </Label>
                  <Textarea
                    id="credentials"
                    className="h-60 bg-ai-dark border-ai-lighter font-mono text-sm"
                    placeholder='{ "installed": { "client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET", ... } }'
                    value={credentials}
                    onChange={(e) => setCredentials(e.target.value)}
                  />
                  <p className="text-xs text-ai-muted">
                    Paste your client_secrets.json content from the Google Cloud
                    Console
                  </p>
                </div>

                <Button
                  onClick={handleSaveCredentials}
                  disabled={isSaving || !credentials}
                  className="ai-btn-primary"
                >
                  {isSaving ? "Saving..." : "Save Credentials"}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Usage Statistics Card */}
          <Card className="bg-ai-light border-ai-lighter mt-6">
            <CardHeader>
              <CardTitle className="text-white">Recent Activity</CardTitle>
              <CardDescription className="text-ai-muted">
                Your recent video processing activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-ai-muted">
                <p>No recent activity to display</p>
                <Button
                  onClick={() => navigate("/upload")}
                  className="ai-btn-primary mt-4"
                >
                  Process a New Video
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Dashboard;
