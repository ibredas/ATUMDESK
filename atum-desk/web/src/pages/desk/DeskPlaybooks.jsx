import React, { useState, useEffect } from 'react'

export default function DeskPlaybooks() {
    const [playbooks, setPlaybooks] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadPlaybooks()
    }, [])

    const loadPlaybooks = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/playbooks', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setPlaybooks(data)
            }
        } catch (err) {
            setError('Failed to load playbooks')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Playbooks / Runbooks</h1>
                <button className="px-4 py-2 bg-[var(--accent-gold)] text-black rounded-lg font-medium">
                    + Create Playbook
                </button>
            </div>

            {loading ? (
                <div className="text-[var(--text-muted)]">Loading playbooks...</div>
            ) : error ? (
                <div className="text-red-400">{error}</div>
            ) : playbooks.length === 0 ? (
                <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-8 text-center">
                    <div className="text-4xl mb-4">📋</div>
                    <h3 className="text-lg font-medium mb-2">No Playbooks Yet</h3>
                    <p className="text-[var(--text-muted)] mb-4">
                        Create incident response playbooks to guide your team through common scenarios.
                    </p>
                    <button className="px-4 py-2 bg-[var(--accent-gold)] text-black rounded-lg font-medium">
                        Create Your First Playbook
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {playbooks.map((playbook) => (
                        <div key={playbook.id} className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                            <h3 className="font-semibold mb-2">{playbook.name}</h3>
                            <p className="text-sm text-[var(--text-muted)] mb-4">
                                {playbook.description || 'No description'}
                            </p>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-[var(--text-muted)]">
                                    {playbook.steps?.length || 0} steps
                                </span>
                                <button className="text-[var(--accent-gold)] hover:underline">
                                    View
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Pre-built Templates */}
            <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4">Quick Start Templates</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                        <h3 className="font-medium mb-2">🔴 Incident Response</h3>
                        <p className="text-sm text-[var(--text-muted)]">
                            Standard incident response workflow with escalation steps
                        </p>
                    </div>
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                        <h3 className="font-medium mb-2">🆘 Password Reset</h3>
                        <p className="text-sm text-[var(--text-muted)]">
                            Guided password reset verification process
                        </p>
                    </div>
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                        <h3 className="font-medium mb-2">💻 Server Outage</h3>
                        <p className="text-sm text-[var(--text-muted)]">
                            Server outage troubleshooting and communication steps
                        </p>
                    </div>
                    <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                        <h3 className="font-medium mb-2">🔐 Security Breach</h3>
                        <p className="text-sm text-[var(--text-muted)]">
                            Security incident containment and reporting steps
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
