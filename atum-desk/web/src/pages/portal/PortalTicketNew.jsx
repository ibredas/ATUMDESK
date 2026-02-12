import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

export default function PortalTicketNew() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('medium')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!subject || !description) { setError('Please fill in all fields.'); return }
    setLoading(true)
    try {
      const res = await fetch('/api/v1/tickets', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, description, priority }),
      })
      if (res.status === 401) { navigate('/portal/login'); return }
      if (res.ok) { navigate('/portal/tickets') }
      else {
        const data = await res.json()
        setError(data.detail || 'Failed to create ticket')
      }
    } catch (e) { setError('Connection failed') }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-[var(--bg-0)]">
      <div className="grain-overlay"></div>
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 border-b border-[var(--glass-border)] backdrop-blur-sm">
        <Wordmark className="h-6 text-[#60a5fa]" suffix="PORTAL" />
        <Link to="/portal/tickets" className="text-[10px] uppercase tracking-widest text-[var(--text-2)] hover:text-white transition-colors">
          ← My Tickets
        </Link>
      </nav>

      <div className="relative z-10 max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Submit a Ticket</h1>

        <form onSubmit={handleSubmit} className="glass-panel rounded-xl p-8 space-y-6">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs text-center font-medium">
              ⚠️ {error}
            </div>
          )}
          <div>
            <label className="atum-label">Subject</label>
            <input value={subject} onChange={(e) => setSubject(e.target.value)} className="atum-input" placeholder="Brief summary of your issue" />
          </div>
          <div>
            <label className="atum-label">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="atum-input" rows={6} placeholder="Describe your issue in detail..." style={{ resize: 'vertical' }} />
          </div>
          <div>
            <label className="atum-label">Priority</label>
            <div className="flex gap-2">
              {['low', 'medium', 'high', 'urgent'].map(p => (
                <button key={p} type="button" onClick={() => setPriority(p)}
                  className={`text-[10px] uppercase tracking-widest font-bold px-4 py-2 rounded-full transition-all border ${priority === p ? `badge-${p} border-current` : 'border-[var(--glass-border)] text-[var(--text-2)] hover:bg-white/5'
                    }`}>
                  {p}
                </button>
              ))}
            </div>
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-4 rounded-lg bg-[#3b82f6] text-white font-bold tracking-wide transition-all hover:bg-[#2563eb] hover:shadow-[0_0_20px_rgba(59,130,246,0.4)] border border-blue-500/30">
            {loading ? 'Submitting...' : 'Submit Ticket'}
          </button>
        </form>
      </div>
    </div>
  )
}
