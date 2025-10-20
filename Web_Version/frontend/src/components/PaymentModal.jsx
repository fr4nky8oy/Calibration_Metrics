import { useState } from 'react';

const PaymentModal = ({ onClose, onPaid, onSkip, skipCount = 0, maxSkips = 3 }) => {
  const [isClosing, setIsClosing] = useState(false);
  const canSkip = skipCount < maxSkips;
  const buyMeCoffeeUrl = 'https://buymeacoffee.com/frankyredente';

  const handleClose = (callback) => {
    setIsClosing(true);
    setTimeout(() => {
      callback();
    }, 200);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        className={`bg-white rounded-lg shadow-xl max-w-md w-full transform transition-all duration-200 ${
          isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'
        }`}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-lg">
          <h2 className="text-2xl font-bold mb-2">Support This Free Tool</h2>
          <p className="text-blue-50 text-sm">
            Thanks for using the ACX Audio Analyzer! This tool is free and open-source,
            but server costs add up. If you find it valuable, consider supporting development with a small tip.
          </p>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          {/* Payment Options */}
          <div className="space-y-3">
            <p className="text-sm font-semibold text-gray-700 mb-2">Choose your support level:</p>

            <a
              href={`${buyMeCoffeeUrl}?amount=1`}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-yellow-50 hover:bg-yellow-100 border-2 border-yellow-200 rounded-lg p-4 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">☕</span>
                  <div>
                    <p className="font-semibold text-gray-900">Buy me a coffee</p>
                    <p className="text-xs text-gray-600">Small but appreciated</p>
                  </div>
                </div>
                <span className="font-bold text-yellow-700">$1</span>
              </div>
            </a>

            <a
              href={`${buyMeCoffeeUrl}?amount=3`}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-orange-50 hover:bg-orange-100 border-2 border-orange-200 rounded-lg p-4 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🍕</span>
                  <div>
                    <p className="font-semibold text-gray-900">Buy me lunch</p>
                    <p className="text-xs text-gray-600">Really helps out</p>
                  </div>
                </div>
                <span className="font-bold text-orange-700">$3</span>
              </div>
            </a>

            <a
              href={`${buyMeCoffeeUrl}?amount=5`}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-green-50 hover:bg-green-100 border-2 border-green-200 rounded-lg p-4 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🎉</span>
                  <div>
                    <p className="font-semibold text-gray-900">Super supporter</p>
                    <p className="text-xs text-gray-600">You're amazing!</p>
                  </div>
                </div>
                <span className="font-bold text-green-700">$5</span>
              </div>
            </a>

            <a
              href={buyMeCoffeeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-purple-50 hover:bg-purple-100 border-2 border-purple-200 rounded-lg p-4 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">💝</span>
                  <div>
                    <p className="font-semibold text-gray-900">Custom amount</p>
                    <p className="text-xs text-gray-600">Choose your own amount</p>
                  </div>
                </div>
                <span className="font-bold text-purple-700">$$$</span>
              </div>
            </a>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 border-t border-gray-200 space-y-2">
            <button
              onClick={() => handleClose(onPaid)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              I've already paid - show results
            </button>

            {canSkip ? (
              <button
                onClick={() => handleClose(onSkip)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors text-sm"
              >
                Skip this time ({maxSkips - skipCount} skips remaining)
              </button>
            ) : (
              <div className="text-center py-2">
                <p className="text-sm text-red-600 font-medium">
                  You've used all your free skips
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Please support to continue using the tool
                </p>
              </div>
            )}
          </div>

          {/* Footer Message */}
          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Your contribution helps keep this tool free for everyone. Thank you!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentModal;
