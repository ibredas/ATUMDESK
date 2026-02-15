import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'
import AtumSilhouette from '../../assets/atum/atum-silhouette.svg'
import GlyphPattern from '../../assets/atum/glyph-pattern.svg'
import { Eye, EyeOff, AlertTriangle } from 'lucide-react'

export default function PortalLogin() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    if (!email || !password) {
      setError('Please enter your credentials.')
      return
    }
    setLoading(true)
    try {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)

      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form,
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Access Denied')
        return
      }
      localStorage.setItem('atum_desk_token', data.access_token)
      localStorage.setItem('atum_desk_refresh', data.refresh_token)
      navigate('/portal/tickets')
    } catch (err) {
      setError('Connection failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[var(--atum-bg)] text-[var(--atum-text)]">

      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[-20%] right-[-10%] w-[80vw] h-[80vw] rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.1)_0%,transparent_70%)] opacity-60 mix-blend-screen animate-pulse-slow"></div>
        <div className="absolute bottom-0 right-0 h-[85vh] w-auto opacity-40 mix-blend-overlay z-0 transform scale-x-[-1]">
          <img src={AtumSilhouette} alt="" className="h-full w-auto object-contain" />
        </div>
        <div className="grain-overlay"></div>
      </div>

      {/* Login Card */}
      <div className="relative z-10 flex min-h-screen w-full items-center justify-center lg:justify-start lg:pl-[15%]">
        <div className="relative group w-full max-w-md px-4">

          <div className="absolute inset-0 -z-10 rounded-2xl bg-[radial-gradient(circle,rgba(59,130,246,0.3)_0%,transparent_70%)] solar-bloom-halo"></div>

          <div className="glass-panel relative w-full p-8 sm:p-12 rounded-2xl border-t border-[rgba(255,255,255,0.1)] shadow-2xl backdrop-blur-xl transform transition-all duration-500 hover:translate-y-[-2px] animate-rise overflow-hidden">

            <Link to="/" className="absolute top-6 left-6 text-[var(--atum-text-muted)] hover:text-white transition-colors text-sm">
              ← Back
            </Link>

            <div
              className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] mix-blend-overlay"
              style={{
                backgroundImage: `url(${GlyphPattern})`,
                backgroundSize: '40px 40px',
                maskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
                WebkitMaskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
              }}
            ></div>

            <div className="relative z-10">
              <div className="text-center mb-10">
                <div className="flex justify-center mb-6">
                  <Wordmark className="h-12 text-[#60a5fa] drop-shadow-[0_0_15px_rgba(59,130,246,0.3)]" suffix="PORTAL" />
                </div>
                <p className="text-[var(--atum-text-1)] text-xs tracking-[0.2em] uppercase opacity-80 font-medium">
                  Customer Access
                </p>
              </div>

              <form onSubmit={handleLogin} className="space-y-6" autoComplete="off">
                {error && (
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-200 text-xs text-center font-medium flex items-center justify-center gap-2">
                    <AlertTriangle size={14} /> {error}
                  </div>
                )}

                <div className="space-y-2">
                  <label className="atum-label">Email</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    className="atum-input" placeholder="customer@company.com" autoComplete="off" />
                </div>

                <div className="space-y-2">
                  <label className="atum-label">Password</label>
                  <div className="relative">
                    <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                      className="atum-input" style={{ paddingRight: '44px' }} placeholder="••••••••" autoComplete="new-password" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--atum-text-muted)] hover:text-white transition-colors text-sm">
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button type="submit" disabled={loading}
                  className="w-full py-4 mt-4 rounded-lg bg-[#3b82f6] text-white font-bold tracking-wide transition-all hover:bg-[#2563eb] hover:shadow-[0_0_20px_rgba(59,130,246,0.4)] border border-blue-500/30">
                  {loading ? 'Authenticating...' : 'Sign In'}
                </button>
              </form>

              <div className="mt-8 flex justify-between text-[10px] text-[var(--atum-text-muted)] uppercase tracking-wide">
                <Link to="/desk/login" className="hover:text-[var(--atum-accent-gold)] transition-colors">
                  ← Staff Desk
                </Link>
                <Link to="/" className="hover:text-[var(--atum-accent-gold)] transition-colors">
                  Home
                </Link>
              </div>

              <div className="mt-6 text-center border-t border-[var(--atum-border)] pt-4">
                <span className="text-[10px] text-[var(--atum-text-muted)] uppercase tracking-widest">
                  ATUM DESK v1.0.0 • Customer Portal
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
