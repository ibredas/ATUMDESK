import React from 'react'
import { Link } from 'react-router-dom'
import { Wordmark } from '../components/Brand/Wordmark'
import AtumSilhouette from '../assets/atum/atum-silhouette.svg'

export default function LandingPage() {
    return (
        <div className="relative min-h-screen w-full overflow-x-hidden bg-[var(--bg-0)] text-[var(--text-0)] selection:bg-[var(--glow-gold)] selection:text-black">

            {/* Background Ambience */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-[-30%] right-[-10%] w-[90vw] h-[90vw] rounded-full bg-[radial-gradient(circle,rgba(212,175,55,0.12)_0%,transparent_70%)] opacity-50 mix-blend-screen animate-pulse-slow"></div>
                <div className="absolute top-0 right-0 h-[80vh] w-auto opacity-40 mix-blend-overlay transform scale-x-[-1]">
                    <img src={AtumSilhouette} alt="" className="h-full w-auto object-contain drop-shadow-[0_0_50px_rgba(0,0,0,0.8)]" />
                </div>
                <div className="grain-overlay"></div>
            </div>

            {/* Navigation */}
            <nav className="relative z-50 flex items-center justify-between px-6 py-6 lg:px-12 backdrop-blur-sm border-b border-[rgba(255,255,255,0.02)]">
                <div className="flex items-center gap-4">
                    <Link to="/" className="group">
                        <Wordmark className="h-8 text-[var(--text-0)]" suffix="DESK" />
                    </Link>
                </div>
                <div className="flex items-center gap-3">
                    <Link
                        to="/portal/login"
                        className="text-xs font-bold tracking-widest uppercase hover:text-[var(--accent-gold)] transition-colors border border-[rgba(255,255,255,0.1)] px-4 py-2 rounded-full hover:bg-[rgba(255,255,255,0.05)]"
                    >
                        Customer Portal
                    </Link>
                    <Link
                        to="/desk/login"
                        className="group relative overflow-hidden rounded-full bg-[var(--text-0)] px-6 py-2 text-black font-bold tracking-wide transition-all hover:scale-105 text-xs uppercase"
                    >
                        <span className="relative z-10 group-hover:text-[var(--bg-0)]">Staff Desk</span>
                        <div className="absolute inset-0 -translate-x-[102%] group-hover:translate-x-0 bg-[var(--accent-gold)] transition-transform duration-300 ease-out"></div>
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="relative z-10 px-6 lg:px-12 pt-24 pb-0 animate-rise">
                <div className="max-w-4xl">
                    <h1 className="text-5xl lg:text-8xl font-black tracking-tight leading-[0.9] text-white mb-8 drop-shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                        Support Excellence. <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-[var(--text-1)]">Reimagined.</span>
                    </h1>
                    <p className="text-xl lg:text-2xl text-[var(--text-1)] max-w-2xl font-light mb-12 leading-relaxed">
                        Enterprise-grade helpdesk and ticketing platform. <br />
                        <span className="text-[var(--accent-gold)] font-medium">AI-powered triage. Real-time updates. Multi-tenant.</span>
                    </p>

                    <div className="flex flex-col sm:flex-row gap-6">
                        <Link
                            to="/desk/login"
                            className="group relative overflow-hidden rounded-full bg-[var(--text-0)] px-10 py-5 text-black font-bold tracking-wide transition-all hover:scale-105 hover:shadow-[0_0_30px_rgba(212,175,55,0.4)] text-center"
                        >
                            <span className="relative z-10 group-hover:text-[var(--bg-0)]">OPEN DESK</span>
                            <div className="absolute inset-0 -translate-x-[102%] group-hover:translate-x-0 bg-[var(--accent-gold)] transition-transform duration-300 ease-out"></div>
                        </Link>

                        <Link
                            to="/portal/login"
                            className="px-8 py-5 rounded-full border border-[var(--glass-border)] hover:bg-[rgba(255,255,255,0.05)] transition-all uppercase text-xs font-bold tracking-widest text-[var(--text-1)] hover:text-white hover:border-[var(--accent-gold)] text-center flex items-center justify-center"
                        >
                            Customer Portal
                        </Link>
                    </div>
                </div>
            </main>

            {/* Elite Access Menu */}
            <section className="relative z-10 mt-32 px-6 lg:px-12 pb-16">
                <div className="max-w-5xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-2">Access Points</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Staff Desk Card */}
                        <Link to="/desk/login" className="nav-card group">
                            <div className="nav-card-icon" style={{ background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.25)' }}>
                                🛡️
                            </div>
                            <div className="nav-card-title">Staff Desk</div>
                            <div className="nav-card-desc">
                                Agent workspace for managing support tickets. Inbox, dashboard, assignment, SLA tracking, and AI-assisted responses.
                            </div>
                            <div className="nav-card-arrow">→</div>
                        </Link>

                        {/* Customer Portal Card */}
                        <Link to="/portal/login" className="nav-card group">
                            <div className="nav-card-icon" style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.25)' }}>
                                🎫
                            </div>
                            <div className="nav-card-title">Customer Portal</div>
                            <div className="nav-card-desc">
                                Self-service portal for customers. Submit tickets, track status, browse knowledge base, and communicate with support.
                            </div>
                            <div className="nav-card-arrow">→</div>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Feature Strip */}
            <section className="relative z-10 border-y border-[var(--glass-border)] bg-[rgba(5,5,5,0.5)] backdrop-blur-md overflow-hidden">
                <div className="max-w-7xl mx-auto px-6 lg:px-12 py-16">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        {[
                            { icon: '⚡', title: 'AI Triage', desc: 'Auto-classify and route tickets with intelligent AI analysis' },
                            { icon: '📡', title: 'Real-Time', desc: 'Live ticket updates and notifications via WebSocket' },
                            { icon: '🏢', title: 'Multi-Tenant', desc: 'Full organization isolation with role-based access control' },
                            { icon: '🔒', title: 'Enterprise Security', desc: 'JWT auth, RBAC, audit logging, and data encryption' },
                        ].map((feat, i) => (
                            <div key={i} className="group text-center md:text-left">
                                <div className="text-2xl mb-4">{feat.icon}</div>
                                <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-2 group-hover:text-[var(--accent-gold)] transition-colors">{feat.title}</h3>
                                <p className="text-xs text-[var(--text-2)] leading-relaxed">{feat.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Bento Grid */}
            <section className="relative z-10 px-6 lg:px-12 py-32">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto">
                    <div className="glass-panel col-span-1 md:col-span-2 p-10 rounded-2xl min-h-[300px] flex flex-col justify-end relative overflow-hidden group border border-[var(--glass-border)]">
                        <div className="absolute inset-0 bg-gradient-to-t from-black/90 to-transparent z-10"></div>
                        <div className="relative z-20">
                            <h3 className="text-3xl font-bold mb-4 group-hover:text-[var(--accent-gold)] transition-colors">Intelligent Ticketing</h3>
                            <p className="text-[var(--text-1)] max-w-md">
                                Unified inbox with AI-powered categorization, smart assignment, SLA monitoring, and automated workflows for your entire support operation.
                            </p>
                        </div>
                        <div className="absolute top-0 right-0 w-full h-full opacity-10 group-hover:opacity-20 transition-opacity">
                            <svg className="w-full h-full" viewBox="0 0 400 300">
                                <path d="M0 0 L400 300" stroke="white" strokeWidth="0.5" />
                                <path d="M400 0 L0 300" stroke="white" strokeWidth="0.5" />
                                <circle cx="200" cy="150" r="100" stroke="white" strokeWidth="0.5" fill="none" />
                            </svg>
                        </div>
                    </div>

                    <div className="glass-panel p-10 rounded-2xl min-h-[300px] flex flex-col justify-end group border border-[var(--glass-border)]">
                        <div className="text-4xl mb-auto text-[var(--text-2)] group-hover:text-[var(--accent-gold)] transition-colors">📊</div>
                        <h3 className="text-3xl font-bold mb-4">Analytics</h3>
                        <p className="text-[var(--text-1)]">Real-time metrics, response time tracking, agent performance, and SLA compliance reporting.</p>
                    </div>
                </div>
            </section>

            {/* AI Copilot Section - NEW */}
            <section className="relative z-10 px-6 lg:px-12 py-24 bg-[rgba(5,5,5,0.3)]">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--accent-gold)] mb-2">◆ AI Intelligence</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <h3 className="text-4xl font-bold mb-8">AI Copilot</h3>
                    <p className="text-xl text-[var(--text-1)] max-w-2xl mb-12">
                        Your intelligent assistant for support operations. Get AI-generated replies, 
                        suggested actions, and contextual insights — all with full audit trails.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🤖</div>
                            <h4 className="text-lg font-bold mb-3">Smart Replies</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• AI draft responses</li>
                                <li>• Context-aware suggestions</li>
                                <li>• Confidence scores</li>
                                <li>• One-click apply</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">📋</div>
                            <h4 className="text-lg font-bold mb-3">Action Checklist</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Suggested next steps</li>
                                <li>• Auto-triage options</li>
                                <li>• Priority recommendations</li>
                                <li>• Assignment hints</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🔍</div>
                            <h4 className="text-lg font-bold mb-3">Evidence Cards</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• KB article citations</li>
                                <li>• Similar ticket references</li>
                                <li>• Full trace replay</li>
                                <li>• Citable sources</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-12">
                        <Link
                            to="/desk/ai/agent-assist"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--accent-gold)] text-black font-bold rounded-full hover:scale-105 transition-transform"
                        >
                            Open AI Copilot →
                        </Link>
                    </div>
                </div>
            </section>

            {/* GraphRAG Knowledge Brain Section - NEW */}
            <section className="relative z-10 px-6 lg:px-12 py-24">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-2">Knowledge</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <h3 className="text-4xl font-bold mb-8">GraphRAG Knowledge Brain</h3>
                    <p className="text-xl text-[var(--text-1)] max-w-2xl mb-12">
                        AI-powered knowledge base with graph relationships. Contextual search, 
                        auto-suggestions, and intelligent deflection for faster resolutions.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🧠</div>
                            <h4 className="text-lg font-bold mb-3">Graph Search</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Semantic vector search</li>
                                <li>• Relationship traversal</li>
                                <li>• Context chains</li>
                                <li>• Multi-hop queries</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">💡</div>
                            <h4 className="text-lg font-bold mb-3">Smart Deflection</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Auto-suggest articles</li>
                                <li>• Customer self-service</li>
                                <li>• Voting system</li>
                                <li>• Relevance scoring</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">📊</div>
                            <h4 className="text-lg font-bold mb-3">Vector Indexing</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• pgvector HNSW</li>
                                <li>• Background workers</li>
                                <li>• Incremental updates</li>
                                <li>• Full-text + semantic</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-12">
                        <Link
                            to="/desk/kb"
                            className="inline-flex items-center gap-2 px-6 py-3 border border-[var(--glass-border)] text-white font-bold rounded-full hover:border-[var(--accent-gold)] transition-colors"
                        >
                            Open Knowledge Base →
                        </Link>
                    </div>
                </div>
            </section>

            {/* Security & 2FA Section - NEW */}
            <section className="relative z-10 px-6 lg:px-12 py-24 bg-[rgba(5,5,5,0.3)]">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-2">Security</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <h3 className="text-4xl font-bold mb-8">Enterprise Security</h3>
                    <p className="text-xl text-[var(--text-1)] max-w-2xl mb-12">
                        Bank-grade security with 2FA, audit logging, IP restrictions, and 
                        role-based access control. Your data stays protected.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🔐</div>
                            <h4 className="text-lg font-bold mb-3">2FA / TOTP</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Time-based OTP</li>
                                <li>• Recovery codes</li>
                                <li>• Org-wide enforcement</li>
                                <li>• QR code setup</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">📝</div>
                            <h4 className="text-lg font-bold mb-3">Audit Logs</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Full action history</li>
                                <li>• Export to CSV</li>
                                <li>• Retention policies</li>
                                <li>• Searchable</li>
                            </ul>
                        </div>

                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🌐</div>
                            <h4 className="text-lg font-bold mb-3">IP Restrictions</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• CIDR allowlisting</li>
                                <li>• Admin endpoints</li>
                                <li>• Per-org settings</li>
                                <li>• VPN support</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-12">
                        <Link
                            to="/desk/admin/security"
                            className="inline-flex items-center gap-2 px-6 py-3 border border-[var(--glass-border)] text-white font-bold rounded-full hover:border-[var(--accent-gold)] transition-colors"
                        >
                            Security Settings →
                        </Link>
                    </div>
                </div>
            </section>

            {/* Workflow Designer Section - NEW */}
            <section className="relative z-10 px-6 lg:px-12 py-24 bg-[rgba(5,5,5,0.3)]">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-2">Automation</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <h3 className="text-4xl font-bold mb-8">Workflow Designer</h3>
                    <p className="text-xl text-[var(--text-1)] max-w-2xl mb-12">
                        Build powerful automation workflows without code. Trigger actions based on ticket events, status changes, and SLA warnings.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Card 1: Triggers */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">⚡</div>
                            <h4 className="text-lg font-bold mb-3">Triggers</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Ticket created</li>
                                <li>• Status changed</li>
                                <li>• SLA warning (75%/90%)</li>
                                <li>• Priority escalated</li>
                                <li>• Customer replied</li>
                            </ul>
                        </div>

                        {/* Card 2: Actions */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🎯</div>
                            <h4 className="text-lg font-bold mb-3">Actions</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Assign to agent/team</li>
                                <li>• Set fields/priority</li>
                                <li>• Send notifications</li>
                                <li>• Trigger webhook</li>
                                <li>• Create follow-up</li>
                            </ul>
                        </div>

                        {/* Card 3: Safe Preview */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🔒</div>
                            <h4 className="text-lg font-bold mb-3">Safe Preview</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Validate before publish</li>
                                <li>• Simulate execution</li>
                                <li>• Test mode support</li>
                                <li>• Full audit trail</li>
                                <li>• Rollback anytime</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-12">
                        <Link
                            to="/desk/workflows"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--text-0)] text-black font-bold rounded-full hover:scale-105 transition-transform"
                        >
                            Open Workflow Designer →
                        </Link>
                    </div>
                </div>
            </section>

            {/* Monitoring & Self-Healing Section - NEW */}
            <section className="relative z-10 px-6 lg:px-12 py-24">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-12">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-2">Observability</h2>
                        <div className="w-12 h-0.5 bg-[var(--accent-gold)] opacity-60"></div>
                    </div>

                    <h3 className="text-4xl font-bold mb-8">Monitoring & Self-Healing</h3>
                    <p className="text-xl text-[var(--text-1)] max-w-2xl mb-12">
                        Enterprise-grade observability with automatic service recovery. Stay ahead of issues with real-time health checks and Prometheus metrics.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Card 1: Live Health */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">💚</div>
                            <h4 className="text-lg font-bold mb-3">Live Health</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• API Service: Healthy</li>
                                <li>• SLA Worker: Healthy</li>
                                <li>• RAG Worker: Healthy</li>
                                <li>• Job Worker: Healthy</li>
                                <li>• Database: Connected</li>
                            </ul>
                        </div>

                        {/* Card 2: Metrics */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">📈</div>
                            <h4 className="text-lg font-bold mb-3">Prometheus Metrics</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Request rate</li>
                                <li>• Response time p50/p95</li>
                                <li>• Error rate</li>
                                <li>• DB pool usage</li>
                                <li>• Queue depth</li>
                            </ul>
                        </div>

                        {/* Card 3: Self-Healing */}
                        <div className="glass-panel p-8 rounded-2xl border border-[var(--glass-border)] hover:border-[var(--accent-gold)] transition-colors">
                            <div className="text-3xl mb-4">🛡️</div>
                            <h4 className="text-lg font-bold mb-3">Self-Healing</h4>
                            <ul className="text-sm text-[var(--text-2)] space-y-2">
                                <li>• Restart on failure</li>
                                <li>• Memory caps enforced</li>
                                <li>• Watchdog timer</li>
                                <li>• Rate limiting</li>
                                <li>• Circuit breaker</li>
                            </ul>
                        </div>
                    </div>

                    <div className="mt-12">
                        <Link
                            to="/desk/monitoring"
                            className="inline-flex items-center gap-2 px-6 py-3 border border-[var(--accent-gold)] text-[var(--accent-gold)] font-bold rounded-full hover:bg-[var(--accent-gold)] hover:text-black transition-colors"
                        >
                            Open Monitoring →
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="relative z-10 border-t border-[var(--glass-border)] py-12 px-6 lg:px-12 bg-black/60 backdrop-blur-xl">
                <div className="flex flex-col md:flex-row justify-between items-center opacity-60 text-[10px] uppercase tracking-widest text-[var(--text-1)]">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[var(--accent-gold)]"></div>
                        <span>© 2026 ATUM DESK | v1.0.0</span>
                    </div>
                    <div className="flex gap-8 mt-4 md:mt-0">
                        <Link to="/desk/login" className="hover:text-white transition-colors">Staff Desk</Link>
                        <Link to="/portal/login" className="hover:text-white transition-colors">Portal</Link>
                        <a href="#" className="hover:text-white transition-colors">Docs</a>
                    </div>
                </div>
            </footer>

        </div>
    )
}
