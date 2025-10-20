const Results = ({ results }) => {
  if (!results) return null;

  const { file_info, acx_compliance, additional_metrics, elevenlabs } = results;

  const CheckIcon = () => (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  );

  const XIcon = () => (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  );

  const ResultRow = ({ label, value, pass, requirement }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-200">
      <div className="flex items-center space-x-3">
        <div className={`${pass ? 'text-green-500' : 'text-red-500'}`}>
          {pass ? <CheckIcon /> : <XIcon />}
        </div>
        <div>
          <p className="font-medium text-gray-900">{label}</p>
          {requirement && (
            <p className="text-xs text-gray-500">{requirement}</p>
          )}
        </div>
      </div>
      <div className="text-right">
        <p className={`font-mono text-sm ${pass ? 'text-green-600' : 'text-red-600'}`}>
          {value}
        </p>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* File Info */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">File Information</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Filename</p>
            <p className="font-medium text-gray-900">{file_info.filename}</p>
          </div>
          <div>
            <p className="text-gray-500">Duration</p>
            <p className="font-medium text-gray-900">{file_info.duration}</p>
          </div>
          <div>
            <p className="text-gray-500">Format</p>
            <p className="font-medium text-gray-900">{file_info.format}</p>
          </div>
          <div>
            <p className="text-gray-500">Sample Rate</p>
            <p className="font-medium text-gray-900">{file_info.sample_rate} Hz</p>
          </div>
          <div>
            <p className="text-gray-500">Channels</p>
            <p className="font-medium text-gray-900">{file_info.channels}</p>
          </div>
          <div>
            <p className="text-gray-500">Bitrate</p>
            <p className="font-medium text-gray-900">{file_info.bitrate}</p>
          </div>
        </div>
      </div>

      {/* ACX Compliance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">ACX Compliance</h2>
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
            acx_compliance.overall_pass
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {acx_compliance.overall_pass ? 'PASS' : 'FAIL'}
          </span>
        </div>

        <div className="space-y-1">
          <ResultRow
            label="RMS Level"
            value={`${acx_compliance.rms.value.toFixed(1)} dB`}
            pass={acx_compliance.rms.pass}
            requirement={acx_compliance.rms.range}
          />
          <ResultRow
            label="Peak Level"
            value={`${acx_compliance.peak.value.toFixed(1)} dB`}
            pass={acx_compliance.peak.pass}
            requirement={acx_compliance.peak.threshold}
          />
          <ResultRow
            label="Noise Floor"
            value={`${acx_compliance.noise_floor.value.toFixed(1)} dB`}
            pass={acx_compliance.noise_floor.pass}
            requirement={acx_compliance.noise_floor.threshold}
          />
          <ResultRow
            label="Format"
            value={acx_compliance.format.value}
            pass={acx_compliance.format.pass}
            requirement={acx_compliance.format.required}
          />
          <ResultRow
            label="Duration"
            value={`${(acx_compliance.duration.value / 60).toFixed(1)} min`}
            pass={acx_compliance.duration.pass}
            requirement={`< ${acx_compliance.duration.max / 60} minutes`}
          />
          <ResultRow
            label="Room Tone"
            value={acx_compliance.room_tone.detected ? 'Detected' : 'Not Detected'}
            pass={acx_compliance.room_tone.pass}
            requirement={acx_compliance.room_tone.required}
          />
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Additional Metrics</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">LUFS</p>
            <p className="text-2xl font-bold text-gray-900">{additional_metrics.lufs.toFixed(1)}</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">True Peak</p>
            <p className="text-2xl font-bold text-gray-900">{additional_metrics.true_peak.toFixed(1)} dB</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">Reverb</p>
            <p className="text-2xl font-bold text-gray-900 capitalize">{additional_metrics.reverb_level}</p>
          </div>
        </div>
      </div>

      {/* ElevenLabs Compliance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">ElevenLabs Compliance</h2>
        <div className="space-y-1">
          <ResultRow
            label="Length"
            value={`${elevenlabs.length_minutes.toFixed(1)} min`}
            pass={elevenlabs.length_ok}
            requirement={elevenlabs.length_requirement}
          />
          <ResultRow
            label="Quality"
            value={elevenlabs.quality_ok ? 'Good' : 'Poor'}
            pass={elevenlabs.quality_ok}
            requirement={elevenlabs.quality_requirement}
          />
        </div>
      </div>
    </div>
  );
};

export default Results;
