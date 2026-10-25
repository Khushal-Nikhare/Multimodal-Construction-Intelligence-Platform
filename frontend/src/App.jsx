import { useState } from 'react'
import SafetyAnalyzer from './SafetyAnalyzer'
import CrackDetection from './CrackDetection'
import Valuation from './Valuation'
import ProjectPlanner from './ProjectPlanner'
import ConstructionChatbot from './ConstructionChatbot'
import DailySiteAssistant from './DailySiteAssistant'
import WeatherAdvisor from './WeatherAdvisor'
import './index.css'

const MODULES = [
  {
    id: 'safety',
    label: 'Safety Monitor',
    icon: '🦺',
    badge: 'FR-01',
    component: <SafetyAnalyzer />,
  },
  {
    id: 'cracks',
    label: 'Crack Detection',
    icon: '🏚️',
    badge: 'FR-02',
    component: <CrackDetection />,
  },
  {
    id: 'valuation',
    label: 'Valuation Engine',
    icon: '💎',
    badge: 'FR-03',
    component: <Valuation />,
  },
  {
    id: 'planning',
    label: 'Project Planner',
    icon: '📐',
    badge: 'FR-04',
    component: <ProjectPlanner />,
  },
  {
    id: 'chatbot',
    label: 'AI Chatbot',
    icon: '💬',
    badge: 'FR-06',
    component: <ConstructionChatbot />,
  },
  {
    id: 'site-assistant',
    label: 'Daily Site Assistant',
    icon: '📋',
    badge: 'FR-07',
    component: <DailySiteAssistant />,
  },
  {
    id: 'weather',
    label: 'Weather Advisory',
    icon: '🌦️',
    badge: 'FR-08',
    component: <WeatherAdvisor />,
  },
]

export default function App() {
  const [activeId, setActiveId] = useState('safety')

  const active = MODULES.find((m) => m.id === activeId)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--clr-bg)' }}>
      {/* ── Top navigation bar ── */}
      <nav
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          background: 'rgba(11 15 26 / 0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid var(--clr-border)',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          height: '56px',
        }}
      >
        {/* Brand */}
        <span
          style={{
            fontWeight: 800,
            fontSize: '0.9375rem',
            letterSpacing: '-0.01em',
            color: 'var(--clr-text)',
            marginRight: '16px',
            whiteSpace: 'nowrap',
          }}
        >
          🏗️ Construction AI
        </span>

        {/* Module tabs */}
        {MODULES.map((mod) => {
          const isActive = mod.id === activeId
          return (
            <button
              key={mod.id}
              id={`tab-${mod.id}`}
              onClick={() => setActiveId(mod.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: 'var(--radius-md)',
                border: isActive
                  ? '1px solid var(--clr-border-hover)'
                  : '1px solid transparent',
                background: isActive ? 'var(--clr-surface-2)' : 'transparent',
                color: isActive ? 'var(--clr-text)' : 'var(--clr-text-muted)',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.8rem',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--clr-text)'
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--clr-text-muted)'
              }}
              aria-selected={isActive}
              role="tab"
            >
              <span>{mod.icon}</span>
              <span>{mod.label}</span>
              <span
                style={{
                  fontSize: '0.65rem',
                  padding: '1px 6px',
                  borderRadius: '999px',
                  background: isActive
                    ? 'var(--clr-primary-glow)'
                    : 'var(--clr-surface-3)',
                  color: isActive ? 'var(--clr-primary)' : 'var(--clr-text-dim)',
                  border: isActive ? '1px solid var(--clr-primary)' : '1px solid transparent',
                  fontWeight: 700,
                  letterSpacing: '0.04em',
                }}
              >
                {mod.badge}
              </span>
            </button>
          )
        })}
      </nav>

      {/* ── Active module ── */}
      <main role="tabpanel" aria-label={active?.label}>
        {active?.component}
      </main>
    </div>
  )
}
