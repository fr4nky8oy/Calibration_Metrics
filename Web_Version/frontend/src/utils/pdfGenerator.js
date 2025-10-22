import { jsPDF } from 'jspdf';

/**
 * Generates a PDF report from audio analysis results
 * @param {Object} results - The analysis results object
 * @returns {void} - Triggers download of PDF file
 */
export const generatePDFReport = (results) => {
  const { file_info, acx_compliance, additional_metrics, elevenlabs } = results;

  // Create new PDF document (A4 size)
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  let yPosition = 20;

  // Helper function to add section header
  const addSectionHeader = (title, y) => {
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(31, 41, 55); // gray-800
    doc.text(title, margin, y);
    doc.setLineWidth(0.5);
    doc.line(margin, y + 2, pageWidth - margin, y + 2);
    return y + 10;
  };

  // Helper function to add key-value pair
  const addKeyValue = (key, value, y, pass = null) => {
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(75, 85, 99); // gray-600
    doc.text(key + ':', margin, y);

    doc.setFont('helvetica', 'normal');

    // Color code based on pass/fail if provided
    if (pass === true) {
      doc.setTextColor(34, 197, 94); // green-500
    } else if (pass === false) {
      doc.setTextColor(239, 68, 68); // red-500
    } else {
      doc.setTextColor(31, 41, 55); // gray-800
    }

    doc.text(String(value), margin + 60, y);
    return y + 7;
  };

  // Helper to check if we need a new page
  const checkPageBreak = (y, spaceNeeded = 20) => {
    if (y + spaceNeeded > doc.internal.pageSize.getHeight() - margin) {
      doc.addPage();
      return 20;
    }
    return y;
  };

  // Title
  doc.setFontSize(22);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(79, 70, 229); // indigo-600
  doc.text('Analise This', pageWidth / 2, yPosition, { align: 'center' });

  yPosition += 8;
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(107, 114, 128); // gray-500
  doc.text('Audio Analysis Report', pageWidth / 2, yPosition, { align: 'center' });

  yPosition += 15;

  // File Information Section
  yPosition = checkPageBreak(yPosition, 60);
  yPosition = addSectionHeader('File Information', yPosition);
  yPosition = addKeyValue('Filename', file_info.filename, yPosition);
  yPosition = addKeyValue('Duration', file_info.duration, yPosition);
  yPosition = addKeyValue('Format', file_info.format, yPosition);
  yPosition = addKeyValue('Sample Rate', `${file_info.sample_rate} Hz`, yPosition);
  yPosition = addKeyValue('Channels', file_info.channels, yPosition);
  yPosition = addKeyValue('Bitrate', file_info.bitrate, yPosition);

  yPosition += 5;

  // ACX Compliance Section
  yPosition = checkPageBreak(yPosition, 80);
  yPosition = addSectionHeader('ACX Compliance', yPosition);

  // Overall status badge
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  const overallPass = acx_compliance.overall_pass;
  if (overallPass) {
    doc.setFillColor(220, 252, 231); // green background
    doc.setTextColor(22, 101, 52); // green text
  } else {
    doc.setFillColor(254, 226, 226); // red background
    doc.setTextColor(153, 27, 27); // red text
  }
  const statusText = overallPass ? 'PASS' : 'FAIL';
  const statusWidth = doc.getTextWidth(statusText) + 10;
  doc.roundedRect(pageWidth - margin - statusWidth, yPosition - 5, statusWidth, 8, 2, 2, 'F');
  doc.text(statusText, pageWidth - margin - statusWidth / 2, yPosition, { align: 'center' });

  yPosition += 5;

  // ACX checks
  yPosition = addKeyValue('RMS Level', `${acx_compliance.rms.value.toFixed(1)} dB (${acx_compliance.rms.range})`, yPosition, acx_compliance.rms.pass);
  yPosition = addKeyValue('Peak Level', `${acx_compliance.peak.value.toFixed(1)} dB (${acx_compliance.peak.threshold})`, yPosition, acx_compliance.peak.pass);
  yPosition = addKeyValue('Noise Floor', `${acx_compliance.noise_floor.value.toFixed(1)} dB (${acx_compliance.noise_floor.threshold})`, yPosition, acx_compliance.noise_floor.pass);
  yPosition = addKeyValue('Format', acx_compliance.format.value, yPosition, acx_compliance.format.pass);
  yPosition = addKeyValue('Duration', `${(acx_compliance.duration.value / 60).toFixed(1)} min (< ${acx_compliance.duration.max / 60} min)`, yPosition, acx_compliance.duration.pass);
  yPosition = addKeyValue('Room Tone', acx_compliance.room_tone.detected ? 'Detected' : 'Not Detected', yPosition, acx_compliance.room_tone.pass);

  yPosition += 5;

  // Additional Metrics Section
  yPosition = checkPageBreak(yPosition, 50);
  yPosition = addSectionHeader('Additional Metrics', yPosition);
  yPosition = addKeyValue('LUFS', additional_metrics.lufs.toFixed(1), yPosition);
  yPosition = addKeyValue('True Peak', `${additional_metrics.true_peak.toFixed(1)} dB`, yPosition);
  yPosition = addKeyValue('Reverb Level', additional_metrics.reverb_level, yPosition);
  if (additional_metrics.dynamic_range !== undefined) {
    yPosition = addKeyValue('Dynamic Range', `${additional_metrics.dynamic_range.toFixed(1)} dB`, yPosition);
  }

  yPosition += 5;

  // ElevenLabs Section
  yPosition = checkPageBreak(yPosition, 80);

  const hasNewElevenLabsFormat = elevenlabs && elevenlabs.overall;

  if (hasNewElevenLabsFormat) {
    yPosition = addSectionHeader('ElevenLabs Voice Cloning Suitability', yPosition);

    // Overall suitability
    const suitability = elevenlabs.overall.suitability.toUpperCase();
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');

    // Color based on suitability
    if (suitability === 'EXCELLENT') {
      doc.setFillColor(220, 252, 231);
      doc.setTextColor(22, 101, 52);
    } else if (suitability === 'GOOD') {
      doc.setFillColor(219, 234, 254);
      doc.setTextColor(30, 58, 138);
    } else if (suitability === 'ACCEPTABLE') {
      doc.setFillColor(254, 249, 195);
      doc.setTextColor(161, 98, 7);
    } else {
      doc.setFillColor(254, 226, 226);
      doc.setTextColor(153, 27, 27);
    }

    const suitabilityText = `${suitability} (${elevenlabs.overall.criteria_met}/${elevenlabs.overall.total_criteria} criteria met)`;
    const suitabilityWidth = doc.getTextWidth(suitabilityText) + 10;
    doc.roundedRect(pageWidth - margin - suitabilityWidth, yPosition - 5, suitabilityWidth, 8, 2, 2, 'F');
    doc.text(suitabilityText, pageWidth - margin - suitabilityWidth / 2, yPosition, { align: 'center' });

    yPosition += 8;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(75, 85, 99);
    const messageLines = doc.splitTextToSize(elevenlabs.overall.message, pageWidth - 2 * margin);
    doc.text(messageLines, margin, yPosition);
    yPosition += messageLines.length * 5 + 5;

    // Cloning type recommendation
    yPosition = checkPageBreak(yPosition);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(75, 85, 99);
    doc.text('Recommended Cloning Type:', margin, yPosition);
    yPosition += 6;

    doc.setFont('helvetica', 'normal');
    doc.setTextColor(31, 41, 55);
    const cloningText = `${elevenlabs.cloning_type.recommended.toUpperCase()} - ${elevenlabs.cloning_type.message}`;
    const cloningLines = doc.splitTextToSize(cloningText, pageWidth - 2 * margin - 5);
    doc.text(cloningLines, margin + 5, yPosition);
    yPosition += cloningLines.length * 5 + 3;

    // Volume check
    yPosition = checkPageBreak(yPosition);
    yPosition = addKeyValue('Volume/Loudness', elevenlabs.volume.pass ? 'PASS' : 'NEEDS ADJUSTMENT', yPosition, elevenlabs.volume.pass);
    yPosition = addKeyValue('  RMS', `${elevenlabs.volume.rms.toFixed(1)} dB`, yPosition);
    yPosition = addKeyValue('  True Peak', `${elevenlabs.volume.true_peak.toFixed(1)} dB`, yPosition);

    // Format check
    yPosition = checkPageBreak(yPosition);
    yPosition = addKeyValue('Audio Format', elevenlabs.format.pass ? 'SUITABLE' : 'NEEDS CONVERSION', yPosition, elevenlabs.format.pass);
    yPosition = addKeyValue('  Current', elevenlabs.format.current, yPosition);

    // Quality checklist
    yPosition = checkPageBreak(yPosition, 30);
    yPosition += 3;
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(75, 85, 99);
    doc.text('Quality Checklist:', margin, yPosition);
    yPosition += 7;

    yPosition = addKeyValue('  Clean Audio', elevenlabs.quality_checklist.clean_audio.pass ? 'PASS' : 'FAIL', yPosition, elevenlabs.quality_checklist.clean_audio.pass);
    yPosition = addKeyValue('  No Reverb/Echo', elevenlabs.quality_checklist.no_reverb.pass ? 'PASS' : 'FAIL', yPosition, elevenlabs.quality_checklist.no_reverb.pass);
    yPosition = addKeyValue('  Consistent Volume', elevenlabs.quality_checklist.consistent_volume.pass ? 'PASS' : 'FAIL', yPosition, elevenlabs.quality_checklist.consistent_volume.pass);
  } else {
    // Old format fallback
    yPosition = addSectionHeader('ElevenLabs Compliance', yPosition);
    yPosition = addKeyValue('Length', `${elevenlabs.length_minutes?.toFixed(1) || 'N/A'} min`, yPosition, elevenlabs.length_ok);
    yPosition = addKeyValue('Quality', elevenlabs.quality_ok ? 'Good' : 'Poor', yPosition, elevenlabs.quality_ok);
  }

  // Footer
  yPosition = checkPageBreak(yPosition, 20);
  const pageHeight = doc.internal.pageSize.getHeight();
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(156, 163, 175); // gray-400
  const footerText = 'Generated by AnaliseThis - https://analisethis.frankyredente.com';
  doc.text(footerText, pageWidth / 2, pageHeight - 10, { align: 'center' });

  // Generate filename with timestamp
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `analise-this-report_${file_info.filename.replace(/\.[^/.]+$/, '')}_${timestamp}.pdf`;

  // Save the PDF
  doc.save(filename);
};
