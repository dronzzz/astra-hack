const ProgressBar = ({ progress, message }) => {
  return (
    <div className="mt-6 mb-8">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium">{message}</span>
        <span className="text-sm font-medium">{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-in-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {/* Show "live" indicator when videos are being processed */}
      {progress > 0 && progress < 100 && (
        <div className="flex items-center mt-2">
          <span className="animate-pulse h-2 w-2 bg-red-500 rounded-full mr-2"></span>
          <span className="text-xs text-gray-500">
            Videos will appear here as they are processed
          </span>
        </div>
      )}
    </div>
  );
};
