const Header = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              ACX Audio Analyzer
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Professional audio analysis for ACX audiobook standards & ElevenLabs voice cloning
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Free & Open Source
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
