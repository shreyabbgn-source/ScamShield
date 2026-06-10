import { useState } from 'react'
import axios from 'axios'
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'

const API = 'http://127.0.0.1:8000/api'

const RISK_CONFIG = {
  LOW:      { color: '#22c55e', bg: '#052e16', label: 'SAFE',      emoji: '✅' },
  MEDIUM:   { color: '#3b82f6', bg: '#2d1f00', label: 'PROMOTIONAL',   emoji: '⚠️' },
  HIGH:     { color: '#f59e0b', bg: '#2d0a0a', label: 'SUSPICIOUS',     emoji: '🚨' },
  CRITICAL: { color: '#ef4444', bg: '#1f0000', label: 'SCAM', emoji: '☠️' },
}

const RECOMMENDED_ACTIONS = {
  banking_scam: [
    'Do not click any links in the message',
    'Verify directly through the official bank app',
    'Call the bank\'s official helpline number',
    'Report the sender to your bank and CERT-In',
    'Delete the message immediately',
  ],
  investment_scam: [
    'Do not send any money or share bank details',
    'Verify the company on SEBI/RBI official website',
    'Report to the National Cyber Crime portal (cybercrime.gov.in)',
    'Warn your contacts — these spread via referral',
    'Block and report the sender',
  ],
  phishing_scam: [
    'Do not enter credentials on this link',
    'Report the URL to Google Safe Browsing',
    'Change passwords if you already clicked',
    'Enable 2FA on all accounts immediately',
    'Report to CERT-In at incident@cert-in.org.in',
  ],
  job_scam: [
    'Never pay a registration or training fee',
    'Verify the company on LinkedIn and official website',
    'Report to the National Cyber Crime portal',
    'Do not share your Aadhaar or bank details',
    'Block and report the contact',
  ],
  lottery_scam: [
    'You cannot win a lottery you did not enter',
    'Do not pay any "processing fee" to claim prizes',
    'Report to cybercrime.gov.in',
    'Block and delete the message immediately',
  ],
  task_scam: [
    'Legitimate jobs never require advance deposits',
    'Do not pay any registration or unlock fees',
    'Report the Telegram/WhatsApp group to authorities',
    'Report to cybercrime.gov.in',
  ],
  unknown: [
    'Exercise caution with this content',
    'Do not share personal or financial information',
    'Verify through official channels before acting',
    'Report if you believe this is fraudulent',
  ],
}

function getActions(category) {
  const key = Object.keys(RECOMMENDED_ACTIONS).find(k => category?.includes(k))
  return RECOMMENDED_ACTIONS[key] || RECOMMENDED_ACTIONS.unknown
}

const LAYER_COLORS = {
  Pattern:     '#6366f1',
  'ML Model':  '#8b5cf6',
  BERT:        '#ec4899',
  Transformer: '#06b6d4',
}

const CATEGORY_COLORS = {
  investment: '#f59e0b',
  betting:    '#ef4444',
  customer_care: '#8b5cf6',
  job:        '#06b6d4',
  phishing:   '#ec4899',
  lottery:    '#22c55e',
  task:       '#f97316',
  mlm:        '#a78bfa',
  banking:    '#60a5fa',
  crypto:     '#34d399',
  loan:       '#fb7185',
  reward:     '#fbbf24',
}

function parseLayerScores(explanation) {
  const scores = {}
  const match = explanation?.match(/Pattern:\s*(\d+)%.*ML:\s*(\d+)%.*BERT:\s*(\d+)%.*Transformer:\s*(\d+)%/)
  if (match) {
    scores['Pattern']     = parseInt(match[1])
    scores['ML Model']    = parseInt(match[2])
    scores['BERT']        = parseInt(match[3])
    scores['Transformer'] = parseInt(match[4])
  }
  return scores
}

function FeedbackRow({ result, file, caption }) {
  const [feedback, setFeedback] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [comment, setComment] = useState('')
  const [showComment, setShowComment] = useState(false)

  async function submitFeedback(type) {
    setFeedback(type)
    if (type === 'incorrect') { setShowComment(true); return }
    await sendFeedback(type, '')
  }

  async function confirmFeedback() { await sendFeedback(feedback, comment) }

  async function sendFeedback(type, note) {
    try {
      await axios.post(`${API}/feedback`, {
        feedback: type, comment: note,
        predicted_risk: result.risk,
        predicted_category: result.category,
        scam_probability: result.scam_probability,
        caption: caption || '',
        ocr_text: result.ocr_text || '',
      })
    } catch {}
    setSubmitted(true)
    setShowComment(false)
  }

  if (submitted) return (
    <div style={{ background: '#12121e', borderRadius: 14, border: '1px solid #2a2a3e', padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 10 }}>
      <span style={{ fontSize: 18 }}>🙏</span>
      <p style={{ fontSize: 13, color: '#a0a0c0', margin: 0 }}>Thanks for your feedback — it helps improve ScamShield AI.</p>
    </div>
  )

  return (
    <div style={{ background: '#12121e', borderRadius: 14, border: '1px solid #2a2a3e', padding: '16px 20px' }}>
      <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>
        💬 Was this result correct?
      </p>
      {!showComment ? (
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={() => submitFeedback('correct')} style={{ flex: 1, padding: '10px 16px', borderRadius: 8, background: feedback === 'correct' ? '#22c55e20' : '#1e1e30', border: `1px solid ${feedback === 'correct' ? '#22c55e' : '#3a3a50'}`, color: feedback === 'correct' ? '#22c55e' : '#a0a0c0', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
            👍 Yes, correct
          </button>
          <button onClick={() => submitFeedback('incorrect')} style={{ flex: 1, padding: '10px 16px', borderRadius: 8, background: feedback === 'incorrect' ? '#ef444420' : '#1e1e30', border: `1px solid ${feedback === 'incorrect' ? '#ef4444' : '#3a3a50'}`, color: feedback === 'incorrect' ? '#ef4444' : '#a0a0c0', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
            👎 No, wrong result
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <p style={{ fontSize: 12, color: '#6b7280', margin: 0 }}>What should the correct result be? (optional)</p>
          <textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="e.g. This is a legitimate ad, not a scam..." rows={2} style={{ width: '100%', background: '#0a0a14', border: '1px solid #3a3a50', borderRadius: 8, padding: '8px 12px', color: '#e0e0f0', fontSize: 12, resize: 'none', outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box' }} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={confirmFeedback} style={{ flex: 1, padding: '9px 16px', borderRadius: 8, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>Submit Feedback</button>
            <button onClick={() => { setShowComment(false); setFeedback(null) }} style={{ padding: '9px 16px', borderRadius: 8, background: '#1e1e30', border: '1px solid #3a3a50', color: '#a0a0c0', fontSize: 13, cursor: 'pointer' }}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [tab, setTab]           = useState('scan')
  const [caption, setCaption]   = useState('')
  const [file, setFile]         = useState(null)
  const [preview, setPreview]   = useState(null)
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [showOcr, setShowOcr]   = useState(false)
  const [stats, setStats]       = useState(null)
  const [statsLoading, setStatsLoading] = useState(false)

  function handleFile(e) {
    const f = e.target.files[0]
    if (!f) return
    setFile(f); setPreview(URL.createObjectURL(f)); setResult(null); setShowOcr(false)
  }

  async function handleScan() {
    if (!file && !caption.trim()) { setError('Please upload an image or enter a caption.'); return }
    setError(null); setLoading(true); setResult(null)
    try {
      const form = new FormData()
      if (file)    form.append('file', file)
      if (caption) form.append('caption', caption)
      const { data } = await axios.post(`${API}/scan`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(data)
    } catch { setError('Backend error. Make sure the server is running on port 8000.') }
    finally { setLoading(false) }
  }

  function handleReset() {
    setCaption(''); setFile(null); setPreview(null); setResult(null); setError(null); setShowOcr(false)
  }

  async function loadDashboard() {
    setTab('dashboard')
    setStatsLoading(true)
    try {
      const { data } = await axios.get(`${API}/stats`)
      setStats(data)
    } catch { setStats(null) }
    finally { setStatsLoading(false) }
  }

  const risk   = result ? RISK_CONFIG[result.risk] || RISK_CONFIG.MEDIUM : null
  const pct    = result ? Math.round(result.scam_probability * 100) : 0
  const layers = result ? parseLayerScores(result.explanation) : {}
  const actions = result ? getActions(result.category) : []

  return (
    <div style={{ minHeight: '100vh', background: '#0f0f13', fontFamily: 'Inter, -apple-system, sans-serif' }}>

      {/* HEADER */}
      <header style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', borderBottom: '1px solid #2a2a3e', padding: '18px 32px', display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 42, height: 42, borderRadius: 10, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>🛡️</div>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: '#fff', margin: 0 }}>ScamShield AI</h1>
          <p style={{ fontSize: 11, color: '#6b7280', margin: 0 }}>Multimodal scam detection · 4-layer ensemble</p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
          {/* Tab buttons */}
          <button onClick={() => setTab('scan')} style={{ padding: '7px 18px', borderRadius: 8, background: tab === 'scan' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : '#1e1e30', border: '1px solid #3a3a50', color: '#fff', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
            🔍 Scan
          </button>
          <button onClick={loadDashboard} style={{ padding: '7px 18px', borderRadius: 8, background: tab === 'dashboard' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : '#1e1e30', border: '1px solid #3a3a50', color: '#fff', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>
            📊 Intelligence
          </button>
          {/* Layer badges */}
          <div style={{ display: 'flex', gap: 6, marginLeft: 8 }}>
            {['Pattern', 'TF-IDF ML', 'DistilBERT', 'Transformer'].map(l => (
              <span key={l} style={{ padding: '3px 9px', borderRadius: 20, background: '#1e1e30', border: '1px solid #3a3a50', fontSize: 10, color: '#a0a0c0' }}>{l}</span>
            ))}
          </div>
        </div>
      </header>

      <main style={{ maxWidth: 960, margin: '0 auto', padding: '28px 16px' }}>

        {/* ── DASHBOARD TAB ── */}
        {tab === 'dashboard' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

            {statsLoading && (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: 40 }}>Loading intelligence data...</div>
            )}

            {!statsLoading && !stats && (
              <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #2a2a3e', padding: 40, textAlign: 'center' }}>
                <p style={{ color: '#6b7280', fontSize: 14 }}>No scan data yet. Run some scans first to see intelligence.</p>
              </div>
            )}

            {!statsLoading && stats && (
              <>
                {/* Summary cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
                  {[
                    { label: 'Total Scanned',   value: stats.total,   color: '#6366f1', emoji: '🔍' },
                    { label: 'Threats Flagged', value: stats.flagged, color: '#ef4444', emoji: '🚨' },
                    { label: 'Safe Content',    value: stats.safe,    color: '#22c55e', emoji: '✅' },
                    { label: 'Detection Rate',  value: `${stats.total ? Math.round(stats.flagged / stats.total * 100) : 0}%`, color: '#f59e0b', emoji: '📊' },
                  ].map(({ label, value, color, emoji }) => (
                    <div key={label} style={{ background: '#1a1a24', borderRadius: 14, border: `1px solid ${color}30`, padding: 20, textAlign: 'center' }}>
                      <div style={{ fontSize: 22, marginBottom: 6 }}>{emoji}</div>
                      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value}</div>
                      <div style={{ fontSize: 11, color: '#6b7280', marginTop: 4 }}>{label}</div>
                    </div>
                  ))}
                </div>

                {/* Category breakdown */}
                <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #2a2a3e', padding: 20 }}>
                  <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16 }}>
                    🎯 Threat Category Intelligence
                  </p>
                  {Object.keys(stats.categories).length === 0 ? (
                    <p style={{ color: '#4a4a60', fontSize: 13 }}>No threat categories detected yet.</p>
                  ) : (
                    Object.entries(stats.categories).slice(0, 10).map(([cat, count]) => {
                      const color = Object.entries(CATEGORY_COLORS).find(([k]) => cat.toLowerCase().includes(k))?.[1] || '#6366f1'
                      const pct = Math.round(count / stats.total * 100)
                      return (
                        <div key={cat} style={{ marginBottom: 12 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ fontSize: 12, color: '#a0a0c0', textTransform: 'capitalize' }}>
                              {cat.replace(/_/g, ' ')}
                            </span>
                            <span style={{ fontSize: 12, color, fontWeight: 600 }}>{count} scans ({pct}%)</span>
                          </div>
                          <div style={{ height: 6, background: '#2a2a3e', borderRadius: 3 }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.5s ease' }} />
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>

                {/* Risk breakdown */}
                <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #2a2a3e', padding: 20 }}>
                  <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16 }}>
                    ⚠️ Risk Level Distribution
                  </p>
                  {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(risk => {
                    const count = stats.risk_breakdown[risk] || 0
                    const color = { LOW: '#22c55e', MEDIUM: '#3b82f6', HIGH: '#f59e0b', CRITICAL: '#ef4444' }[risk]
                    const pct = stats.total ? Math.round(count / stats.total * 100) : 0
                    return (
                      <div key={risk} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                        <span style={{ width: 72, fontSize: 11, color, fontWeight: 700 }}>{risk}</span>
                        <div style={{ flex: 1, height: 6, background: '#2a2a3e', borderRadius: 3 }}>
                          <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width 0.5s ease' }} />
                        </div>
                        <span style={{ fontSize: 12, color: '#6b7280', width: 60, textAlign: 'right' }}>{count} ({pct}%)</span>
                      </div>
                    )
                  })}
                </div>

                {/* Rakshit Sir's 3 themes */}
                <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #6366f130', padding: 20 }}>
                  <p style={{ fontSize: 11, color: '#6366f1', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16 }}>
                    🔒 Unlawful Content Monitoring — Key Themes
                  </p>
                  {[
                    { label: 'Real Money Betting / Gambling', key: 'betting',     color: '#ef4444', icon: '🎲' },
                    { label: 'Investment Scams',              key: 'investment',  color: '#f59e0b', icon: '💰' },
                    { label: 'Fake Customer Care',            key: 'customer',    color: '#8b5cf6', icon: '📞' },
                  ].map(({ label, key, color, icon }) => {
                    const count = Object.entries(stats.categories)
                      .filter(([cat]) => cat.toLowerCase().includes(key))
                      .reduce((sum, [, c]) => sum + c, 0)
                    return (
                      <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', borderRadius: 10, background: `${color}10`, border: `1px solid ${color}30`, marginBottom: 10 }}>
                        <span style={{ fontSize: 24 }}>{icon}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: 13, color: '#e0e0f0', fontWeight: 600 }}>{label}</div>
                          <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>
                            {count > 0 ? `${count} instance${count > 1 ? 's' : ''} detected` : 'No instances detected yet'}
                          </div>
                        </div>
                        <div style={{ fontSize: 22, fontWeight: 700, color }}>{count}</div>
                      </div>
                    )
                  })}
                  <p style={{ fontSize: 11, color: '#4a4a60', marginTop: 8, margin: 0 }}>
                    Based on all content scanned via ScamShield AI
                  </p>
                </div>

              </>
            )}
          </div>
        )}

        {/* ── SCAN TAB ── */}
        {tab === 'scan' && (
          <>
            {/* INPUT CARD */}
            <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #2a2a3e', padding: 24, marginBottom: 20 }}>
              <p style={{ fontSize: 13, fontWeight: 600, color: '#6b7280', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
                Analyze Content
              </p>

              <div onClick={() => document.getElementById('fileInput').click()} style={{ border: `2px dashed ${preview ? '#6366f1' : '#3a3a50'}`, borderRadius: 10, padding: 20, textAlign: 'center', cursor: 'pointer', marginBottom: 14, background: preview ? '#12122a' : 'transparent' }}>
                <input id="fileInput" type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFile} />
                {preview ? (
                  <img src={preview} alt="preview" style={{ maxHeight: 180, maxWidth: '100%', borderRadius: 6, objectFit: 'contain' }} />
                ) : (
                  <>
                    <div style={{ fontSize: 28, marginBottom: 6 }}>🖼️</div>
                    <p style={{ color: '#6b7280', fontSize: 13, margin: 0 }}>Click to upload screenshot or image</p>
                    <p style={{ color: '#4a4a60', fontSize: 11, marginTop: 3 }}>JPG, PNG, WebP · OCR reads Hindi, Hinglish, English</p>
                  </>
                )}
              </div>

              <textarea value={caption} onChange={e => setCaption(e.target.value)} placeholder="Or paste caption / message text here..." rows={3} style={{ width: '100%', background: '#12121e', border: '1px solid #3a3a50', borderRadius: 8, padding: '10px 14px', color: '#e0e0f0', fontSize: 13, resize: 'vertical', outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box' }} />

              {error && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>{error}</p>}

              <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                <button onClick={handleScan} disabled={loading} style={{ flex: 1, padding: '11px 20px', borderRadius: 8, background: loading ? '#3a3a50' : 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', color: '#fff', fontSize: 14, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}>
                  {loading ? '🔍 Analyzing...' : '🔍 Scan for Scam'}
                </button>
                {result && (
                  <button onClick={handleReset} style={{ padding: '11px 18px', borderRadius: 8, background: '#1e1e30', border: '1px solid #3a3a50', color: '#a0a0c0', fontSize: 13, cursor: 'pointer' }}>Reset</button>
                )}
              </div>
            </div>

            {/* RESULTS */}
            {result && risk && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

                {/* ROW 1 */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                  <div style={{ background: '#1a1a24', borderRadius: 14, border: `1px solid ${risk.color}40`, padding: 20 }}>
                    <div style={{ display: 'flex', gap: 18, alignItems: 'center', marginBottom: 16 }}>
                      <div style={{ width: 90, height: 90, flexShrink: 0 }}>
                        <CircularProgressbar value={pct} text={`${pct}%`} styles={buildStyles({ textSize: '22px', pathColor: risk.color, textColor: risk.color, trailColor: '#2a2a3e' })} />
                      </div>
                      <div>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 24, background: risk.bg, border: `1px solid ${risk.color}50`, marginBottom: 8 }}>
                          <span style={{ fontSize: 16 }}>{risk.emoji}</span>
                          <span style={{ color: risk.color, fontWeight: 700, fontSize: 14 }}>{risk.label}</span>
                        </div>
                        <div>
                          <span style={{ padding: '3px 10px', borderRadius: 16, background: '#1e1e30', border: '1px solid #3a3a50', fontSize: 11, color: '#a0a0c0', textTransform: 'uppercase', letterSpacing: 1 }}>
                            {result.category.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 11, color: '#6b7280', width: 70 }}>Confidence</span>
                      <div style={{ flex: 1, height: 5, background: '#2a2a3e', borderRadius: 3, overflow: 'hidden' }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: risk.color, borderRadius: 3 }} />
                      </div>
                      <span style={{ fontSize: 11, color: risk.color, width: 30, textAlign: 'right' }}>{pct}%</span>
                    </div>
                  </div>

                  <div style={{ background: '#1a1a24', borderRadius: 14, border: '1px solid #2a2a3e', padding: 20 }}>
                    <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>Confidence Breakdown</p>
                    {Object.entries(layers).length > 0 ? (
                      Object.entries(layers).map(([layer, score]) => (
                        <div key={layer} style={{ marginBottom: 10 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ fontSize: 12, color: '#a0a0c0' }}>{layer}</span>
                            <span style={{ fontSize: 12, color: LAYER_COLORS[layer] || '#6b7280', fontWeight: 600 }}>{score}%</span>
                          </div>
                          <div style={{ height: 5, background: '#2a2a3e', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ width: `${score}%`, height: '100%', background: LAYER_COLORS[layer] || '#6366f1', borderRadius: 3 }} />
                          </div>
                        </div>
                      ))
                    ) : (
                      ['Pattern', 'ML Model', 'BERT', 'Transformer'].map(l => (
                        <div key={l} style={{ marginBottom: 10 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ fontSize: 12, color: '#a0a0c0' }}>{l}</span>
                            <span style={{ fontSize: 11, color: '#4a4a60' }}>Active ✓</span>
                          </div>
                          <div style={{ height: 5, background: '#2a2a3e', borderRadius: 3 }} />
                        </div>
                      ))
                    )}
                    <div style={{ borderTop: '1px solid #2a2a3e', paddingTop: 10, marginTop: 4, display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: 12, color: '#6b7280', fontWeight: 600 }}>Final Risk Score</span>
                      <span style={{ fontSize: 13, color: risk.color, fontWeight: 700 }}>{pct}%</span>
                    </div>
                  </div>
                </div>

                {/* ROW 2 — Evidence */}
                {result.weighted_evidence?.length > 0 && (
                  <div style={{ background: '#1a1a24', borderRadius: 14, border: `1px solid ${risk.color}30`, padding: 20 }}>
                    <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>🔎 Evidence Detected</p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {result.weighted_evidence.slice(0, 7).map((e, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{ minWidth: 160, fontSize: 12, color: risk.color, padding: '4px 10px', borderRadius: 14, background: `${risk.color}15`, border: `1px solid ${risk.color}30`, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>⚠ {e.text || e.indicator}</span>
                          <div style={{ flex: 1, height: 5, background: '#2a2a3e', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ width: `${Math.min(100, e.weight * 4)}%`, height: '100%', background: risk.color, borderRadius: 3, opacity: 0.8 }} />
                          </div>
                          <span style={{ fontSize: 11, color: '#6b7280', width: 32, textAlign: 'right' }}>{e.weight}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ROW 3 — URL Analysis */}
                {result.url_analysis?.length > 0 && (
                  <div style={{ background: '#1a0a0a', borderRadius: 14, border: '1px solid #ef444440', padding: 20 }}>
                    <p style={{ fontSize: 11, color: '#ef4444', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>🔗 Domain Intelligence</p>
                    {result.url_analysis.map((ua, i) => (
                      <div key={i} style={{ background: '#12121e', borderRadius: 10, border: '1px solid #2a2a3e', padding: '14px 16px', marginBottom: i < result.url_analysis.length - 1 ? 10 : 0 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                          <div>
                            <p style={{ fontSize: 13, color: '#fca5a5', fontFamily: 'monospace', margin: '0 0 4px' }}>{ua.domain}</p>
                            {ua.impersonated_brand && <span style={{ padding: '2px 8px', borderRadius: 12, background: '#f59e0b20', border: '1px solid #f59e0b40', fontSize: 11, color: '#fcd34d' }}>⚠ Impersonates {ua.impersonated_brand}</span>}
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: 20, fontWeight: 700, color: ua.risk_score >= 70 ? '#ef4444' : ua.risk_score >= 45 ? '#f59e0b' : '#22c55e' }}>{ua.risk_score}%</div>
                            <div style={{ fontSize: 11, fontWeight: 600, color: ua.risk_score >= 70 ? '#ef4444' : ua.risk_score >= 45 ? '#f59e0b' : '#22c55e' }}>Domain Risk</div>
                          </div>
                        </div>
                        {ua.flags?.length > 0 && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                            {ua.flags.map((f, j) => <span key={j} style={{ padding: '3px 9px', borderRadius: 12, background: '#1e1e30', border: '1px solid #3a3a50', fontSize: 11, color: '#a0a0c0' }}>{f}</span>)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* ROW 4 — Brand Impersonation */}
                {result.brand_impersonation?.length > 0 && (
                  <div style={{ background: '#1a1200', borderRadius: 14, border: '1px solid #f59e0b40', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ fontSize: 20 }}>🏦</span>
                    <div>
                      <p style={{ fontSize: 11, color: '#f59e0b', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, margin: '0 0 6px' }}>Brand Impersonation Detected</p>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {result.brand_impersonation.map((b, i) => <span key={i} style={{ padding: '3px 10px', borderRadius: 14, background: '#f59e0b20', border: '1px solid #f59e0b40', fontSize: 12, color: '#fcd34d' }}>⚠ {b}</span>)}
                      </div>
                    </div>
                  </div>
                )}

                {/* ROW 5 — Analysis + Image Quality */}
                <div style={{ display: 'grid', gridTemplateColumns: result.image_quality ? '2fr 1fr' : '1fr', gap: 14 }}>
                  <div style={{ background: '#12121e', borderRadius: 14, border: '1px solid #2a2a3e', padding: '16px 18px' }}>
                    <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>📋 Analysis</p>
                    <p style={{ fontSize: 13, color: '#c0c0d8', lineHeight: 1.6, margin: 0 }}>{result.explanation}</p>
                  </div>
                  {result.image_quality && (
                    <div style={{ background: '#12121e', borderRadius: 14, border: '1px solid #2a2a3e', padding: '16px 18px' }}>
                      <p style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>🖼 Image Quality</p>
                      {[
                        { label: 'Quality',        value: result.image_quality.image_quality },
                        { label: 'Blur Level',     value: result.image_quality.blur_level },
                        { label: 'Compression',    value: result.image_quality.compression },
                        { label: 'OCR Confidence', value: result.ocr_confidence },
                        { label: 'Text Visibility',value: result.text_visibility },
                        { label: 'Words Found',    value: result.ocr_text ? `${result.ocr_text.split(' ').length}` : '0' },
                      ].map(({ label, value }) => (
                        <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
                          <span style={{ fontSize: 12, color: '#6b7280' }}>{label}</span>
                          <span style={{ fontSize: 12, fontWeight: 600, color: '#a0a0c0' }}>{value}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* ROW 6 — OCR */}
                {result.ocr_text && (
                  <div style={{ background: '#12121e', borderRadius: 14, border: '1px solid #2a2a3e', overflow: 'hidden' }}>
                    <button onClick={() => setShowOcr(!showOcr)} style={{ width: '100%', padding: '14px 18px', background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>📄 Extracted Text (OCR)</span>
                      <span style={{ fontSize: 12, color: '#6b7280' }}>{showOcr ? '▲ Hide' : '▼ Show'}</span>
                    </button>
                    {showOcr && (
                      <div style={{ padding: '0 18px 16px' }}>
                        <div style={{ background: '#0a0a14', borderRadius: 8, border: '1px solid #2a2a3e', padding: '12px 14px' }}>
                          <pre style={{ fontSize: 12, color: '#a0a0c0', fontFamily: 'monospace', lineHeight: 1.7, whiteSpace: 'pre-wrap', margin: 0 }}>{result.ocr_text}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* ROW 7 — Recommended Actions */}
                <div style={{ background: '#0a1a14', borderRadius: 14, border: '1px solid #22c55e40', padding: 20 }}>
                  <p style={{ fontSize: 11, color: '#22c55e', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>🛡 Recommended Actions</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {actions.map((action, i) => (
                      <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <span style={{ width: 20, height: 20, borderRadius: '50%', background: '#22c55e20', border: '1px solid #22c55e40', fontSize: 11, color: '#22c55e', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 1 }}>{i + 1}</span>
                        <span style={{ fontSize: 13, color: '#a0c8a0', lineHeight: 1.5 }}>{action}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* ROW 8 — Feedback */}
                <FeedbackRow result={result} file={file} caption={caption} />

              </div>
            )}
          </>
        )}
      </main>

      <style>{`
        textarea:focus { border-color: #6366f1 !important; }
        button:hover { opacity: 0.9; }
      `}</style>
    </div>
  )
}