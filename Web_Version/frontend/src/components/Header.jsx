const Header = ({ onSupportClick }) => {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-bold text-gray-900 flex items-center gap-3">
              <span className="text-4xl">🎤</span>
              Analise This
              <span className="text-4xl">📊</span>
            </h1>
            <p className="mt-2 text-base text-gray-600">
              Professional audio analysis for ACX audiobook standards & ElevenLabs voice cloning
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onSupportClick}
              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors cursor-pointer"
            >
              Support This Project
            </button>
          </div>
        </div>

        {/* What You'll Get Section */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">What You'll Get:</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* ACX Compliance */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
              <h3 className="font-semibold text-blue-900 text-sm mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                ACX Compliance Check
              </h3>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• RMS Level (-23 to -18 dB)</li>
                <li>• Peak Level (&lt; -3 dB)</li>
                <li>• Noise Floor (&lt; -60 dB)</li>
                <li>• Format Validation</li>
                <li>• Room Tone Detection</li>
                <li>• Duration Check</li>
              </ul>
            </div>

            {/* Additional Metrics */}
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
              <h3 className="font-semibold text-purple-900 text-sm mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
                Advanced Metrics
              </h3>
              <ul className="text-xs text-purple-800 space-y-1">
                <li>• LUFS Loudness</li>
                <li>• True Peak Levels</li>
                <li>• Dynamic Range</li>
                <li>• Reverb Detection</li>
                <li>• Sample Rate & Bitrate</li>
                <li>• Channel Analysis</li>
              </ul>
            </div>

            {/* ElevenLabs Voice Cloning */}
            <div className="bg-green-50 rounded-lg p-4 border border-green-100">
              <h3 className="font-semibold text-green-900 text-sm mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
                Voice Cloning Suitability
              </h3>
              <ul className="text-xs text-green-800 space-y-1">
                <li>• Cloning Type Recommendation</li>
                <li>• Volume & Loudness Check</li>
                <li>• Audio Quality Assessment</li>
                <li>• Clean Audio Verification</li>
                <li>• Reverb/Echo Detection</li>
                <li>• Duration Requirements</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
