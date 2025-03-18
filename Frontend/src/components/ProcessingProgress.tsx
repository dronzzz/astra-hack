interface ProcessingProgressProps {
  progress: number;
  currentStage: string;
  jobId: string | null;
}

export const ProcessingProgress = ({
  progress,
  currentStage,
  jobId,
}: ProcessingProgressProps) => {
  return (
    <div className="mt-8 p-6 bg-ai-light rounded-lg border border-ai-lighter">
      <h3 className="text-lg font-medium text-white mb-2">
        Processing Your Video
      </h3>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-ai-muted mb-1">Current Status:</p>
          <p className="text-white font-medium">
            {currentStage || "Initializing..."}
          </p>
        </div>

        <div>
          <div className="flex justify-between text-xs text-ai-muted mb-1">
            <span>Overall Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-ai-darker rounded-full h-3">
            <div
              className="bg-gradient-to-r from-ai-accent to-ai-accent2 h-3 rounded-full transition-all duration-300 ease-in-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        <div className="text-xs text-ai-muted">
          <p>Job ID: {jobId}</p>
          <p className="mt-1">
            This process can take several minutes depending on the video length.
          </p>
          <p className="mt-3 flex items-center">
            <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Live status updates will appear here
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingProgress;
