import { useState } from 'react'
import axios from 'axios'
import styles from './WeatherAdvisor.module.css'
import ErrorBoundary from './ErrorBoundary'

const ACTIVITIES = ['Slab Concreting', 'Excavation', 'Crane Lifting', 'Scaffolding', 'Masonry', 'Roofing', 'Waterproofing', 'Painting']
const RECOMMENDATION_STYLE = {
  SAFE_TO_PROCEED: styles.go,
  PROCEED_WITH_PRECAUTIONS: styles.caution,
  SUSPEND_ACTIVITY: styles.noGo,
}

function WeatherAdvisorInner() {
  const [city, setCity] = useState('Bengaluru')
  const [activity, setActivity] = useState('Slab Concreting')
  const [advisory, setAdvisory] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!city.trim()) {
      setError('Enter a city so current weather can be verified.')
      return
    }
    setLoading(true)
    setError('')
    setAdvisory(null)
    try {
      const response = await axios.get('/api/weather/advisory', { params: { city: city.trim(), activity }, timeout: 20_000 })
      if (response.data?.status !== 'success' || !response.data?.data) {
        throw new Error(response.data?.error?.message || 'Weather advisory could not be generated.')
      }
      setAdvisory(response.data.data)
    } catch (requestError) {
      const detail = requestError.response?.data?.detail?.error?.message || requestError.response?.data?.error?.message
      setError(detail || requestError.message || 'Current weather could not be retrieved. No recommendation was generated.')
    } finally {
      setLoading(false)
    }
  }

  return <div className={styles.page}>
    <header className={styles.header}>
      <span className={styles.badge}>FR-08</span>
      <h1>Weather-Aware Construction Advisory</h1>
      <p>Uses current Open-Meteo observations and a near-term precipitation forecast for transparent, activity-specific site advice.</p>
    </header>
    <div className={styles.layout}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h2>Planned work</h2>
        <label htmlFor="weather-city">City</label>
        <input id="weather-city" value={city} onChange={(event) => setCity(event.target.value)} placeholder="e.g. Bengaluru" maxLength="120" />
        <label htmlFor="weather-activity">Construction activity</label>
        <select id="weather-activity" value={activity} onChange={(event) => setActivity(event.target.value)}>
          {ACTIVITIES.map((option) => <option key={option}>{option}</option>)}
        </select>
        {error && <p className={styles.error} role="alert">⚠️ {error}</p>}
        <button type="submit" disabled={loading}>{loading ? 'Checking verified weather…' : 'Check weather advisory'}</button>
        <p className={styles.note}>If current data is unavailable, no GO / NO-GO recommendation is shown.</p>
      </form>
      <section className={styles.results} aria-live="polite">
        {!advisory && !loading && <div className={styles.empty}>Select the planned work and check current conditions.</div>}
        {loading && <div className={styles.empty}>Retrieving current weather and assessing construction thresholds…</div>}
        {advisory && <>
          <div className={`${styles.decision} ${RECOMMENDATION_STYLE[advisory.recommendation] || styles.caution}`}>
            <span>Recommendation</span><strong>{advisory.recommendation.replaceAll('_', ' ')}</strong><p>{advisory.recommendation_reason}</p>
          </div>
          <div className={styles.weatherGrid}>
            <Metric label="Temperature" value={`${advisory.weather.temperature_c} °C`} />
            <Metric label="Wind" value={`${advisory.weather.wind_speed_kmh} km/h`} />
            <Metric label="Rain now" value={`${advisory.weather.precipitation_mm} mm`} />
            <Metric label="Rain probability" value={`${advisory.weather.precipitation_probability_percent}%`} />
          </div>
          <p className={styles.observation}>Observed {advisory.weather.observed_at} · {advisory.weather.city} · Source: {advisory.weather.source}</p>
          <AdviceList title="Weather-related risks" items={advisory.weather_related_risks} empty="No configured activity-specific weather risk is currently triggered." />
          <AdviceList title="Safety precautions" items={advisory.safety_precautions} />
          <AdviceList title="Mitigation steps" items={advisory.mitigation_steps} />
          <p className={styles.note}>{advisory.data_freshness_note} {advisory.disclaimer}</p>
        </>}
      </section>
    </div>
  </div>
}

function Metric({ label, value }) { return <div className={styles.metric}><span>{label}</span><strong>{value}</strong></div> }
function AdviceList({ title, items, empty }) { return <section className={styles.section}><h2>{title}</h2><ul>{items.length ? items.map((item, index) => <li key={index}>{item}</li>) : <li>{empty}</li>}</ul></section> }
export default function WeatherAdvisor() { return <ErrorBoundary><WeatherAdvisorInner /></ErrorBoundary> }
