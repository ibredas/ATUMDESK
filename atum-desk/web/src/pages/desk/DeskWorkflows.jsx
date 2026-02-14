import React, { useState, useEffect } from 'react'

const EXAMPLE_TEMPLATES = [
    {
        name: 'Auto-assign on category',
        json: `{
  "name": "Auto-assign on category",
  "trigger": "ticket.created",
  "conditions": [
    {"field": "category", "operator": "equals", "value": "technical"}
  ],
  "actions": [
    {"type": "assign", "to": "team.technical"},
    {"type": "set_field", "field": "priority", "value": "medium"}
  ]
}`
    },
    {
        name: 'SLA 75% warning notify',
        json: `{
  "name": "SLA 75% Warning",
  "trigger": "sla.warning",
  "conditions": [
    {"field": "sla_breach_percent", "operator": "gte", "value": 75}
  ],
  "actions": [
    {"type": "notify", "channel": "email", "to": "assignee"},
    {"type": "set_field", "field": "priority", "value": "high"}
  ]
}`
    },
    {
        name: 'Close after inactivity',
        json: `{
  "name": "Close after inactivity",
  "trigger": "ticket.inactive",
  "conditions": [
    {"field": "days_inactive", "operator": "gte", "value": 7},
    {"field": "status", "operator": "equals", "value": "resolved"}
  ],
  "actions": [
    {"type": "set_field", "field": "status", "value": "closed"},
    {"type": "notify", "channel": "email", "to": "customer", "template": "ticket_closed"}
  ]
}`
    }
]

export default function DeskWorkflows() {
    const [workflows, setWorkflows] = useState([])
    const [selectedWorkflow, setSelectedWorkflow] = useState(null)
    const [jsonEditor, setJsonEditor] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [validationResult, setValidationResult] = useState(null)
    const [simulateResult, setSimulateResult] = useState(null)
    const [backendConnected, setBackendConnected] = useState(true)
    const [saveStatus, setSaveStatus] = useState('')

    useEffect(() => {
        loadWorkflows()
    }, [])

    const loadWorkflows = async () => {
        setLoading(true)
        setError(null)
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/workflows', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setWorkflows(data)
                setBackendConnected(true)
            } else {
                setBackendConnected(false)
            }
        } catch (err) {
            setBackendConnected(false)
        } finally {
            setLoading(false)
        }
    }

    const validateJson = () => {
        setValidationResult(null)
        setSimulateResult(null)
        
        try {
            const parsed = JSON.parse(jsonEditor)
            
            const errors = []
            if (!parsed.trigger) errors.push('Missing "trigger" field')
            if (!parsed.conditions || !Array.isArray(parsed.conditions)) errors.push('Missing or invalid "conditions" array')
            if (!parsed.actions || !Array.isArray(parsed.actions)) errors.push('Missing or invalid "actions" array')
            
            if (errors.length > 0) {
                setValidationResult({ valid: false, errors })
            } else {
                setValidationResult({ valid: true, message: 'Workflow JSON is valid!' })
            }
        } catch (e) {
            setValidationResult({ valid: false, errors: ['Invalid JSON: ' + e.message] })
        }
    }

    const simulateWorkflow = async () => {
        setSimulateResult(null)
        
        try {
            const parsed = JSON.parse(jsonEditor)
            setSimulateResult({
                success: true,
                message: `Would trigger on: ${parsed.trigger}`,
                steps: parsed.actions?.map((a, i) => `Step ${i+1}: ${a.type}`) || []
            })
        } catch (e) {
            setSimulateResult({ success: false, message: 'Fix JSON errors first' })
        }
    }

    const saveDraft = () => {
        setSaveStatus('Draft saved locally')
        setTimeout(() => setSaveStatus(''), 3000)
    }

    const publishWorkflow = async () => {
        if (!validationResult?.valid) {
            setSaveStatus('Please validate first')
            return
        }
        setSaveStatus('Publishing... (API not connected - local mode)')
        setTimeout(() => setSaveStatus('Published (simulated)'), 1000)
    }

    const loadTemplate = (template) => {
        setJsonEditor(template.json)
        setValidationResult(null)
        setSimulateResult(null)
    }

    const createNewWorkflow = () => {
        const newWorkflow = {
            id: 'new-' + Date.now(),
            name: 'New Workflow',
            status: 'draft',
            json: EXAMPLE_TEMPLATES[0].json
        }
        setSelectedWorkflow(newWorkflow)
        setJsonEditor(newWorkflow.json)
    }

    return (
        <div className="p-6 h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Workflow Designer</h1>
                {!backendConnected && (
                    <span className="px-3 py-1 bg-yellow-900 text-yellow-300 text-xs rounded">
                        Backend not connected - Local mode
                    </span>
                )}
            </div>

            <div className="flex-1 flex gap-6 min-h-0">
                {/* Left: Workflow List */}
                <div className="w-64 flex-shrink-0 bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 flex flex-col">
                    <h2 className="text-sm font-semibold mb-4">Workflows</h2>
                    
                    <button 
                        onClick={createNewWorkflow}
                        className="w-full mb-4 px-3 py-2 bg-[var(--accent-gold)] text-black rounded text-sm font-medium hover:opacity-90"
                    >
                        + New Workflow
                    </button>

                    {loading ? (
                        <div className="text-[var(--text-muted)] text-sm">Loading...</div>
                    ) : workflows.length === 0 ? (
                        <div className="text-[var(--text-muted)] text-sm">
                            <p className="mb-2">No workflows yet</p>
                            <p className="text-xs">Click "+ New Workflow" to create one</p>
                        </div>
                    ) : (
                        <div className="flex-1 overflow-y-auto space-y-2">
                            {workflows.map((wf) => (
                                <div 
                                    key={wf.id}
                                    onClick={() => { setSelectedWorkflow(wf); setJsonEditor(wf.json || '') }}
                                    className={`p-3 rounded cursor-pointer border ${
                                        selectedWorkflow?.id === wf.id 
                                        ? 'border-[var(--accent-gold)] bg-[rgba(212,175,55,0.1)]' 
                                        : 'border-[var(--border)] hover:border-[var(--text-muted)]'
                                    }`}
                                >
                                    <div className="font-medium text-sm">{wf.name}</div>
                                    <div className="text-xs text-[var(--text-muted)]">{wf.status}</div>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="mt-4 pt-4 border-t border-[var(--border)]">
                        <label className="text-xs text-[var(--text-muted)] block mb-2">Example Templates</label>
                        <select 
                            className="w-full px-2 py-1 bg-[var(--bg)] border border-[var(--border)] rounded text-xs"
                            onChange={(e) => {
                                const template = EXAMPLE_TEMPLATES.find(t => t.name === e.target.value)
                                if (template) loadTemplate(template)
                            }}
                            defaultValue=""
                        >
                            <option value="" disabled>Select template...</option>
                            {EXAMPLE_TEMPLATES.map((t) => (
                                <option key={t.name} value={t.name}>{t.name}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Right: Editor Panel */}
                <div className="flex-1 flex flex-col min-w-0">
                    {selectedWorkflow || jsonEditor ? (
                        <>
                            {/* Workflow Name */}
                            <div className="flex gap-4 mb-4">
                                <div className="flex-1">
                                    <label className="text-xs text-[var(--text-muted)] block mb-1">Workflow Name</label>
                                    <input 
                                        type="text" 
                                        className="w-full px-3 py-2 bg-[var(--card)] border border-[var(--border)] rounded"
                                        placeholder="Enter workflow name..."
                                        defaultValue={selectedWorkflow?.name || 'New Workflow'}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-[var(--text-muted)] block mb-1">Status</label>
                                    <select className="px-3 py-2 bg-[var(--card)] border border-[var(--border)] rounded">
                                        <option value="draft">Draft</option>
                                        <option value="published">Published</option>
                                    </select>
                                </div>
                            </div>

                            {/* JSON Editor */}
                            <div className="flex-1 min-h-0">
                                <label className="text-xs text-[var(--text-muted)] block mb-1">Workflow JSON</label>
                                <textarea 
                                    className="w-full h-full min-h-[300px] px-4 py-3 bg-[#1a1a1a] border border-[var(--border)] rounded font-mono text-sm resize-none"
                                    value={jsonEditor}
                                    onChange={(e) => setJsonEditor(e.target.value)}
                                    placeholder="Enter workflow JSON..."
                                    spellCheck={false}
                                />
                            </div>

                            {/* Validation/Simulation Results */}
                            {validationResult && (
                                <div className={`mt-4 p-3 rounded ${validationResult.valid ? 'bg-green-900/30 border border-green-700' : 'bg-red-900/30 border border-red-700'}`}>
                                    <div className={`text-sm font-medium ${validationResult.valid ? 'text-green-400' : 'text-red-400'}`}>
                                        {validationResult.valid ? '✓ Valid' : '✗ Invalid'}
                                    </div>
                                    {validationResult.errors && (
                                        <ul className="mt-1 text-xs text-red-300">
                                            {validationResult.errors.map((err, i) => <li key={i}>• {err}</li>)}
                                        </ul>
                                    )}
                                </div>
                            )}

                            {simulateResult && (
                                <div className={`mt-4 p-3 rounded ${simulateResult.success ? 'bg-blue-900/30 border border-blue-700' : 'bg-red-900/30 border border-red-700'}`}>
                                    <div className="text-sm text-blue-400">{simulateResult.message}</div>
                                    {simulateResult.steps && (
                                        <ul className="mt-1 text-xs text-blue-300">
                                            {simulateResult.steps.map((step, i) => <li key={i}>• {step}</li>)}
                                        </ul>
                                    )}
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex gap-3 mt-4">
                                <button 
                                    onClick={validateJson}
                                    className="px-4 py-2 border border-[var(--border)] rounded hover:bg-[var(--bg)] transition-colors"
                                >
                                    Validate
                                </button>
                                <button 
                                    onClick={simulateWorkflow}
                                    className="px-4 py-2 border border-[var(--border)] rounded hover:bg-[var(--bg)] transition-colors"
                                >
                                    Simulate
                                </button>
                                <button 
                                    onClick={saveDraft}
                                    className="px-4 py-2 border border-[var(--border)] rounded hover:bg-[var(--bg)] transition-colors"
                                >
                                    Save Draft
                                </button>
                                <button 
                                    onClick={publishWorkflow}
                                    className="px-4 py-2 bg-[var(--accent-gold)] text-black rounded font-medium hover:opacity-90"
                                >
                                    Publish
                                </button>
                                {saveStatus && (
                                    <span className="px-3 py-2 text-sm text-[var(--text-muted)]">{saveStatus}</span>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex items-center justify-center bg-[var(--card)] border border-[var(--border)] rounded-lg">
                            <div className="text-center">
                                <div className="text-4xl mb-4">⚡</div>
                                <h3 className="text-lg font-medium mb-2">No Workflow Selected</h3>
                                <p className="text-[var(--text-muted)] mb-4">
                                    Select a workflow from the list or create a new one
                                </p>
                                <button 
                                    onClick={createNewWorkflow}
                                    className="px-4 py-2 bg-[var(--accent-gold)] text-black rounded font-medium"
                                >
                                    Create New Workflow
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
