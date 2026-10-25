import { useState } from 'react'
import axios from 'axios'
import styles from './DailySiteAssistant.module.css'
import ErrorBoundary from './ErrorBoundary'

const ACTIVITIES = ['Concreting', 'Masonry', 'Excavation', 'Reinforcement', 'Formwork', 'Plastering', 'Waterproofing']
const CONDITIONS = ['Normal', 'Rainy', 'Hot', 'Windy', 'Restricted Access', 'Unsafe']

function DailySiteAssistantInner() {
  const [activity, setActivity] = useState('Concreting')
  const [labourCount, setLabourCount] = useState(10)
  const [siteCondition, setSiteCondition] = useState('Normal')
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    const parsedLabourCount = Number.parseInt(labourCount, 10)
    if (!Number.isInteger(parsedLabourCount) || parsedLabourCount < 1) {
      setError('Enter a workforce count of at least 1.')
      return
    }

    setLoading(true)
    setError('')
    setPlan(null)
    try {
      const response = await axios.post('/api/site-assistant', {
        activity,
        labour_count: parsedLabourCount,
        site_condition: siteCondition,
      }, { timeout: 120_000 })
      const body = response.data
      if (!body?.data || !['success', 'partial'].includes(body.status)) {
        throw new Error(body?.error?.message || 'Unable to generate the daily site plan.')
      }
      setPlan({ ...body.data, partial: body.status === 'partial' })
    } catch (requestError) {
      const detail = requestError.response?.data?.detail?.error?.message || requestError.response?.data?.error?.message
      setError(detail || requestError.message || 'Unable to reach the daily site assistant.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <span className={styles.badge}>FR-07</span>
        <h1>Daily Site Assistant</h1>
        <p>Turn the day’s activity, crew availability, and site condition into a structured coordination plan.</p>
      </header>

      <div className={styles.layout}>
        <form className={styles.card} onSubmit={handleSubmit}>
          <h2>Site Inputs</h2>
          <label htmlFor="site-activity">Construction activity</label>
          <select id="site-activity" value={activity} onChange={(event) => setActivity(event.target.value)}>
            {ACTIVITIES.map((option) => <option key={option}>{option}</option>)}
          </select>

          <label htmlFor="site-labour">Available workforce</label>
          <input id="site-labour" type="number" min="1" max="10000" value={labourCount} onChange={(event) => setLabourCount(event.target.value)} />

          <label htmlFor="site-condition">Current site condition</label>
          <select id="site-condition" value={siteCondition} onChange={(event) => setSiteCondition(event.target.value)}>
            {CONDITIONS.map((option) => <option key={option}>{option}</option>)}
          </select>

          {error && <p className={styles.error} role="alert">⚠️ {error}</p>}
          <button type="submit" disabled={loading}>{loading ? 'Generating plan…' : 'Generate daily plan'}</button>
          <p className={styles.note}>AI coordination support only. Follow approved method statements and the site engineer’s directions.</p>
        </form>

        <section className={styles.results} aria-live="polite">
          {!plan && !loading && <div className={styles.empty}>Choose an activity and generate a daily plan.</div>}
          {loading && <div className={styles.empty}>Synthesizing work priorities, controls, and site checks…</div>}
          {plan && <>
            {plan.partial && <p className={styles.partial}>⚠️ A safe fallback plan is shown because the AI response was not fully structured. Verify all critical decisions.</p>}
            <div className={styles.summary}>
              <span>{plan.activity}</span><strong>{plan.labour_count} workers · {plan.site_condition}</strong>
              <p>{plan.progress_summary}</p>
            </div>
            <PlanSection title="Execution priorities">
              {plan.task_breakdown.map((task, index) => <li key={`${task.task}-${index}`}><strong>{task.priority}: {task.task}</strong><br />Crew: {task.suggested_crew} · {task.execution_notes}</li>)}
            </PlanSection>
            <PlanSection title="Materials, equipment & PPE">
              {plan.required_materials_and_equipment.map((item, index) => <li key={`${item.item}-${index}`}><strong>{item.item}</strong> <em>({item.category})</em> — {item.purpose}</li>)}
            </PlanSection>
            <div className={styles.twoColumns}>
              <PlanSection title="Safety precautions">{plan.safety_precautions.map((item, index) => <li key={index}>{item}</li>)}</PlanSection>
              <PlanSection title="Inspection checklist">{plan.inspection_checklist.map((item, index) => <li key={index}>{item}</li>)}</PlanSection>
            </div>
            <PlanSection title="Operational risks">{plan.operational_risks.length ? plan.operational_risks.map((item, index) => <li key={index}>{item}</li>) : <li>No specific condition-driven risks were identified.</li>}</PlanSection>
            <PlanSection title="Recommended actions">{plan.recommended_actions.map((item, index) => <li key={index}>{item}</li>)}</PlanSection>
            <p className={styles.note}>{plan.disclaimer}</p>
          </>}
        </section>
      </div>
    </div>
  )
}

function PlanSection({ title, children }) {
  return <section className={styles.section}><h2>{title}</h2><ul>{children}</ul></section>
}

export default function DailySiteAssistant() {
  return <ErrorBoundary><DailySiteAssistantInner /></ErrorBoundary>
}
