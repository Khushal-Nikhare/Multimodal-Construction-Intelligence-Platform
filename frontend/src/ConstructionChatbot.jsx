import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, HelpCircle, AlertCircle, RefreshCw } from 'lucide-react'
import styles from './ConstructionChatbot.module.css'
import ErrorBoundary from './ErrorBoundary'
import { apiUrl } from './api'

const STARTER_QUERIES = [
  'Can I remove props from a 4m RCC slab after 5 days?',
  'What is the minimum curing period for OPC concrete under IS 456?',
  'What should we do if we hit groundwater at 2 meters during footing excavation?',
  'Concrete', // Ambiguity test
]

function ConstructionChatbotInner() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I am your Construction Intelligence Assistant. You can ask me technical questions regarding IS/CPWD codes, structural detailing, concrete curing, on-site problem solving, and safety protocols.',
      action_suggestions: [
        'What IS codes apply to concrete curing?',
        'How to handle deep footing water seepage?',
        'Formwork stripping schedules under IS 456',
      ],
    },
  ])
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(() => `sess-${Math.random().toString(36).substring(2, 9)}`)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSendMessage = async (textToSend) => {
    const messageText = (textToSend || query).trim()
    // Step 2: Empty or whitespace-only validation
    if (!messageText) return

    const userMessageId = `user-${Date.now()}`
    const newHistory = [...messages, { id: userMessageId, role: 'user', content: messageText }]

    // Step 3: Update local state immediately
    setMessages(newHistory)
    setQuery('')
    setLoading(true)

    try {
      // Step 4: Submit POST request to /api/chatbot via Axios
      const res = await axios.post(apiUrl('/api/chatbot'), {
        message: messageText,
        session_id: sessionId,
        history: newHistory
          .filter((m) => m.id !== 'welcome')
          .slice(-6)
          .map((m) => ({ role: m.role, content: m.content })),
      }, { timeout: 120_000 })

      // Step 6: Extract reply and optional action_suggestions (defaulting to empty array)
      const reply = res.data?.reply || 'Received response, but no answer was provided.'
      const action_suggestions = Array.isArray(res.data?.action_suggestions)
        ? res.data.action_suggestions
        : []

      if (res.data?.session_id) {
        setSessionId(res.data.session_id)
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          role: 'assistant',
          content: reply,
          action_suggestions,
          requires_clarification: res.data?.requires_clarification || false,
          partial: res.data?.status === 'partial',
        },
      ])
    } catch (err) {
      console.error('Chatbot error:', err)
      // Step 8: Fallback message on failure
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content:
            '⚠️ An error occurred while communicating with the construction intelligence service. Please verify your connection or try rephrasing your question.',
          action_suggestions: ['Retry previous query', 'Check server health'],
        },
      ])
    } finally {
      // Step 7: Reset loading state in finally block
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    handleSendMessage()
  }

  const handleSelectSuggestion = (suggestion) => {
    handleSendMessage(suggestion)
  }

  return (
    <div className={styles.chatContainer}>
      {/* ── Header ── */}
      <header className={styles.headerSection}>
        <div className={styles.badge}>
          <Bot size={13} />
          <span>FR-06 • Construction Chatbot</span>
        </div>
        <h1 className={styles.title}>Civil Engineering On-Site Copilot</h1>
        <p className={styles.subtitle}>
          Context-aware multi-turn guidance for civil engineers, site managers, and contractors.
          Referencing IS 456, IS 800, CPWD norms, and OSHA site safety standards.
        </p>
      </header>

      {/* ── Chat Messages Container ── */}
      <div className={styles.chatWindow}>
        <div className={styles.messagesList}>
          {messages.length === 1 && (
            <div className={styles.emptyChatPrompt}>
              <div className={styles.emptyIcon}>🏗️</div>
              <h3 style={{ color: '#f1f5f9', fontWeight: 700, marginBottom: '0.4rem' }}>
                Ask a Technical Construction Question
              </h3>
              <p style={{ fontSize: '0.85rem' }}>
                Select a standard query or type your field issue below to get immediate engineering advice.
              </p>
              <div className={styles.starterGrid}>
                {STARTER_QUERIES.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className={styles.starterButton}
                    onClick={() => handleSelectSuggestion(q)}
                  >
                    <HelpCircle size={14} style={{ color: '#22d3ee', flexShrink: 0 }} />
                    <span>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {messages.map((msg) => {
              const isUser = msg.role === 'user'
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`${styles.messageRow} ${
                    isUser ? styles.messageRowUser : styles.messageRowAssistant
                  }`}
                >
                  {!isUser && (
                    <div className={`${styles.avatar} ${styles.assistantAvatar}`}>
                      <Bot size={18} />
                    </div>
                  )}

                  <div style={{ maxWidth: '85%' }}>
                    <div
                      className={`${styles.bubble} ${
                        isUser ? styles.bubbleUser : styles.bubbleAssistant
                      }`}
                    >
                      <div className={styles.bubbleMarkdown}>{msg.content}</div>
                    </div>

                    {msg.partial && (
                      <div
                        role="status"
                        style={{ color: '#fcd34d', fontSize: '0.75rem', marginTop: '0.35rem' }}
                      >
                        ⚠️ The assistant response could not be fully structured; verify critical guidance.
                      </div>
                    )}

                    {/* Action Suggestions Chips (Step 6 & 9) */}
                    {!isUser && msg.action_suggestions && msg.action_suggestions.length > 0 && (
                      <div className={styles.suggestionsContainer}>
                        {msg.action_suggestions.map((action, i) => (
                          <button
                            key={i}
                            type="button"
                            className={styles.suggestionChip}
                            onClick={() => handleSelectSuggestion(action)}
                          >
                            <Sparkles size={11} />
                            <span>{action}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className={`${styles.avatar} ${styles.userAvatar}`}>
                      <User size={18} />
                    </div>
                  )}
                </motion.div>
              )
            })}
          </AnimatePresence>

          {/* Loading Indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={`${styles.messageRow} ${styles.messageRowAssistant}`}
            >
              <div className={`${styles.avatar} ${styles.assistantAvatar}`}>
                <Bot size={18} />
              </div>
              <div className={`${styles.bubble} ${styles.bubbleAssistant}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8' }}>
                  <span className="spinner" style={{ width: 14, height: 14 }} />
                  <span>Synthesizing civil engineering advice...</span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ── Input Form ── */}
        <form onSubmit={handleSubmit} className={styles.inputArea}>
          <input
            id="chat-user-input"
            type="text"
            className={styles.chatInput}
            placeholder="Ask a question (e.g., curing duration, groundwater ingress, slab prop removal)..."
            value={query}
            disabled={loading}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            id="chat-send-btn"
            type="submit"
            disabled={loading || !query.trim()}
            className={styles.sendButton}
          >
            <Send size={15} />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}

export default function ConstructionChatbot() {
  return (
    <ErrorBoundary>
      <ConstructionChatbotInner />
    </ErrorBoundary>
  )
}
