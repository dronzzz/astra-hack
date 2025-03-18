
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Play, ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export interface Short {
  id: string;
  title: string;
  thumbnailUrl: string;
  videoUrl: string;
  duration: string;
}

interface VideoShortsProps {
  shorts: Short[];
}

const VideoShorts = ({ shorts }: VideoShortsProps) => {
  if (shorts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-xl font-semibold text-ai-blue">Generated Shorts</h2>
        <p className="text-ai-muted text-sm">
          We've created {shorts.length} optimized shorts from your video.
        </p>
      </div>

      <Tabs defaultValue="grid" className="w-full">
        <div className="flex justify-between items-center mb-4">
          <TabsList className="bg-ai-lighter/30">
            <TabsTrigger value="grid">Grid View</TabsTrigger>
            <TabsTrigger value="list">List View</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="grid" className="mt-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {shorts.map((short) => (
              <Card key={short.id} className="overflow-hidden border-ai-lighter bg-ai-dark/50">
                <CardContent className="p-3 space-y-3">
                  <div className="relative group">
                    <AspectRatio ratio={16 / 9}>
                      <img
                        src={short.thumbnailUrl}
                        alt={short.title}
                        className="rounded object-cover w-full h-full"
                      />
                    </AspectRatio>
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button size="icon" variant="outline" className="rounded-full bg-ai-blue/20 border-ai-blue/50">
                        <Play className="h-6 w-6 text-white" />
                      </Button>
                    </div>
                    <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                      {short.duration}
                    </span>
                  </div>
                  
                  <div className="flex items-start justify-between">
                    <h3 className="text-sm font-medium line-clamp-2">{short.title}</h3>
                    <Button size="icon" variant="ghost" className="h-8 w-8 text-ai-muted">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="list" className="mt-0">
          <div className="space-y-4">
            {shorts.map((short) => (
              <Card key={short.id} className="overflow-hidden border-ai-lighter bg-ai-dark/50">
                <CardContent className="p-3">
                  <div className="flex gap-4">
                    <div className="relative flex-shrink-0 w-40">
                      <AspectRatio ratio={16 / 9}>
                        <img
                          src={short.thumbnailUrl}
                          alt={short.title}
                          className="rounded object-cover w-full h-full"
                        />
                      </AspectRatio>
                      <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                        {short.duration}
                      </span>
                    </div>
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <h3 className="font-medium mb-2">{short.title}</h3>
                        <p className="text-sm text-ai-muted">Ready to download and share</p>
                      </div>
                      <div className="flex justify-end">
                        <Button size="sm" variant="ghost" className="text-ai-muted">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          Open
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default VideoShorts;
