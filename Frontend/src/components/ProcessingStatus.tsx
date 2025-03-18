import { ProcessingJob } from "@/lib/videoService";
import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

interface ProcessingStatusProps {
  status: ProcessingJob;
}

export function ProcessingStatus({ status }: ProcessingStatusProps) {
  return (
    <div className="p-6 rounded-lg bg-ai-light/20 border border-ai-border">
      <h3 className="text-xl font-medium mb-4 text-white flex items-center">
        <Loader2 className="h-5 w-5 mr-2 animate-spin text-ai-blue" />
        Processing Your Video
      </h3>

      <div className="space-y-4">
        <div className="flex justify-between text-sm">
          <span className="text-ai-muted">{status.message}</span>
          <span className="text-ai-blue">{status.progress}%</span>
        </div>

        <Progress value={status.progress} className="h-2 bg-ai-lighter">
          <div className="h-full bg-gradient-to-r from-ai-accent to-ai-accent2 rounded-full" />
        </Progress>

        {status.segments && status.segments.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-ai-muted mb-2">
              Segments detected:
            </h4>
            <ul className="space-y-2">
              {status.segments.map((segment, i) => (
                <li
                  key={i}
                  className="text-sm text-white bg-ai-light/30 rounded p-2"
                >
                  <div className="flex justify-between mb-1">
                    <span className="text-ai-accent">Segment {i + 1}</span>
                    <span className="text-ai-muted">
                      {Math.round(segment.start_time)}s -{" "}
                      {Math.round(segment.end_time)}s
                    </span>
                  </div>
                  <p className="text-ai-muted">{segment.reason}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
