/**
 * CrackDetection.jsx
 * FR-02 — Structural Crack Detection and Assessment
 *
 * Accepts a structural surface image + optional surface/element context,
 * submits to POST /api/cracks/analyze via multipart/form-data, and
 * renders the structured crack findings returned by the AI backend.
 */

import { useRef, useState, useCallback } from 'react';
import axios from 'axios';
import styles from './CrackDetection.module.css';
import { apiUrl } from './api';

// ─── Constants ────────────────────────────────────────────────────────────────
const API_URL = apiUrl('/api/cracks/analyze');
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const SURFACE_OPTIONS = [
  { value: '', label: '— Select surface type —' },
  { value: 'concrete', label: 'Concrete' },
  { value: 'brick_masonry', label: 'Brick Masonry' },
  { value: 'plaster', label: 'Plaster' },
  { value: 'stone', label: 'Stone' },
  { value: 'other', label: 'Other' },
];

const ELEMENT_OPTIONS = [
  { value: '', label: '— Select structural element —' },
  { value: 'beam', label: 'Beam' },
  { value: 'column', label: 'Column' },
  { value: 'shear_wall', label: 'Shear Wall' },
  { value: 'slab', label: 'Slab' },
  { value: 'non_structural_wall', label: 'Non-Structural Wall' },
  { value: 'foundation', label: 'Foundation' },
];

// Human-readable labels for AI enum values
const CRACK_TYPE_LABELS = {
  HAIRLINE: 'Hairline Crack',
  VERTICAL: 'Vertical Crack',
  HORIZONTAL: 'Horizontal Crack',
  DIAGONAL_SHEAR: 'Diagonal / Shear Crack',
  MAP_CRACKING: 'Map / Pattern Cracking',
  SPALLING: 'Spalling',
  OTHER: 'Other Pattern',
};

const WIDTH_LABELS = {
  HAIRLINE_LESS_0_2MM: '< 0.2 mm (Hairline)',
  FINE_0_2_TO_1MM: '0.2 – 1 mm (Fine)',
  MEDIUM_1_TO_3_MM: '1 – 3 mm (Medium)',
  WIDE_OVER_3MM: '> 3 mm (Wide)',
  INDETERMINATE: 'Indeterminate',
};

const SEVERITY_SHORT = {
  COSMETIC: 'Cosmetic',
  MINOR_NON_STRUCTURAL: 'Minor',
  MODERATE_STRUCTURAL: 'Moderate',
  SEVERE_STRUCTURAL: 'Severe',
  CRITICAL: 'Critical',
  INDETERMINATE: 'Indeterminate',
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function severityCardClass(sev) {
  const key = (sev || '').toUpperCase();
  const map = {
    COSMETIC: styles.sevCosmetic,
    MINOR_NON_STRUCTURAL: styles.sevMinor,
    MODERATE_STRUCTURAL: styles.sevModerate,
    SEVERE_STRUCTURAL: styles.sevSevere,
    CRITICAL: styles.sevCritical,
    INDETERMINATE: styles.sevIndeterminate,
  };
  return map[key] || styles.sevIndeterminate;
}

function severityBadgeClass(sev) {
  const key = (sev || '').toUpperCase();
  const map = {
    COSMETIC: styles.badgeCosmetic,
    MINOR_NON_STRUCTURAL: styles.badgeMinor,
    MODERATE_STRUCTURAL: styles.badgeModerate,
    SEVERE_STRUCTURAL: styles.badgeSevere,
    CRITICAL: styles.badgeCritical,
    INDETERMINATE: styles.badgeIndeterminate,
  };
  return map[key] || styles.badgeIndeterminate;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function FindingCard({ finding, index }) {
  const {
    crack_type,
    apparent_width_category,
    orientation,
    preliminary_severity,
    probable_causes = [],
    recommended_inspections = [],
  } = finding;

  return (
    <div
      className={`${styles.findingCard} ${severityCardClass(preliminary_severity)}`}
      style={{ animationDelay: `${index * 90}ms` }}
    >
      {/* Header */}
      <div className={styles.findingHeader}>
        <div>
          <div className={styles.findingType}>
            {CRACK_TYPE_LABELS[crack_type] || crack_type}
          </div>
          <div className={styles.findingMeta}>
            {orientation && (
              <span className={styles.metaChip}>↗ {orientation.replace(/_/g, ' ')}</span>
            )}
            {apparent_width_category && (
              <span className={styles.metaChip}>⟷ {WIDTH_LABELS[apparent_width_category] || apparent_width_category}</span>
            )}
          </div>
        </div>
        <span className={`${styles.severityBadge} ${severityBadgeClass(preliminary_severity)}`}>
          {SEVERITY_SHORT[preliminary_severity] || preliminary_severity}
        </span>
      </div>

      {/* Causes & inspections */}
      <div className={styles.twoCol}>
        {probable_causes.length > 0 && (
          <div className={styles.subsection}>
            <div className={styles.subsectionTitle}>🔎 Probable Causes</div>
            {probable_causes.map((cause, i) => (
              <div key={i} className={styles.listItem}>
                <span>▸</span>
                <span>{cause}</span>
              </div>
            ))}
          </div>
        )}

        {recommended_inspections.length > 0 && (
          <div className={styles.subsection}>
            <div className={styles.subsectionTitle}>🛠 Recommended Actions</div>
            {recommended_inspections.map((action, i) => (
              <div key={i} className={styles.listItem}>
                <span>✓</span>
                <span>{action}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ImageQualityPanel({ assessment }) {
  if (!assessment) return null;
  const { clarity, lighting, recommendation } = assessment;

  const clarityColour =
    clarity === 'SUFFICIENT' ? '#6ee7b7' : clarity === 'BLURRY' ? '#fcd34d' : '#fca5a5';
  const lightingColour =
    lighting === 'ADEQUATE' ? '#6ee7b7' : lighting === 'POOR' ? '#fca5a5' : '#fcd34d';

  return (
    <div>
      <div className={styles.sectionTitle}>🔬 Image Quality Assessment</div>
      <div className={styles.qualityPanel}>
        <div className={styles.qualityStat}>
          <div className={styles.qualityStatLabel}>Clarity</div>
          <div className={styles.qualityStatValue} style={{ color: clarityColour }}>
            {clarity || '—'}
          </div>
        </div>
        <div className={styles.qualityStat}>
          <div className={styles.qualityStatLabel}>Lighting</div>
          <div className={styles.qualityStatValue} style={{ color: lightingColour }}>
            {lighting || '—'}
          </div>
        </div>
        <div className={styles.qualityStat}>
          <div className={styles.qualityStatLabel}>Overall</div>
          <div className={styles.qualityStatValue}>
            {clarity === 'SUFFICIENT' && lighting === 'ADEQUATE' ? '✅ Good' : '⚠️ Limited'}
          </div>
        </div>
      </div>
      {recommendation && (
        <div className={styles.qualityRec}>⚠️ {recommendation}</div>
      )}
    </div>
  );
}

function AnalysisResults({ data }) {
  if (!data) return null;

  const {
    crack_detected,
    findings = [],
    image_quality_assessment,
    disclaimer,
  } = data;

  return (
    <div className={styles.resultsSection}>
      {/* Detection banner */}
      <div className={`${styles.detectedBanner} ${crack_detected ? styles.detectedTrue : styles.detectedFalse}`}>
        <div>
          <div className={styles.detectedLabel}>Crack Detection Result</div>
          <div className={styles.detectedValue}>
            {crack_detected === null ? 'Uncertain' : crack_detected ? 'Crack(s) Detected' : 'No Crack Detected'}
          </div>
        </div>
        <div className={styles.detectedIcon}>
          {crack_detected === null ? '❓' : crack_detected ? '⚠️' : '✅'}
        </div>
      </div>

      {/* Finding cards */}
      {findings.length > 0 ? (
        <div>
          <div className={styles.sectionTitle}>
            🔍 Crack Findings ({findings.length})
          </div>
          <div className={styles.findingGrid}>
            {findings.map((f, i) => (
              <FindingCard key={i} finding={f} index={i} />
            ))}
          </div>
        </div>
      ) : crack_detected === false ? (
        <div className={styles.noCrack}>
          <div className={styles.noCrackIcon}>🏗️</div>
          <p>No structural crack patterns were identified in this image.</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--clr-text-dim)' }}>
            Consider taking a closer photograph with a reference scale for more accurate assessment.
          </p>
        </div>
      ) : null}

      {/* Image quality */}
      <ImageQualityPanel assessment={image_quality_assessment} />

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
export default function CrackDetection() {
  // Form state
  const [image, setImage] = useState(null);
  const [surfaceType, setSurfaceType] = useState('');
  const [structuralElement, setStructuralElement] = useState('');
  const [description, setDescription] = useState('');
  const [dragOver, setDragOver] = useState(false);

  // Request lifecycle
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const fileInputRef = useRef(null);

  // ── Image selection ───────────────────────────────────────────────────────
  const handleFile = useCallback((file) => {
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError(`Unsupported file type "${file.type}". Please upload JPEG, PNG, or WebP.`);
      return;
    }
    if (file.size > MAX_FILE_BYTES) {
      setError(`File is too large (${formatBytes(file.size)}). Maximum allowed size is 10 MB.`);
      return;
    }

    setError(null);
    setResult(null);
    setImage({ file, previewUrl: URL.createObjectURL(file), name: file.name, size: file.size });
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
      setError('Please select a structural surface image before submitting.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('image', image.file);
    if (surfaceType) formData.append('surface_type', surfaceType);
    if (structuralElement) formData.append('structural_element', structuralElement);
    if (description.trim()) formData.append('description', description.trim());

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,
      });

      const body = response.data;

      if (body.status === 'error') {
        setError(body.error?.message || 'Analysis returned an error. Please try again.');
      } else {
        setResult(body.data);
      }
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. The AI service may be busy — please retry.');
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
    setSurfaceType('');
    setStructuralElement('');
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
        <div className={styles.headerIcon}>🏚️</div>
        <div className={styles.headerText}>
          <h1>Structural Crack Detection</h1>
          <p>Upload a surface image for AI-assisted crack classification and preliminary severity assessment</p>
        </div>
        <span className={styles.badge}>FR-02</span>
      </header>

      {/* Input form */}
      <section className={styles.card}>
        <form onSubmit={handleSubmit} id="crack-analysis-form" noValidate>
          <div className={styles.sectionTitle}>📷 Surface Image</div>

          {/* Drop zone */}
          <div
            className={`${styles.dropZone} ${dragOver ? styles.dragOver : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            aria-label="Upload structural surface image"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              id="crack-image-input"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileInput}
              aria-label="Structural surface image file input"
              onClick={(e) => e.stopPropagation()}
            />
            <div className={styles.dropIcon}>🧱</div>
            <div className={styles.dropLabel}>
              {image ? 'Replace image' : 'Drop surface image here or click to browse'}
            </div>
            <div className={styles.dropHint}>JPEG · PNG · WebP · max 10 MB</div>
          </div>

          {/* Image preview */}
          {image && (
            <div className={styles.previewWrapper}>
              <img src={image.previewUrl} alt="Selected structural surface" className={styles.previewImg} />
              <div className={styles.previewOverlay}>
                <span className={styles.chipLabel}>{image.name}</span>
                <span className={styles.chipLabel}>{formatBytes(image.size)}</span>
              </div>
            </div>
          )}

          {/* Surface type & structural element selects */}
          <div className={styles.formGrid}>
            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel} htmlFor="surface-type">
                Surface Type <span style={{ opacity: 0.5 }}>(optional)</span>
              </label>
              <select
                id="surface-type"
                className={styles.fieldSelect}
                value={surfaceType}
                onChange={(e) => setSurfaceType(e.target.value)}
              >
                {SURFACE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.fieldLabel} htmlFor="structural-element">
                Structural Element <span style={{ opacity: 0.5 }}>(optional)</span>
              </label>
              <select
                id="structural-element"
                className={styles.fieldSelect}
                value={structuralElement}
                onChange={(e) => setStructuralElement(e.target.value)}
              >
                {ELEMENT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Description */}
          <div className={`${styles.fieldGroup} ${styles.formGridFull}`}>
            <label className={styles.fieldLabel} htmlFor="crack-description">
              Additional Context <span style={{ opacity: 0.5 }}>(optional)</span>
            </label>
            <textarea
              id="crack-description"
              className={styles.fieldTextarea}
              placeholder="e.g. Crack appeared after last monsoon; building is 12 years old; located near column C3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={1000}
            />
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 'var(--sp-3)', marginTop: 'var(--sp-6)' }}>
            <button
              type="submit"
              id="crack-analyze-btn"
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
                <>🔍 Detect Cracks</>
              )}
            </button>

            {(image || result) && (
              <button
                type="button"
                id="crack-clear-btn"
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

      {/* Error */}
      {error && (
        <div className={styles.errorBanner} role="alert" id="crack-error-message">
          <span className={styles.errorIcon}>⛔</span>
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <section className={styles.card} id="crack-analysis-results">
          <div className={styles.sectionTitle}>📊 Analysis Results</div>
          <AnalysisResults data={result} />
        </section>
      )}
    </div>
  );
}
