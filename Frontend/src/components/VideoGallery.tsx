const VideoGallery = ({ videos }) => {
  if (!videos || videos.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-8">
      {videos.map((video) => (
        <div
          key={video.id}
          className="border rounded-lg overflow-hidden shadow-md"
        >
          <div className="relative pt-[56.25%]">
            <video
              className="absolute top-0 left-0 w-full h-full object-cover"
              controls
              poster={video.thumbnailUrl}
              src={video.url}
            />
          </div>
          <div className="p-4">
            <h3 className="font-semibold text-lg">{video.title}</h3>
            <p className="text-sm text-gray-600">Duration: {video.duration}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
