const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-12">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-center md:text-left">
            <p className="text-sm text-gray-600">
              <span className="font-semibold">Privacy First:</span> Your files are processed in memory and immediately deleted after analysis.
            </p>
            <p className="text-xs text-gray-500 mt-1">
              No data is stored or logged. 100% secure and private.
            </p>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-900 transition-colors"
            >
              GitHub
            </a>
            <span className="text-gray-400">|</span>
            <a
              href="#"
              className="hover:text-gray-900 transition-colors"
            >
              About
            </a>
            <span className="text-gray-400">|</span>
            <a
              href="#"
              className="hover:text-gray-900 transition-colors"
            >
              API Docs
            </a>
          </div>
        </div>
        <div className="mt-4 text-center text-xs text-gray-400">
          Made with Claude Code
        </div>
      </div>
    </footer>
  );
};

export default Footer;
