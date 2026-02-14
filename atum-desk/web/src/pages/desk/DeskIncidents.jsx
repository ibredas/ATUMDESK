import React from 'react'

export default function DeskIncidents() {
    return (
        <div className="desk-page">
            <div className="desk-page-header">
                <h1>🚨 Incidents</h1>
                <p className="text-[var(--text-1)]">Major incident management</p>
            </div>
            <div className="glass-panel p-8 rounded-xl border border-[var(--glass-border)]">
                <div className="text-center py-12">
                    <div className="text-4xl mb-4">🚨</div>
                    <h2 className="text-xl font-bold mb-2">Incident Management</h2>
                    <p className="text-[var(--text-2)]">Coming soon - Track and manage major incidents</p>
                </div>
            </div>
        </div>
    )
}
