import { useState } from 'react'
import styles from './ProjectPlanner.module.css'
import ErrorBoundary from './ErrorBoundary'

const CONSTRUCTION_GRADES = [
  { value: 'standard_residential', label: 'Standard Residential (RCC)' },
  { value: 'premium_residential', label: 'Premium Residential (High-End)' },
  { value: 'commercial_rcc', label: 'Commercial RCC Frame' },
  { value: 'steel_structure', label: 'Pre-Engineered / Steel' },
]

const POPULAR_CITIES = [
  'Bengaluru',
  'Delhi',
  'Mumbai',
  'Hyderabad',
  'Chennai',
  'Pune',
  'Kolkata',
  'Ahmedabad',
  'Jaipur',
  'Lucknow',
]

const PRESETS = [
  { label: '2BHK Duplex (2,400 sq.ft, 2 Fl)', area: 2400, floors: 2, grade: 'standard_residential', city: 'Bengaluru' },
  { label: 'Villa (4,000 sq.ft, 3 Fl)', area: 4000, floors: 3, grade: 'premium_residential', city: 'Delhi' },
  { label: 'Commercial Office (8,500 sq.ft, 4 Fl)', area: 8500, floors: 4, grade: 'commercial_rcc', city: 'Mumbai' },
  { label: 'Unrealistic Density (500 sq.ft, 50 Fl)', area: 500, floors: 50, grade: 'standard_residential', city: 'Mumbai' },
]

function ProjectPlannerInner() {
  const [area, setArea] = useState(3000)
  const [floors, setFloors] = useState(2)
  const [grade, setGrade] = useState('standard_residential')
  const [city, setCity] = useState('Bengaluru')
  const [contingency, setContingency] = useState(7.5)
  const [projectTitle, setProjectTitle] = useState('')
  const [description, setDescription] = useState('')

  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [planResult, setPlanResult] = useState(null)
  const [activeTab, setActiveTab] = useState('summary') // 'summary' | 'materials' | 'cost' | 'schedule' | 'viz'

  const handleApplyPreset = (p) => {
    setArea(p.area)
    setFloors(p.floors)
    setGrade(p.grade)
    setCity(p.city)
    setErrorMsg(null)
  }

  const handleGeneratePlan = async (e) => {
    e.preventDefault()
    if (!area || area <= 0) {
      setErrorMsg('Please specify a valid built-up area greater than 0.')
      return
    }
    if (!floors || floors < 1) {
      setErrorMsg('Please specify at least 1 floor.')
      return
    }

    setLoading(true)
    setErrorMsg(null)

    try {
      const response = await fetch('/api/planning/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          built_up_area_sqft: parseFloat(area),
          floors: parseInt(floors, 10),
          construction_grade: grade,
          city,
          contingency_percent: parseFloat(contingency),
          project_title: projectTitle.trim() || undefined,
          description: description.trim() || undefined,
        }),
      })

      const result = await response.json()
      if (!response.ok || result.status !== 'success') {
        throw new Error(result.error?.message || 'Failed to generate construction plan')
      }

      setPlanResult(result.data)
      setActiveTab('summary')
    } catch (err) {
      console.error('Plan generation error:', err)
      setErrorMsg(err.message || 'Error communicating with planning service')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.plannerContainer}>
      {/* ── Header ── */}
      <header className={styles.headerSection}>
        <div className={styles.badge}>
          <span>📐</span>
          <span>FR-04 • Unified Project Planning</span>
        </div>
        <h1 className={styles.title}>Construction Planning & Quantity Estimation</h1>
        <p className={styles.subtitle}>
          Generate instant parametric material takeoffs (MTO), cost breakdowns in Indian Rupees (₹),
          sequenced WBS task schedules, and conceptual architectural visualization.
        </p>
      </header>

      {/* ── Main Layout ── */}
      <div className={styles.mainLayout}>
        {/* Left: Input Panel */}
        <section className={styles.inputCard}>
          <h2 className={styles.cardTitle}>
            <span>📋</span>
            <span>Project Parameters</span>
          </h2>

          <div style={{ marginBottom: '1rem' }}>
            <span className={styles.formLabel}>Quick Presets</span>
            <div className={styles.presetButtons}>
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  id={`preset-btn-${idx}`}
                  className={styles.presetBtn}
                  onClick={() => handleApplyPreset(p)}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleGeneratePlan}>
            <div className={styles.formGroup}>
              <label htmlFor="input-project-title" className={styles.formLabel}>
                Project Title (Optional)
              </label>
              <input
                id="input-project-title"
                type="text"
                className={styles.formInput}
                placeholder="e.g. Green Valley Duplex Residence"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
              />
            </div>

            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="input-built-area" className={styles.formLabel}>
                  Built-Up Area (sq.ft) *
                </label>
                <input
                  id="input-built-area"
                  type="number"
                  min="50"
                  step="50"
                  required
                  className={styles.formInput}
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="input-floors" className={styles.formLabel}>
                  Floors (Stories) *
                </label>
                <input
                  id="input-floors"
                  type="number"
                  min="1"
                  max="120"
                  required
                  className={styles.formInput}
                  value={floors}
                  onChange={(e) => setFloors(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label htmlFor="select-city" className={styles.formLabel}>
                  City / Location
                </label>
                <select
                  id="select-city"
                  className={styles.formSelect}
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                >
                  {POPULAR_CITIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="input-contingency" className={styles.formLabel}>
                  Contingency Buffer (%)
                </label>
                <input
                  id="input-contingency"
                  type="number"
                  min="0"
                  max="30"
                  step="0.5"
                  className={styles.formInput}
                  value={contingency}
                  onChange={(e) => setContingency(e.target.value)}
                />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="select-grade" className={styles.formLabel}>
                Construction Grade / Type
              </label>
              <select
                id="select-grade"
                className={styles.formSelect}
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
              >
                {CONSTRUCTION_GRADES.map((g) => (
                  <option key={g.value} value={g.value}>
                    {g.label}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="input-description" className={styles.formLabel}>
                Project Notes / Context
              </label>
              <textarea
                id="input-description"
                rows="2"
                className={styles.formTextarea}
                placeholder="e.g. Clay soil, solar terrace provision, boundary wall included..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {errorMsg && (
              <div style={{ color: '#f87171', fontSize: '0.8125rem', marginTop: '0.5rem' }}>
                ⚠️ {errorMsg}
              </div>
            )}

            <button
              id="btn-generate-plan"
              type="submit"
              disabled={loading}
              className={styles.submitBtn}
            >
              {loading ? (
                <>
                  <span className="spinner" style={{ width: 16, height: 16 }} />
                  <span>Computing Plan & Estimations...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Generate Construction Plan</span>
                </>
              )}
            </button>
          </form>
        </section>

        {/* Right: Results Display */}
        <section className={styles.resultsArea}>
          {!planResult && !loading && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>📐</div>
              <h3 style={{ color: '#f1f5f9', fontWeight: 700, marginBottom: '0.5rem' }}>
                No Plan Generated Yet
              </h3>
              <p style={{ maxWidth: '440px', margin: '0 auto', fontSize: '0.875rem' }}>
                Enter your site area, floors, and location on the left or select a preset to generate
                materials takeoff, cost forecast, schedule milestones, and architectural visualization.
              </p>
            </div>
          )}

          {planResult && (
            <>
              {/* Feasibility Alert if triggered */}
              {planResult.feasibility_warning && (
                <div className={styles.advisoryWarning} role="alert">
                  <span style={{ fontSize: '1.25rem' }}>⚠️</span>
                  <div>
                    <strong>Structural Feasibility Advisory</strong>
                    <div>{planResult.feasibility_warning}</div>
                  </div>
                </div>
              )}

              {/* Summary KPIs */}
              <div className={styles.summaryRow}>
                <div className={styles.summaryCard}>
                  <span className={styles.summaryLabel}>Total Estimated Cost</span>
                  <span className={styles.summaryValue}>
                    ₹{(planResult.cost.total_estimated_cost).toLocaleString('en-IN')}
                  </span>
                  <span className={styles.summaryMeta}>
                    ₹{planResult.cost.estimated_cost_per_sqft}/sq.ft ({planResult.cost.city})
                  </span>
                </div>

                <div className={styles.summaryCard}>
                  <span className={styles.summaryLabel}>Estimated Duration</span>
                  <span className={styles.summaryValue}>
                    {planResult.schedule.estimated_total_duration_days} Days
                  </span>
                  <span className={styles.summaryMeta}>
                    ~{Math.round(planResult.schedule.estimated_total_duration_days / 30)} Months • {planResult.schedule.phases.length} Phases
                  </span>
                </div>

                <div className={styles.summaryCard}>
                  <span className={styles.summaryLabel}>Built-up Specification</span>
                  <span className={styles.summaryValue}>
                    {planResult.parameters.built_up_area_sqft.toLocaleString()} sq.ft
                  </span>
                  <span className={styles.summaryMeta}>
                    {planResult.parameters.floors} Floor{planResult.parameters.floors > 1 ? 's' : ''} • {planResult.cost.contingency_percent}% buffer
                  </span>
                </div>
              </div>

              {/* View Tabs */}
              <div className={styles.tabNav} role="tablist">
                <button
                  role="tab"
                  aria-selected={activeTab === 'summary'}
                  className={`${styles.tabBtn} ${activeTab === 'summary' ? styles.tabBtnActive : ''}`}
                  onClick={() => setActiveTab('summary')}
                >
                  📊 Consolidated Summary
                </button>
                <button
                  role="tab"
                  aria-selected={activeTab === 'materials'}
                  className={`${styles.tabBtn} ${activeTab === 'materials' ? styles.tabBtnActive : ''}`}
                  onClick={() => setActiveTab('materials')}
                >
                  🧱 Material Takeoff ({planResult.materials.length})
                </button>
                <button
                  role="tab"
                  aria-selected={activeTab === 'cost'}
                  className={`${styles.tabBtn} ${activeTab === 'cost' ? styles.tabBtnActive : ''}`}
                  onClick={() => setActiveTab('cost')}
                >
                  💰 Cost Breakdown
                </button>
                <button
                  role="tab"
                  aria-selected={activeTab === 'schedule'}
                  className={`${styles.tabBtn} ${activeTab === 'schedule' ? styles.tabBtnActive : ''}`}
                  onClick={() => setActiveTab('schedule')}
                >
                  📅 Task WBS Schedule
                </button>
                <button
                  role="tab"
                  aria-selected={activeTab === 'viz'}
                  className={`${styles.tabBtn} ${activeTab === 'viz' ? styles.tabBtnActive : ''}`}
                  onClick={() => setActiveTab('viz')}
                >
                  🏛️ Conceptual Visualization
                </button>
              </div>

              {/* TAB 1: SUMMARY */}
              {activeTab === 'summary' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  <div className={styles.tableCard}>
                    <div className={styles.tableHeader}>
                      <h3>{planResult.project_title}</h3>
                      <span>{planResult.cost.city}</span>
                    </div>
                    <table className={styles.planTable}>
                      <thead>
                        <tr>
                          <th>Expense Category</th>
                          <th>Allocation Share</th>
                          <th>Estimated Amount (₹)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td><strong>Materials (Cement, Steel, Aggregates, Masonry)</strong></td>
                          <td>~60%</td>
                          <td>₹{planResult.cost.materials_cost.toLocaleString('en-IN')}</td>
                        </tr>
                        <tr>
                          <td><strong>Direct & Subcontracted Labor</strong></td>
                          <td>~28%</td>
                          <td>₹{planResult.cost.labor_cost.toLocaleString('en-IN')}</td>
                        </tr>
                        <tr>
                          <td><strong>Plant & Equipment Rentals / Formwork</strong></td>
                          <td>~12%</td>
                          <td>₹{planResult.cost.equipment_cost.toLocaleString('en-IN')}</td>
                        </tr>
                        <tr style={{ background: 'rgba(255, 255, 255, 0.03)' }}>
                          <td><strong>Subtotal</strong></td>
                          <td>100%</td>
                          <td>₹{planResult.cost.subtotal.toLocaleString('en-IN')}</td>
                        </tr>
                        <tr>
                          <td>Contingency Buffer ({planResult.cost.contingency_percent}%)</td>
                          <td>Buffer</td>
                          <td>₹{planResult.cost.contingency_cost.toLocaleString('en-IN')}</td>
                        </tr>
                        <tr style={{ background: 'rgba(16, 185, 129, 0.08)', fontWeight: 700 }}>
                          <td style={{ color: '#34d399' }}>Total Estimated Project Cost</td>
                          <td style={{ color: '#34d399' }}>Gross Total</td>
                          <td style={{ color: '#34d399', fontSize: '1.05rem' }}>
                            ₹{planResult.cost.total_estimated_cost.toLocaleString('en-IN')}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div className={styles.disclaimerNotice}>
                    ℹ️ <strong>Standard Reference:</strong> {planResult.disclaimer}
                  </div>
                </div>
              )}

              {/* TAB 2: MATERIALS */}
              {activeTab === 'materials' && (
                <div className={styles.tableCard}>
                  <div className={styles.tableHeader}>
                    <h3>Parametric Material Takeoff (MTO)</h3>
                    <span>IS 456 / CPWD Norms</span>
                  </div>
                  <table className={styles.planTable}>
                    <thead>
                      <tr>
                        <th>Material Item</th>
                        <th>Estimated Quantity</th>
                        <th>Unit</th>
                        <th>Standard Coefficient</th>
                      </tr>
                    </thead>
                    <tbody>
                      {planResult.materials.map((m, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{m.item}</td>
                          <td style={{ color: '#34d399', fontWeight: 700 }}>
                            {m.quantity.toLocaleString()}
                          </td>
                          <td style={{ color: '#94a3b8' }}>{m.unit}</td>
                          <td style={{ color: '#94a3b8' }}>{m.coefficient_per_sqft} / sq.ft</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* TAB 3: COST */}
              {activeTab === 'cost' && (
                <div className={styles.tableCard}>
                  <div className={styles.tableHeader}>
                    <h3>Detailed Cost Allocation Breakdown</h3>
                    <span>Location: {planResult.cost.city}</span>
                  </div>
                  <table className={styles.planTable}>
                    <thead>
                      <tr>
                        <th>Item Description</th>
                        <th>Calculation Basis</th>
                        <th>Amount (INR ₹)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Materials Expenditure</td>
                        <td>Procurement of cement, steel, sand, coarse aggregate, masonry blocks</td>
                        <td>₹{planResult.cost.materials_cost.toLocaleString('en-IN')}</td>
                      </tr>
                      <tr>
                        <td>Skilled & Unskilled Labor</td>
                        <td>Bar benders, masons, carpenters, helpers, site supervisors</td>
                        <td>₹{planResult.cost.labor_cost.toLocaleString('en-IN')}</td>
                      </tr>
                      <tr>
                        <td>Machinery & Scaffolding Equipment</td>
                        <td>Concrete mixers, vibrators, hoist, scaffolding staging rentals</td>
                        <td>₹{planResult.cost.equipment_cost.toLocaleString('en-IN')}</td>
                      </tr>
                      <tr>
                        <td>Contingency Allocation</td>
                        <td>{planResult.cost.contingency_percent}% variance allowance for price escalations & weather</td>
                        <td>₹{planResult.cost.contingency_cost.toLocaleString('en-IN')}</td>
                      </tr>
                      <tr style={{ background: 'rgba(16, 185, 129, 0.08)' }}>
                        <td style={{ fontWeight: 800, color: '#34d399' }}>Total Projected Cost</td>
                        <td style={{ fontWeight: 600, color: '#34d399' }}>All inclusive baseline estimate</td>
                        <td style={{ fontWeight: 800, color: '#34d399', fontSize: '1.1rem' }}>
                          ₹{planResult.cost.total_estimated_cost.toLocaleString('en-IN')}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

              {/* TAB 4: SCHEDULE */}
              {activeTab === 'schedule' && (
                <div className={styles.tableCard}>
                  <div className={styles.tableHeader}>
                    <h3>Execution WBS Schedule & Milestones</h3>
                    <span>Total Duration: {planResult.schedule.estimated_total_duration_days} Days</span>
                  </div>
                  <div className={styles.timelineList}>
                    {planResult.schedule.phases.map((ph) => (
                      <div key={ph.task_id} className={styles.phaseItem}>
                        <span className={styles.phaseBadge}>{ph.task_id}</span>
                        <div className={styles.phaseName}>
                          <div>{ph.name}</div>
                          {ph.dependencies.length > 0 && (
                            <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>
                              Preceded by: {ph.dependencies.join(', ')}
                            </div>
                          )}
                        </div>
                        {ph.milestone && (
                          <span className={styles.milestonePill}>⭐ Milestone</span>
                        )}
                        <span className={styles.phaseDuration}>{ph.duration_days} Days</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 5: VISUALIZATION */}
              {activeTab === 'viz' && (
                <div className={styles.vizCard}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>
                    Conceptual Architectural Blueprint & Visualization
                  </h3>
                  <div className={styles.blueprintFrame}>
                    <div className={styles.blueprintGraphic}>🏛️</div>
                    <div className={styles.blueprintTitle}>
                      {planResult.parameters.floors}-Storey {planResult.parameters.construction_grade.replace('_', ' ')} Concept
                    </div>
                    <div className={styles.blueprintDetails}>
                      Footprint: ~{Math.round(planResult.parameters.built_up_area_sqft / planResult.parameters.floors)} sq.ft/floor • Grid Framing RCC • Location: {planResult.cost.city}
                    </div>
                  </div>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--clr-text-muted)', lineHeight: 1.5 }}>
                    Conceptual preview synthesized based on project footprint ({planResult.parameters.built_up_area_sqft} sq.ft across {planResult.parameters.floors} floors) and regional structural typology. Formal structural engineering layouts must be validated against CAD/BIM models.
                  </p>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  )
}

export default function ProjectPlanner() {
  return (
    <ErrorBoundary>
      <ProjectPlannerInner />
    </ErrorBoundary>
  )
}
