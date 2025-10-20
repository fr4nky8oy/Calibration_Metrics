const Results = ({ results }) => {
  if (!results) return null;

  const { file_info, acx_compliance, additional_metrics, elevenlabs } = results;

  // Check if we have the new ElevenLabs structure (with 'overall' property)
  const hasNewElevenLabsFormat = elevenlabs && elevenlabs.overall;

  // Check if we have dynamic_range in additional_metrics
  const hasDynamicRange = additional_metrics && additional_metrics.dynamic_range !== undefined;

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
        <div className={`grid ${hasDynamicRange ? 'grid-cols-2 md:grid-cols-4' : 'grid-cols-3'} gap-4`}>
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
          {hasDynamicRange && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-500 text-sm mb-1">Dynamic Range</p>
              <p className="text-2xl font-bold text-gray-900">{additional_metrics.dynamic_range.toFixed(1)} dB</p>
            </div>
          )}
        </div>
      </div>

      {/* ElevenLabs Voice Cloning Suitability */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {hasNewElevenLabsFormat ? 'ElevenLabs Voice Cloning Suitability' : 'ElevenLabs Compliance'}
        </h2>

        {hasNewElevenLabsFormat ? (
          <>
        {/* Overall Suitability Badge */}
        <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Overall Suitability</p>
              <p className={`text-xl font-bold ${
                elevenlabs.overall.suitability === 'excellent' ? 'text-green-600' :
                elevenlabs.overall.suitability === 'good' ? 'text-blue-600' :
                elevenlabs.overall.suitability === 'acceptable' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {elevenlabs.overall.suitability.toUpperCase()}
              </p>
              <p className="text-sm text-gray-700 mt-1">{elevenlabs.overall.message}</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">{elevenlabs.overall.criteria_met}/{elevenlabs.overall.total_criteria}</p>
              <p className="text-xs text-gray-500">Criteria Met</p>
            </div>
          </div>
        </div>

        {/* Cloning Type Recommendation */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start">
            <svg className="w-6 h-6 text-blue-500 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-semibold text-blue-900 mb-1">Recommended Cloning Type</p>
              <p className="text-sm text-blue-800">
                <span className="font-bold capitalize">{elevenlabs.cloning_type.recommended}</span>
                {' '}- {elevenlabs.cloning_type.message}
              </p>
              <p className="text-xs text-blue-600 mt-1">Duration: {elevenlabs.cloning_type.duration_minutes.toFixed(1)} minutes</p>
            </div>
          </div>
        </div>

        {/* Volume Check */}
        <div className="mb-4">
          <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
            <span className={`mr-2 ${elevenlabs.volume.pass ? 'text-green-500' : 'text-yellow-500'}`}>
              {elevenlabs.volume.pass ? '✓' : '⚠'}
            </span>
            Volume & Loudness
          </h3>
          <div className="ml-7 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-700 mb-2">{elevenlabs.volume.message}</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">RMS:</span>
                <span className="ml-1 font-mono font-semibold">{elevenlabs.volume.rms.toFixed(1)} dB</span>
              </div>
              <div>
                <span className="text-gray-500">True Peak:</span>
                <span className="ml-1 font-mono font-semibold">{elevenlabs.volume.true_peak.toFixed(1)} dB</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Ideal: {elevenlabs.volume.ideal_range}</p>
          </div>
        </div>

        {/* Format Check */}
        <div className="mb-4">
          <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
            <span className={`mr-2 ${elevenlabs.format.pass ? 'text-green-500' : 'text-yellow-500'}`}>
              {elevenlabs.format.pass ? '✓' : '⚠'}
            </span>
            Audio Format
          </h3>
          <div className="ml-7 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-700 mb-1">{elevenlabs.format.message}</p>
            <div className="text-xs">
              <span className="text-gray-500">Current:</span>
              <span className="ml-1 font-mono font-semibold">{elevenlabs.format.current}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Recommended: {elevenlabs.format.recommended}</p>
          </div>
        </div>

        {/* Quality Checklist */}
        <div className="mb-4">
          <h3 className="font-semibold text-gray-800 mb-3">Audio Quality Checklist</h3>
          <div className="ml-7 space-y-2">
            {/* Clean Audio */}
            <div className="flex items-start p-2 bg-gray-50 rounded">
              <span className={`mr-2 mt-0.5 ${elevenlabs.quality_checklist.clean_audio.pass ? 'text-green-500' : 'text-red-500'}`}>
                {elevenlabs.quality_checklist.clean_audio.pass ? '✓' : '✗'}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">Clean Audio</p>
                <p className="text-xs text-gray-600">{elevenlabs.quality_checklist.clean_audio.message}</p>
                <p className="text-xs text-gray-500">Noise floor: {elevenlabs.quality_checklist.clean_audio.value}</p>
              </div>
            </div>

            {/* No Reverb */}
            <div className="flex items-start p-2 bg-gray-50 rounded">
              <span className={`mr-2 mt-0.5 ${elevenlabs.quality_checklist.no_reverb.pass ? 'text-green-500' : 'text-red-500'}`}>
                {elevenlabs.quality_checklist.no_reverb.pass ? '✓' : '✗'}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">No Reverb/Echo</p>
                <p className="text-xs text-gray-600">{elevenlabs.quality_checklist.no_reverb.message}</p>
                <p className="text-xs text-gray-500">Reverb level: {elevenlabs.quality_checklist.no_reverb.value}</p>
              </div>
            </div>

            {/* Consistent Volume */}
            <div className="flex items-start p-2 bg-gray-50 rounded">
              <span className={`mr-2 mt-0.5 ${elevenlabs.quality_checklist.consistent_volume.pass ? 'text-green-500' : 'text-red-500'}`}>
                {elevenlabs.quality_checklist.consistent_volume.pass ? '✓' : '✗'}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">Consistent Volume</p>
                <p className="text-xs text-gray-600">{elevenlabs.quality_checklist.consistent_volume.message}</p>
                <p className="text-xs text-gray-500">Dynamic range: {elevenlabs.quality_checklist.consistent_volume.value}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Documentation Links */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 mb-2">Learn more about voice cloning requirements:</p>
          <div className="flex flex-wrap gap-2">
            <a
              href={elevenlabs.documentation.instant_voice_cloning}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-3 py-1.5 bg-purple-100 text-purple-700 hover:bg-purple-200 rounded text-xs font-medium transition-colors"
            >
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Instant Voice Cloning Docs
            </a>
            <a
              href={elevenlabs.documentation.professional_voice_cloning}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded text-xs font-medium transition-colors"
            >
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Professional Voice Cloning Docs
            </a>
          </div>
        </div>
        </>
        ) : (
          /* Old Format - Fallback */
          <div className="space-y-1">
            <ResultRow
              label="Length"
              value={`${elevenlabs.length_minutes?.toFixed(1) || 'N/A'} min`}
              pass={elevenlabs.length_ok || false}
              requirement={elevenlabs.length_requirement || 'Minimum 1 minute'}
            />
            <ResultRow
              label="Quality"
              value={elevenlabs.quality_ok ? 'Good' : 'Poor'}
              pass={elevenlabs.quality_ok || false}
              requirement={elevenlabs.quality_requirement || 'Clean audio required'}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;
