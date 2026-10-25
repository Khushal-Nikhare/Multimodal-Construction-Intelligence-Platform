/**
 * SafetyAnalyzer.jsx
 * FR-01 — Construction Site Safety Image Analysis
 *
 * Accepts a construction-site image + optional location/description text,
 * submits them to POST /api/safety/analyze via multipart/form-data, and
 * renders structured hazard findings returned by the AI backend.
 */

import { useRef, useState, useCallback } from 'react';
import axios from 'axios';
import styles from './SafetyAnalyzer.module.css';
import { apiUrl } from './api';

// ─── Constants ────────────────────────────────────────────────────────────────
const API_URL = apiUrl('/api/safety/analyze');
const MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const SEVERITY_ICONS = {
  LOW: '🟢',
  MEDIUM: '🟡',
  HIGH: '🟠',
  CRITICAL: '🔴',
};

const RISK_ICONS = {
  LOW: '✅',
  MEDIUM: '⚠️',
  HIGH: '🚨',
  CRITICAL: '🆘',
  UNKNOWN: '❓',
};

const CATEGORY_LABELS = {
  PPE_NON_COMPLIANCE: 'PPE Compliance',
  FALL_HAZARD: 'Fall Hazard',
  ELECTRICAL_HAZARD: 'Electrical',
  STRUCTURAL_HAZARD: 'Structural',
  ENVIRONMENTAL_HAZARD: 'Environmental',
  EQUIPMENT_HAZARD: 'Equipment',
  OTHER: 'Other',
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function severityClass(sev) {
  switch ((sev || '').toUpperCase()) {
    case 'LOW': return styles.sevLow;
    case 'MEDIUM': return styles.sevMedium;
    case 'HIGH': return styles.sevHigh;
    case 'CRITICAL': return styles.sevCritical;
    default: return '';
  }
}

function badgeClass(sev) {
  switch ((sev || '').toUpperCase()) {
    case 'LOW': return styles.badgeLow;
    case 'MEDIUM': return styles.badgeMedium;
    case 'HIGH': return styles.badgeHigh;
    case 'CRITICAL': return styles.badgeCritical;
    default: return '';
  }
}

function riskClass(risk) {
  switch ((risk || '').toUpperCase()) {
    case 'LOW': return styles.riskLow;
    case 'MEDIUM': return styles.riskMedium;
    case 'HIGH': return styles.riskHigh;
    case 'CRITICAL': return styles.riskCritical;
    default: return styles.riskUnknown;
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function HazardCard({ hazard, index }) {
  return (
    <div
      className={`${styles.hazardCard} ${severityClass(hazard.severity)}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className={styles.hazardHeader}>
        <div>
          <div className={styles.hazardTitle}>{hazard.title}</div>
          <div className={styles.hazardCategory}>
            {CATEGORY_LABELS[hazard.category] || hazard.category}
          </div>
        </div>
        <span className={`${styles.severityBadge} ${badgeClass(hazard.severity)}`}>
          {SEVERITY_ICONS[hazard.severity] || '⚪'} {hazard.severity}
        </span>
      </div>

      <p className={styles.hazardDescription}>{hazard.description}</p>

      {hazard.location_hint && (
        <div className={styles.hazardMeta}>
          <span className={styles.metaItem}>📍 {hazard.location_hint}</span>
          {hazard.id && (
            <span className={styles.metaItem} style={{ color: 'var(--clr-text-dim)', fontFamily: 'monospace', fontSize: '0.72rem' }}>
              {hazard.id}
            </span>
          )}
        </div>
      )}

      {hazard.corrective_action && (
        <div className={styles.corrective}>
          <div className={styles.correctiveLabel}>Corrective Action</div>
          {hazard.corrective_action}
        </div>
      )}
    </div>
  );
}

function PPESummary({ ppeSummary }) {
  if (!ppeSummary) return null;
  const { compliant_items = [], missing_or_non_compliant = [] } = ppeSummary;
  if (compliant_items.length === 0 && missing_or_non_compliant.length === 0) return null;

  return (
    <div>
      <div className={styles.sectionTitle}>🦺 PPE Status</div>
      <div className={styles.ppeGrid}>
        {compliant_items.length > 0 && (
          <div className={styles.ppePanel}>
            <div className={`${styles.ppePanelTitle} ${styles.compliant}`}>
              ✅ Compliant Items
            </div>
            <ul className={styles.ppeList}>
              {compliant_items.map((item, i) => (
                <li key={i} className={styles.ppeItem}>✔ {item}</li>
              ))}
            </ul>
          </div>
        )}
        {missing_or_non_compliant.length > 0 && (
          <div className={styles.ppePanel}>
            <div className={`${styles.ppePanelTitle} ${styles.missing}`}>
              ❌ Missing / Non-Compliant
            </div>
            <ul className={styles.ppeList}>
              {missing_or_non_compliant.map((item, i) => (
                <li key={i} className={styles.ppeItem}>✖ {item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function AnalysisResults({ data }) {
  if (!data) return null;

  const {
    hazards_identified = [],
    overall_site_risk = 'UNKNOWN',
    ppe_summary,
    uncertainty_note,
    disclaimer,
  } = data;

  const riskKey = (overall_site_risk || 'UNKNOWN').toUpperCase();

  return (
    <div className={styles.resultsSection}>
      {/* Overall risk banner */}
      <div className={`${styles.riskBanner} ${riskClass(riskKey)}`}>
        <div>
          <div className={styles.riskLabel}>Overall Site Risk</div>
          <div className={styles.riskValue}>{riskKey}</div>
        </div>
        <div className={styles.riskIcon}>{RISK_ICONS[riskKey] || '❓'}</div>
      </div>

      {/* Hazard cards */}
      {hazards_identified.length > 0 ? (
        <div>
          <div className={styles.sectionTitle}>
            🔍 Identified Hazards ({hazards_identified.length})
          </div>
          <div className={styles.hazardGrid}>
            {hazards_identified.map((hazard, idx) => (
              <HazardCard key={hazard.id || idx} hazard={hazard} index={idx} />
            ))}
          </div>
        </div>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>✅</div>
          <p>No specific hazards were identified in this image.</p>
        </div>
      )}

      {/* PPE summary */}
      <PPESummary ppeSummary={ppe_summary} />

      {/* Uncertainty note */}
      {uncertainty_note && (
        <div className={styles.uncertaintyNote}>
          <span>⚠️</span>
          <span>{uncertainty_note}</span>
        </div>
      )}

      {/* Disclaimer */}
      {disclaimer && (
        <div className={styles.disclaimer}>
          <span>ℹ️</span>
          <span>{disclaimer}</span>
        </div>
      )}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function SafetyAnalyzer() {
  // Form state
  const [image, setImage] = useState(null);           // { file, previewUrl, name, size }
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [dragOver, setDragOver] = useState(false);

  // Request lifecycle
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Analysis result (matches backend UniversalResponse.data)
  const [result, setResult] = useState(null);

  const fileInputRef = useRef(null);

  // ── Image selection & validation ──────────────────────────────────────────
  const handleFile = useCallback((file) => {
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError(`Unsupported file type "${file.type}". Please upload a JPEG, PNG, or WebP image.`);
      return;
    }

    if (file.size > MAX_FILE_BYTES) {
      setError(`File is too large (${formatBytes(file.size)}). Maximum allowed size is 10 MB.`);
      return;
    }

    setError(null);
    setResult(null);

    const previewUrl = URL.createObjectURL(file);
    setImage({ file, previewUrl, name: file.name, size: file.size });
  }, []);

  const handleFileInput = (e) => handleFile(e.target.files?.[0]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files?.[0]);
  }, [handleFile]);

  const handleDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const handleDragLeave = () => setDragOver(false);

  // ── Form submission ────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!image?.file) {
      setError('Please select a construction site image before submitting.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('image', image.file);
    if (location.trim()) formData.append('location', location.trim());
    if (description.trim()) formData.append('description', description.trim());

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000, // 2-minute timeout for AI processing
      });

      const body = response.data;

      if (body.status === 'error') {
        setError(body.error?.message || 'The analysis returned an error. Please try again.');
      } else {
        setResult(body.data);
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('The request timed out. The AI service may be busy — please retry in a moment.');
      } else if (err.response) {
        const serverErr = err.response.data?.error || err.response.data?.detail;
        const msg =
          typeof serverErr === 'object'
            ? serverErr.message || JSON.stringify(serverErr)
            : serverErr || `Server error ${err.response.status}`;
        setError(msg);
      } else {
        setError('Network error — please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Reset ─────────────────────────────────────────────────────────────────
  const handleClear = () => {
    if (image?.previewUrl) URL.revokeObjectURL(image.previewUrl);
    setImage(null);
    setLocation('');
    setDescription('');
    setError(null);
    setResult(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // ─── Render ───────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerIcon}>🦺</div>
        <div className={styles.headerText}>
          <h1>Safety Image Analysis</h1>
          <p>Upload a construction site image to identify hazards and assess risk with AI</p>
        </div>
        <span className={styles.badge}>FR-01</span>
      </header>

      {/* Input form */}
      <section className={styles.card}>
        <form onSubmit={handleSubmit} id="safety-analysis-form" noValidate>
          <div className={styles.sectionTitle}>📷 Site Image</div>

          {/* Drop zone */}
          <div
            className={`${styles.dropZone} ${dragOver ? styles.dragOver : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            aria-label="Upload construction site image"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              id="site-image-input"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileInput}
              aria-label="Construction site image file input"
              onClick={(e) => e.stopPropagation()}
            />
            <div className={styles.dropIcon}>🏗️</div>
            <div className={styles.dropLabel}>
              {image ? 'Replace image' : 'Drop image here or click to browse'}
            </div>
            <div className={styles.dropHint}>JPEG · PNG · WebP · max 10 MB</div>
          </div>

          {/* Image preview */}
          {image && (
            <div className={styles.previewWrapper}>
              <img
                src={image.previewUrl}
                alt="Selected construction site"
                className={styles.previewImg}
              />
              <div className={styles.previewOverlay}>
                <span className={styles.chipLabel}>{image.name}</span>
                <span className={styles.chipLabel}>{formatBytes(image.size)}</span>
              </div>
            </div>
          )}

          {/* Text inputs */}
          <div className={styles.formGrid}>
            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel} htmlFor="site-location">
                Location <span style={{ opacity: 0.5 }}>(optional)</span>
              </label>
              <input
                id="site-location"
                className={styles.fieldInput}
                type="text"
                placeholder="e.g. Tower B, 4th Floor Slab"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                maxLength={200}
              />
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel} htmlFor="site-description">
                Description <span style={{ opacity: 0.5 }}>(optional)</span>
              </label>
              <textarea
                id="site-description"
                className={styles.fieldTextarea}
                placeholder="e.g. Workers preparing rebar cages near perimeter edge"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={1000}
              />
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 'var(--sp-3)', marginTop: 'var(--sp-6)' }}>
            <button
              type="submit"
              id="analyze-submit-btn"
              className={styles.submitBtn}
              disabled={loading || !image}
              style={{ flex: 1 }}
              aria-busy={loading}
            >
              {loading ? (
                <>
                  <span className={styles.spinner} role="status" aria-label="Analysing" />
                  Analysing…
                </>
              ) : (
                <>🔍 Analyse Safety</>
              )}
            </button>

            {(image || result) && (
              <button
                type="button"
                id="clear-btn"
                onClick={handleClear}
                style={{
                  padding: 'var(--sp-4) var(--sp-5)',
                  background: 'var(--clr-surface-2)',
                  border: '1px solid var(--clr-border)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--clr-text-muted)',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  transition: 'border-color var(--transition-fast)',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--clr-border-hover)')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--clr-border)')}
              >
                ✕ Clear
              </button>
            )}
          </div>
        </form>
      </section>

      {/* Error display */}
      {error && (
        <div className={styles.errorBanner} role="alert" id="error-message">
          <span className={styles.errorIcon}>⛔</span>
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <section className={styles.card} id="analysis-results">
          <div className={styles.sectionTitle}>📊 Analysis Results</div>
          <AnalysisResults data={result} />
        </section>
      )}
    </div>
  );
}
