<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Existing cards */}

  {/* Trend Analyzer Card */}
  <div className="bg-white dark:bg-ai-dark rounded-lg shadow p-6">
    <div className="flex items-center mb-4">
      <TrendingUpIcon className="h-6 w-6 text-ai-accent mr-2" />
      <h3 className="text-lg font-medium">Trend Analyzer</h3>
    </div>
    <p className="text-ai-muted mb-4">
      Analyze YouTube videos to determine their trend potential and virality.
    </p>
    <Link
      to="/analyze-trend"
      className="inline-block px-4 py-2 bg-ai-accent text-white rounded hover:bg-ai-accent-dark transition"
    >
      Analyze Trends
    </Link>
  </div>
</div>;
