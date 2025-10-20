import { useState, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUpload from './components/FileUpload';
import Results from './components/Results';
import PaymentModal from './components/PaymentModal';
import { analyzeAudio } from './services/api';

// localStorage helper functions
const getUsageData = () => {
  try {
    const data = localStorage.getItem('audioAnalyzerUsage');
    if (!data) {
      return { analysisCount: 0, skipCount: 0, hasPaid: false };
    }
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading localStorage:', error);
    return { analysisCount: 0, skipCount: 0, hasPaid: false };
  }
};

const saveUsageData = (data) => {
  try {
    localStorage.setItem('audioAnalyzerUsage', JSON.stringify(data));
  } catch (error) {
    console.error('Error saving to localStorage:', error);
  }
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [pendingResults, setPendingResults] = useState(null);
  const [usageData, setUsageData] = useState(getUsageData());

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setError(null);
    setResults(null);
    setIsAnalyzing(true);

    try {
      const data = await analyzeAudio(file);

      // Check if we should show payment modal
      if (usageData.analysisCount === 0 || usageData.hasPaid) {
        // First time or user has paid - show results immediately
        setResults(data);

        // Increment usage count if first time
        if (usageData.analysisCount === 0) {
          const newUsageData = { ...usageData, analysisCount: 1 };
          setUsageData(newUsageData);
          saveUsageData(newUsageData);
        }
      } else {
        // Second+ time and hasn't paid - show payment modal
        setPendingResults(data);
        setShowPaymentModal(true);
      }
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.message ||
        'An error occurred while analyzing the audio file'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResults(null);
    setError(null);
  };

  const handlePaid = () => {
    // User claims they've paid - mark as paid and show results
    const newUsageData = { ...usageData, hasPaid: true };
    setUsageData(newUsageData);
    saveUsageData(newUsageData);
    setResults(pendingResults);
    setPendingResults(null);
    setShowPaymentModal(false);
  };

  const handleSkip = () => {
    // User skipped - increment skip count and show results
    const newUsageData = {
      ...usageData,
      skipCount: usageData.skipCount + 1,
      analysisCount: usageData.analysisCount + 1,
    };
    setUsageData(newUsageData);
    saveUsageData(newUsageData);
    setResults(pendingResults);
    setPendingResults(null);
    setShowPaymentModal(false);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Upload Audio File
            </h2>
            <FileUpload onFileSelect={handleFileSelect} isAnalyzing={isAnalyzing} />

            {selectedFile && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-900">
                      Selected: {selectedFile.name}
                    </p>
                    <p className="text-xs text-blue-700">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  {!isAnalyzing && (
                    <button
                      onClick={handleReset}
                      className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Upload Another
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Loading State */}
          {isAnalyzing && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
                <p className="text-lg font-medium text-gray-900">
                  Analyzing audio...
                </p>
                <p className="text-sm text-gray-600">
                  This may take 30-60 seconds depending on file size
                </p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start space-x-3">
                <svg
                  className="w-6 h-6 text-red-600 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <div>
                  <h3 className="text-sm font-medium text-red-800">
                    Error analyzing audio
                  </h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {results && <Results results={results} />}
        </div>
      </main>

      <Footer />

      {/* Payment Modal */}
      {showPaymentModal && (
        <PaymentModal
          onClose={() => setShowPaymentModal(false)}
          onPaid={handlePaid}
          onSkip={handleSkip}
          skipCount={usageData.skipCount}
          maxSkips={3}
        />
      )}
    </div>
  );
}

export default App;
