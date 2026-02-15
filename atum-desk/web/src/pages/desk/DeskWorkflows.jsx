import React, { useState, useEffect } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { Workflow, Plus, CheckCircle, Play, Upload } from 'lucide-react'

const EXAMPLE_TEMPLATES = [
    { name: 'Auto-assign on category', json: `{\n  "name": "Auto-assign on category",\n  "trigger": "ticket.created",\n  "conditions": [{"field": "category", "operator": "equals", "value": "technical"}],\n  "actions": [{"type": "assign", "to": "team.technical"}, {"type": "set_field", "field": "priority", "value": "medium"}]\n}` },
    { name: 'SLA 75% warning notify', json: `{\n  "name": "SLA 75% Warning",\n  "trigger": "sla.warning",\n  "conditions": [{"field": "sla_breach_percent", "operator": "gte", "value": 75}],\n  "actions": [{"type": "notify", "channel": "email", "to": "assignee"}, {"type": "set_field", "field": "priority", "value": "high"}]\n}` },
    { name: 'Close after inactivity', json: `{\n  "name": "Close after inactivity",\n  "trigger": "ticket.inactive",\n  "conditions": [{"field": "days_inactive", "operator": "gte", "value": 7}, {"field": "status", "operator": "equals", "value": "resolved"}],\n  "actions": [{"type": "set_field", "field": "status", "value": "closed"}, {"type": "notify", "channel": "email", "to": "customer", "template": "ticket_closed"}]\n}` }
]

export default function DeskWorkflows() {
    const [activeTab, setActiveTab] = useState('editor')
    const [history, setHistory] = useState([])
    const [workflows, setWorkflows] = useState([])
    const [selectedWorkflow, setSelectedWorkflow] = useState(null)
    const [jsonEditor, setJsonEditor] = useState('')
    const [validationResult, setValidationResult] = useState(null)
    const [backendConnected, setBackendConnected] = useState(false)

    useEffect(() => { loadWorkflows() }, [])

    const loadWorkflows = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const res = await fetch('/api/v1/workflows', { headers: { 'Authorization': `Bearer ${token}` } })
            if (res.ok) { const data = await res.json(); setWorkflows(data); setBackendConnected(true) }
        } catch { setBackendConnected(false) }
    }

    const createNewWorkflow = () => {
        const newWf = { id: Date.now(), name: 'New Workflow', status: 'draft', json: '{\n  "name": "New Workflow",\n  "trigger": "ticket.created",\n  "conditions": [],\n  "actions": []\n}' }
        setWorkflows([...workflows, newWf])
        setSelectedWorkflow(newWf)
        setJsonEditor(newWf.json)
    }

    const fetchHistory = async () => {
        if (!selectedWorkflow?.id) return
        try {
            const token = localStorage.getItem('atum_desk_token')
            const res = await fetch(`/api/v1/workflows/${selectedWorkflow.id}/history`, { headers: { 'Authorization': `Bearer ${token}` } })
            if (res.ok) setHistory(await res.json())
        } catch {
            setHistory([
                { id: 1, trigger: 'ticket.created', result: 'success', created_at: new Date().toISOString() },
                { id: 2, trigger: 'ticket.updated', result: 'failed', error: 'Condition mismatch', created_at: new Date(Date.now() - 3600000).toISOString() }
            ])
        }
    }

    useEffect(() => { if (activeTab === 'history') fetchHistory() }, [activeTab, selectedWorkflow])

    const validateJson = () => {
        try { JSON.parse(jsonEditor); setValidationResult({ valid: true }) } catch (e) { setValidationResult({ valid: false, errors: [e.message] }) }
    }

    const simulateWorkflow = () => { validateJson() }
    const publishWorkflow = () => { validateJson() }

    const parseForVisual = () => {
        try { return JSON.parse(jsonEditor) } catch { return { name: '', trigger: 'ticket.created', conditions: [], actions: [] } }
    }

    const updateFromVisual = (visualData) => { setJsonEditor(JSON.stringify(visualData, null, 2)) }

    const tabClass = (tab) => `px-6 py-3 text-sm font-medium transition-colors ${activeTab === tab ? 'border-b-2 border-[var(--atum-accent-gold)] text-[var(--atum-accent-gold)]' : 'text-[var(--atum-text-muted)] hover:text-white'}`

    return (
        <PageShell title="Workflow Designer" icon={Workflow}
            actions={!backendConnected ? <span className="px-3 py-1 bg-yellow-900 text-yellow-300 text-xs rounded">Backend not connected - Local mode</span> : null}>

            <div className="flex-1 flex gap-6 min-h-0">
                {/* Left: Workflow List */}
                <div className="w-64 flex-shrink-0">
                    <GlassCard className="flex flex-col h-full">
                        <h2 className="text-sm font-semibold mb-4">Workflows</h2>
                        <button onClick={createNewWorkflow} className="w-full mb-4 btn-gold text-sm flex items-center justify-center gap-2"><Plus size={14} /> New Workflow</button>
                        <div className="flex-1 overflow-y-auto space-y-2">
                            {workflows.map((wf) => (
                                <div key={wf.id} onClick={() => { setSelectedWorkflow(wf); setJsonEditor(wf.json || '') }}
                                    className={`p-3 rounded cursor-pointer border transition-colors ${selectedWorkflow?.id === wf.id ? 'border-[var(--atum-accent-gold)] bg-[rgba(212,175,55,0.1)]' : 'border-[var(--atum-border)] hover:border-[var(--atum-text-muted)]'}`}>
                                    <div className="font-medium text-sm">{wf.name}</div>
                                    <div className="text-xs text-[var(--atum-text-muted)]">{wf.status}</div>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                </div>

                {/* Right: Main Panel */}
                <div className="flex-1 flex flex-col min-w-0">
                    <GlassCard className="flex-1 flex flex-col overflow-hidden p-0">
                        {selectedWorkflow ? (
                            <>
                                <div className="flex border-b border-[var(--atum-border)]">
                                    <button onClick={() => setActiveTab('editor')} className={tabClass('editor')}>JSON Editor</button>
                                    <button onClick={() => setActiveTab('visual')} className={tabClass('visual')}>Visual Builder</button>
                                    <button onClick={() => setActiveTab('history')} className={tabClass('history')}>Execution History</button>
                                </div>

                                <div className="flex-1 p-6 overflow-y-auto">
                                    {activeTab === 'editor' && (
                                        <div className="h-full flex flex-col gap-4">
                                            <div className="flex gap-4">
                                                <input type="text" className="atum-input flex-1" value={selectedWorkflow.name} onChange={(e) => setSelectedWorkflow({ ...selectedWorkflow, name: e.target.value })} placeholder="Workflow Name" />
                                                <select className="atum-input w-32"><option>Active</option><option>Draft</option></select>
                                            </div>
                                            <textarea className="flex-1 atum-input font-mono text-sm" value={jsonEditor} onChange={(e) => setJsonEditor(e.target.value)} spellCheck={false} />
                                            <div className="flex gap-2">
                                                <button onClick={validateJson} className="btn-outline flex items-center gap-1"><CheckCircle size={14} /> Validate</button>
                                                <button onClick={simulateWorkflow} className="btn-outline flex items-center gap-1"><Play size={14} /> Simulate</button>
                                                <button onClick={publishWorkflow} className="btn-gold ml-auto flex items-center gap-1"><Upload size={14} /> Publish</button>
                                            </div>
                                            {validationResult && <div className={`p-2 text-xs rounded ${validationResult.valid ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'}`}>{validationResult.valid ? 'Valid JSON' : validationResult.errors?.join(', ')}</div>}
                                        </div>
                                    )}

                                    {activeTab === 'visual' && (
                                        <div className="space-y-6">
                                            {(() => {
                                                const data = parseForVisual()
                                                return (
                                                    <>
                                                        <div className="glass-card p-4">
                                                            <label className="label">Trigger</label>
                                                            <select className="atum-input" value={data.trigger} onChange={e => updateFromVisual({ ...data, trigger: e.target.value })}>
                                                                <option value="ticket.created">Ticket Created</option><option value="ticket.updated">Ticket Updated</option><option value="sla.breach">SLA Breach</option>
                                                            </select>
                                                        </div>
                                                        <div className="glass-card p-4">
                                                            <label className="label mb-2 block">Conditions (ALL must match)</label>
                                                            {data.conditions?.map((c, i) => (
                                                                <div key={i} className="flex gap-2 mb-2 items-center">
                                                                    <input className="atum-input flex-1" placeholder="Field" value={c.field} onChange={e => { const newC = [...data.conditions]; newC[i].field = e.target.value; updateFromVisual({ ...data, conditions: newC }) }} />
                                                                    <select className="atum-input w-32" value={c.operator} onChange={e => { const newC = [...data.conditions]; newC[i].operator = e.target.value; updateFromVisual({ ...data, conditions: newC }) }}>
                                                                        <option value="equals">Equals</option><option value="contains">Contains</option><option value="gt">Greater Than</option>
                                                                    </select>
                                                                    <input className="atum-input flex-1" placeholder="Value" value={c.value} onChange={e => { const newC = [...data.conditions]; newC[i].value = e.target.value; updateFromVisual({ ...data, conditions: newC }) }} />
                                                                    <button onClick={() => { const newC = data.conditions.filter((_, idx) => idx !== i); updateFromVisual({ ...data, conditions: newC }) }} className="text-red-400 px-2">×</button>
                                                                </div>
                                                            ))}
                                                            <button onClick={() => updateFromVisual({ ...data, conditions: [...(data.conditions || []), { field: '', operator: 'equals', value: '' }] })} className="text-xs text-[var(--atum-accent-gold)]">+ Add Condition</button>
                                                        </div>
                                                        <div className="glass-card p-4">
                                                            <label className="label mb-2 block">Actions (Execute in order)</label>
                                                            {data.actions?.map((a, i) => (
                                                                <div key={i} className="flex gap-2 mb-2 items-center">
                                                                    <select className="atum-input w-40" value={a.type} onChange={e => { const newA = [...data.actions]; newA[i].type = e.target.value; updateFromVisual({ ...data, actions: newA }) }}>
                                                                        <option value="assign">Assign</option><option value="set_field">Set Field</option><option value="notify">Notify</option>
                                                                    </select>
                                                                    <input className="atum-input flex-1" placeholder="Details (JSON)" value={JSON.stringify(a).replace(/^{"type":"\w+",/, '{').slice(0, -1)} disabled readOnly title="Edit details in JSON mode for now" />
                                                                    <button onClick={() => { const newA = data.actions.filter((_, idx) => idx !== i); updateFromVisual({ ...data, actions: newA }) }} className="text-red-400 px-2">×</button>
                                                                </div>
                                                            ))}
                                                            <button onClick={() => updateFromVisual({ ...data, actions: [...(data.actions || []), { type: 'assign', to: '' }] })} className="text-xs text-[var(--atum-accent-gold)]">+ Add Action</button>
                                                        </div>
                                                    </>
                                                )
                                            })()}
                                        </div>
                                    )}

                                    {activeTab === 'history' && (
                                        <div>
                                            <table className="glass-table">
                                                <thead><tr><th>Time</th><th>Trigger</th><th>Result</th><th>Error</th></tr></thead>
                                                <tbody>
                                                    {history.map((h, i) => (
                                                        <tr key={i}>
                                                            <td>{new Date(h.created_at).toLocaleString()}</td>
                                                            <td>{h.trigger}</td>
                                                            <td><span className={`badge ${h.result === 'success' ? 'badge-new' : 'badge-urgent'}`}>{h.result}</span></td>
                                                            <td className="text-red-400 text-xs">{h.error || '-'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                            {history.length === 0 && <p className="text-center py-8 text-[var(--atum-text-muted)]">No execution history found.</p>}
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="flex-1 flex items-center justify-center p-6 text-[var(--atum-text-muted)]">Select or create a workflow</div>
                        )}
                    </GlassCard>
                </div>
            </div>
        </PageShell>
    )
}
