import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { Input, Toggle } from '../../../design-system/components/Input'
import { Modal, ModalFooter } from '../../../design-system/components/Modal'

export default function AdminIPRestrictions() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [globalEnabled, setGlobalEnabled] = useState(false)
  const [newRule, setNewRule] = useState({ ip_address: '', rule_type: 'allow', description: '' })

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [rulesRes, settingsRes] = await Promise.all([
        fetch('/api/v1/admin/ip-rules', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/admin/ip-settings', { headers: { 'Authorization': `Bearer ${token}` } })
      ])
      
      if (rulesRes.ok) {
        const data = await rulesRes.json()
        setRules(data.rules || [])
      }
      
      if (settingsRes.ok) {
        const data = await settingsRes.json()
        setGlobalEnabled(data.ip_restrictions_enabled || false)
      }
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const columns = [
    { key: 'ip_address', header: 'IP Address / CIDR' },
    { key: 'rule_type', header: 'Type', render: (row) => (
      <Badge variant={row.rule_type === 'allow' ? 'success' : 'error'}>
        {row.rule_type.toUpperCase()}
      </Badge>
    )},
    { key: 'description', header: 'Description' },
    { key: 'is_active', header: 'Status', render: (row) => (
      <Badge variant={row.is_active ? 'success' : 'default'}>
        {row.is_active ? 'Active' : 'Inactive'}
      </Badge>
    )},
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
  ]

  const handleAddRule = async () => {
    try {
      const res = await fetch('/api/v1/admin/ip-rules', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newRule)
      })
      
      if (res.ok) {
        setIsModalOpen(false)
        setNewRule({ ip_address: '', rule_type: 'allow', description: '' })
        fetchData()
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleToggleGlobal = async () => {
    try {
      await fetch('/api/v1/admin/ip-settings', {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ip_restrictions_enabled: !globalEnabled })
      })
      setGlobalEnabled(!globalEnabled)
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[var(--bg-0)]">
        <DeskSidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin h-8 w-8 border-2 border-[var(--accent-gold)] border-t-transparent rounded-full"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      <DeskSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">🔐</span>
                IP Restrictions
              </h1>
              <p className="text-[var(--text-muted)] mt-1">Manage IP allow/deny rules for admin access</p>
            </div>
            <div className="flex gap-3">
              <Button onClick={() => setIsModalOpen(true)}>+ Add Rule</Button>
            </div>
          </div>

          {/* Global Toggle */}
          <div className="glass-panel rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-[var(--text-0)]">IP Restrictions Global Setting</h3>
                <p className="text-sm text-[var(--text-muted)]">When enabled, only IPs in the allowlist can access admin endpoints</p>
              </div>
              <Toggle 
                checked={globalEnabled} 
                onChange={handleToggleGlobal}
                label={globalEnabled ? 'Enabled' : 'Disabled'}
              />
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-4 mb-6">
            <div className="flex items-start gap-3">
              <span className="text-xl">ℹ️</span>
              <div>
                <div className="font-medium text-blue-400">How IP Restrictions Work</div>
                <ul className="text-sm text-[var(--text-muted)] mt-1 space-y-1">
                  <li>• Empty allowlist = Allow all (when enabled)</li>
                  <li>• "deny" rules block matching IPs</li>
                  <li>• Rules are evaluated top-to-bottom</li>
                  <li>• Default: OFF (all IPs allowed)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Rules Table */}
          <div className="glass-panel rounded-xl p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">IP Rules</h2>
            <Table columns={columns} data={rules} emptyMessage="No IP rules configured" />
          </div>

          {/* Add Rule Modal */}
          <Modal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            title="Add IP Rule"
            size="md"
          >
            <div className="space-y-4">
              <Input
                label="IP Address / CIDR"
                placeholder="192.168.1.1 or 10.0.0.0/8"
                value={newRule.ip_address}
                onChange={(e) => setNewRule({...newRule, ip_address: e.target.value})}
              />
              
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--text-2)] mb-2">
                  Rule Type
                </label>
                <select
                  className="w-full px-4 py-2.5 bg-[var(--bg-2)] border border-[var(--border)] rounded-lg text-[var(--text-0)]"
                  value={newRule.rule_type}
                  onChange={(e) => setNewRule({...newRule, rule_type: e.target.value})}
                >
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                </select>
              </div>

              <Input
                label="Description"
                placeholder="Optional description"
                value={newRule.description}
                onChange={(e) => setNewRule({...newRule, description: e.target.value})}
              />
            </div>
            
            <ModalFooter>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button onClick={handleAddRule}>Add Rule</Button>
            </ModalFooter>
          </Modal>
        </div>
      </div>
    </div>
  )
}
