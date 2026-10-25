import { useState } from 'react'
import axios from 'axios'
import styles from './Valuation.module.css'
import ErrorBoundary from './ErrorBoundary'

const PROPERTY_TYPES = [
  { value: 'residential_apartment', label: 'Residential Apartment' },
  { value: 'independent_house', label: 'Independent House / Builder Floor' },
  { value: 'villa', label: 'Luxury Gated Villa' },
  { value: 'commercial_office', label: 'Commercial Office Space' },
  { value: 'commercial_retail', label: 'Retail Shop / Showroom' },
  { value: 'plot_land', label: 'Residential / Commercial Plot' },
]

const POPULAR_LOCALITIES = [
  { city: 'Bengaluru', locality: 'Whitefield', pin: '560066' },
  { city: 'Bengaluru', locality: 'Indiranagar', pin: '560038' },
  { city: 'Bengaluru', locality: 'Koramangala', pin: '560034' },
  { city: 'Mumbai', locality: 'Bandra West', pin: '400050' },
  { city: 'Mumbai', locality: 'Andheri West', pin: '400058' },
  { city: 'Delhi', locality: 'South Delhi', pin: '110017' },
  { city: 'Delhi', locality: 'Dwarka', pin: '110075' },
  { city: 'Hyderabad', locality: 'Gachibowli', pin: '500032' },
  { city: 'Hyderabad', locality: 'Hitec City', pin: '500081' },
  { city: 'Pune', locality: 'Baner', pin: '411045' },
]

const AVAILABLE_AMENITIES = [
  { id: 'covered_parking', label: 'Covered Car Parking' },
  { id: 'clubhouse', label: 'Clubhouse & Gym' },
  { id: 'power_backup', label: '100% Power Backup' },
  { id: 'swimming_pool', label: 'Swimming Pool' },
  { id: 'security_24x7', label: '24/7 Gated Security' },
  { id: 'lift', label: 'High-speed Elevators' },
  { id: 'piped_gas', label: 'Piped Gas Connection' },
  { id: 'solar_panels', label: 'Rooftop Solar Array' },
]

const PRESETS = [
  {
    label: 'Whitefield 3BHK (1,450 sq.ft, 4 yrs)',
    city: 'Bengaluru',
    locality: 'Whitefield',
    area: 1450,
    carpet: 1180,
    type: 'residential_apartment',
    age: 4,
    condition: 'good',
    floor: 6,
    totalFloors: 14,
    amenities: ['covered_parking', 'clubhouse', 'power_backup', 'swimming_pool'],
  },
  {
    label: 'Bandra West Luxury (2,100 sq.ft, 2 yrs)',
    city: 'Mumbai',
    locality: 'Bandra West',
    area: 2100,
    carpet: 1750,
    type: 'residential_apartment',
    age: 2,
    condition: 'excellent',
    floor: 12,
    totalFloors: 25,
    amenities: ['covered_parking', 'clubhouse', 'power_backup', 'swimming_pool', 'security_24x7', 'lift'],
  },
  {
    label: 'Gachibowli Commercial (3,500 sq.ft)',
    city: 'Hyderabad',
    locality: 'Gachibowli',
    area: 3500,
    carpet: 2900,
    type: 'commercial_office',
    age: 3,
    condition: 'good',
    floor: 4,
    totalFloors: 8,
    amenities: ['covered_parking', 'power_backup', 'security_24x7', 'lift'],
  },
]

function ValuationInner() {
  const [city, setCity] = useState('Bengaluru')
  const [locality, setLocality] = useState('Whitefield')
  const [pincode, setPincode] = useState('560066')
  const [builtUpArea, setBuiltUpArea] = useState(1450)
  const [carpetArea, setCartpetArea] = useState(1180)
  const [propertyType, setPropertyType] = useState('residential_apartment')
  const [ageYears, setAgeYears] = useState(4)
  const [condition, setCondition] = useState('good')
  const [floorNumber, setFloorNumber] = useState(6)
  const [totalFloors, setTotalFloors] = useState(14)
  const [selectedAmenities, setSelectedAmenities] = useState([
    'covered_parking',
    'clubhouse',
    'power_backup',
    'swimming_pool',
  ])

  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [valuationData, setValuationData] = useState(null)

  const handleToggleAmenity = (id) => {
    setSelectedAmenities((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    )
  }

  const handleApplyPreset = (p) => {
    setCity(p.city)
    setLocality(p.locality)
    setBuiltUpArea(p.area)
    setCartpetArea(p.carpet)
    setPropertyType(p.type)
    setAgeYears(p.age)
    setCondition(p.condition)
    setFloorNumber(p.floor)
    setTotalFloors(p.totalFloors)
    setSelectedAmenities(p.amenities)
    setErrorMsg(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Scenario 3.2 Client-side validation check
    if (!builtUpArea || parseFloat(builtUpArea) <= 0) {
      setErrorMsg('Built-up area must be strictly greater than 0 sq.ft.')
      return
    }
    if (!city.trim() || !locality.trim()) {
      setErrorMsg('City and Locality are required fields.')
      return
    }

    setLoading(true)
    setErrorMsg(null)

    try {
      // Step 3 & 4: Use FormData interface and submit via Axios POST
      const formData = new FormData()
      formData.append('city', city.trim())
      formData.append('locality', locality.trim())
      formData.append('built_up_area_sqft', builtUpArea.toString())
      if (carpetArea) formData.append('carpet_area_sqft', carpetArea.toString())
      formData.append('property_type', propertyType)
      formData.append('age_years', ageYears.toString())
      formData.append('condition', condition)
      formData.append('floor_number', floorNumber.toString())
      formData.append('total_floors', totalFloors.toString())
      if (pincode) formData.append('pincode', pincode.trim())
      if (selectedAmenities.length > 0) {
        formData.append('amenities', selectedAmenities.join(','))
      }

      const response = await axios.post('/api/real-estate-valuation', formData)

      if (response.data && response.data.status === 'success') {
        setValuationData(response.data.data)
      } else {
        throw new Error(response.data?.error?.message || 'Valuation processing failed')
      }
    } catch (err) {
      console.error('Valuation submission error:', err)
      const detail = err.response?.data?.error?.message || err.response?.data?.detail?.error?.message || err.message
      setErrorMsg(detail || 'Failed to connect to real estate valuation engine')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.valuationContainer}>
      {/* ── Header ── */}
      <header className={styles.headerSection}>
        <div className={styles.badge}>
          <span>💎</span>
          <span>FR-03 • Real Estate Valuation Engine</span>
        </div>
        <h1 className={styles.title}>Property Market Valuation & Investment Analytics</h1>
        <p className={styles.subtitle}>
          Estimate indicative property market values in Indian Rupees (₹), rate per square foot,
          rental yield potential, net ROI, and 5-year capital appreciation forecasts based on regional market benchmarks.
        </p>
      </header>

      {/* ── Main Layout ── */}
      <div className={styles.mainLayout}>
        {/* Left: Input Form Card */}
        <section className={styles.formCard}>
          <h2 className={styles.cardTitle}>
            <span>🏢</span>
            <span>Property Attributes</span>
          </h2>

          <div style={{ marginBottom: '1rem' }}>
            <span className={styles.formLabel}>Presets</span>
            <div className={styles.presetButtons}>
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  id={`val-preset-${idx}`}
                  className={styles.presetBtn}
                  onClick={() => handleApplyPreset(p)}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="val-city" className={styles.formLabel}>City *</label>
                <input
                  id="val-city"
                  type="text"
                  required
                  className={styles.formInput}
                  placeholder="e.g. Bengaluru"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="val-locality" className={styles.formLabel}>Locality / Area *</label>
                <input
                  id="val-locality"
                  type="text"
                  required
                  className={styles.formInput}
                  placeholder="e.g. Whitefield"
                  value={locality}
                  onChange={(e) => setLocality(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="val-built-area" className={styles.formLabel}>Built-Up Area (sq.ft) *</label>
                <input
                  id="val-built-area"
                  type="number"
                  step="10"
                  required
                  className={styles.formInput}
                  value={builtUpArea}
                  onChange={(e) => setBuiltUpArea(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="val-carpet-area" className={styles.formLabel}>Carpet Area (sq.ft)</label>
                <input
                  id="val-carpet-area"
                  type="number"
                  step="10"
                  className={styles.formInput}
                  value={carpetArea}
                  onChange={(e) => setCartpetArea(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="val-property-type" className={styles.formLabel}>Property Type</label>
              <select
                id="val-property-type"
                className={styles.formSelect}
                value={propertyType}
                onChange={(e) => setPropertyType(e.target.value)}
              >
                {PROPERTY_TYPES.map((pt) => (
                  <option key={pt.value} value={pt.value}>
                    {pt.label}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="val-age" className={styles.formLabel}>Building Age (Years)</label>
                <input
                  id="val-age"
                  type="number"
                  min="0"
                  max="100"
                  className={styles.formInput}
                  value={ageYears}
                  onChange={(e) => setAgeYears(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="val-condition" className={styles.formLabel}>Condition</label>
                <select
                  id="val-condition"
                  className={styles.formSelect}
                  value={condition}
                  onChange={(e) => setCondition(e.target.value)}
                >
                  <option value="excellent">Excellent / Brand New</option>
                  <option value="good">Good / Well Maintained</option>
                  <option value="needs_renovation">Needs Civil Renovation</option>
                </select>
              </div>
            </div>

            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="val-floor" className={styles.formLabel}>Floor Level</label>
                <input
                  id="val-floor"
                  type="number"
                  min="0"
                  max="120"
                  className={styles.formInput}
                  value={floorNumber}
                  onChange={(e) => setFloorNumber(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="val-total-floors" className={styles.formLabel}>Total Building Floors</label>
                <input
                  id="val-total-floors"
                  type="number"
                  min="1"
                  max="120"
                  className={styles.formInput}
                  value={totalFloors}
                  onChange={(e) => setTotalFloors(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.formGroup}>
              <span className={styles.formLabel}>Verified Amenities</span>
              <div className={styles.amenitiesGrid}>
                {AVAILABLE_AMENITIES.map((am) => (
                  <label key={am.id} className={styles.amenityCheckbox}>
                    <input
                      type="checkbox"
                      id={`amenity-${am.id}`}
                      checked={selectedAmenities.includes(am.id)}
                      onChange={() => handleToggleAmenity(am.id)}
                    />
                    <span>{am.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {errorMsg && (
              <div style={{ color: '#f87171', fontSize: '0.8125rem', marginTop: '0.5rem' }}>
                ⚠️ {errorMsg}
              </div>
            )}

            <button
              id="btn-evaluate-property"
              type="submit"
              disabled={loading}
              className={styles.submitBtn}
            >
              {loading ? (
                <>
                  <span className="spinner" style={{ width: 16, height: 16 }} />
                  <span>Computing Market Valuation...</span>
                </>
              ) : (
                <>
                  <span>💰</span>
                  <span>Estimate Property Value</span>
                </>
              )}
            </button>
          </form>
        </section>

        {/* Right: Valuation Results Area */}
        <section className={styles.resultsArea}>
          {!valuationData && !loading && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>💎</div>
              <h3 style={{ color: '#f1f5f9', fontWeight: 700, marginBottom: '0.5rem' }}>
                No Valuation Generated Yet
              </h3>
              <p style={{ maxWidth: '440px', margin: '0 auto', fontSize: '0.875rem' }}>
                Enter property parameters or choose a preset on the left to compute indicative
                market values, per sq.ft benchmark adjustments, expected rental income, and ROI.
              </p>
            </div>
          )}

          {valuationData && (
            <>
              {/* Hero Valuation Banner */}
              <div className={styles.heroValuationCard}>
                <div className={styles.heroLeft}>
                  <span className={styles.heroLabel}>Indicative Market Valuation</span>
                  <div className={styles.heroValue}>
                    {valuationData.formatted_total_value}
                  </div>
                  <div className={styles.heroRate}>
                    Estimated Rate: <span>₹{valuationData.estimated_rate_per_sqft.toLocaleString('en-IN')}/sq.ft</span>
                  </div>
                </div>

                <div className={styles.bandBox}>
                  <div className={styles.bandTitle}>Valuation Range Band</div>
                  <div className={styles.bandRange}>
                    ₹{(valuationData.valuation_band.low / 100000).toFixed(1)}L – ₹{(valuationData.valuation_band.high / 100000).toFixed(1)}L
                  </div>
                  <span className={styles.confidenceBadge}>
                    🎯 {valuationData.valuation_band.confidence_level} Confidence
                  </span>
                </div>
              </div>

              {/* Financial & ROI Metrics Row */}
              <div className={styles.metricsGrid}>
                <div className={styles.metricCard}>
                  <span className={styles.metricLabel}>Rental Potential</span>
                  <span className={styles.metricValue}>
                    {valuationData.rental_and_roi.formatted_monthly_rent}
                  </span>
                  <span className={styles.metricSub}>
                    ₹{(valuationData.rental_and_roi.estimated_annual_rent).toLocaleString('en-IN')}/year
                  </span>
                </div>

                <div className={styles.metricCard}>
                  <span className={styles.metricLabel}>Gross Rental Yield</span>
                  <span className={styles.metricValue}>
                    {valuationData.rental_and_roi.gross_rental_yield_percent}%
                  </span>
                  <span className={styles.metricSub}>
                    Net ROI: {valuationData.rental_and_roi.net_roi_percent}%
                  </span>
                </div>

                <div className={styles.metricCard}>
                  <span className={styles.metricLabel}>5-Year Projected Value</span>
                  <span className={styles.metricValue}>
                    {valuationData.rental_and_roi.formatted_5yr_value}
                  </span>
                  <span className={styles.metricSub}>
                    ~{valuationData.rental_and_roi.projected_cagr_percent}% Annual Appreciation
                  </span>
                </div>
              </div>

              {/* Itemized Adjustments Breakdown */}
              <div className={styles.factorsCard}>
                <div className={styles.factorsHeader}>
                  <h3>Itemized Rate Adjustments</h3>
                  <span>Parametric Indian Benchmark Model</span>
                </div>
                <table className={styles.factorsTable}>
                  <thead>
                    <tr>
                      <th>Factor</th>
                      <th>Rate Impact (₹/sq.ft)</th>
                      <th>Rationale</th>
                    </tr>
                  </thead>
                  <tbody>
                    {valuationData.factors_applied.map((f, idx) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: 600 }}>{f.factor}</td>
                        <td
                          className={
                            f.rate_adjustment >= 0
                              ? styles.positiveAdjustment
                              : styles.negativeAdjustment
                          }
                        >
                          {f.rate_adjustment >= 0 ? `+₹${f.rate_adjustment}` : `-₹${Math.abs(f.rate_adjustment)}`}
                        </td>
                        <td style={{ color: '#94a3b8' }}>{f.rationale}</td>
                      </tr>
                    ))}
                    <tr style={{ background: 'rgba(139, 92, 246, 0.08)', fontWeight: 700 }}>
                      <td style={{ color: '#c4b5fd' }}>Net Rate per Sq.Ft</td>
                      <td style={{ color: '#34d399', fontSize: '1rem' }}>
                        ₹{valuationData.estimated_rate_per_sqft.toLocaleString('en-IN')}
                      </td>
                      <td style={{ color: '#c4b5fd' }}>
                        Final calculated unit rate applied to {builtUpArea} sq.ft
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Legal / Inspection Disclaimer */}
              <div className={styles.disclaimerBox}>
                ℹ️ <strong>Notice & Limitations:</strong> {valuationData.assumptions_and_limitations} All estimates are indicative for preliminary investment screening only.
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}

export default function Valuation() {
  return (
    <ErrorBoundary>
      <ValuationInner />
    </ErrorBoundary>
  )
}
