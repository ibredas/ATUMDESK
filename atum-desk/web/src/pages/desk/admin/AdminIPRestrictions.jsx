import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { Input, Toggle } from '../../../design-system/components/Input'
import { Modal, ModalFooter } from '../../../design-system/components/Modal'
import { Shield, Plus, Info } from 'lucide-react'

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
      if (rulesRes.ok) { const data = await rulesRes.json(); setRules(data.rules || []) }
      if (settingsRes.ok) { const data = await settingsRes.json(); setGlobalEnabled(data.ip_restrictions_enabled || false) }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const columns = [
    { key: 'ip_address', header: 'IP Address / CIDR' },
    { key: 'rule_type', header: 'Type', render: (row) => <Badge variant={row.rule_type === 'allow' ? 'success' : 'error'}>{row.rule_type.toUpperCase()}</Badge> },
    { key: 'description', header: 'Description' },
    { key: 'is_active', header: 'Status', render: (row) => <Badge variant={row.is_active ? 'success' : 'default'}>{row.is_active ? 'Active' : 'Inactive'}</Badge> },
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
  ]

  const handleAddRule = async () => {
    try {
      const res = await fetch('/api/v1/admin/ip-rules', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(newRule)
      })
      if (res.ok) { setIsModalOpen(false); setNewRule({ ip_address: '', rule_type: 'allow', description: '' }); fetchData() }
    } catch (e) { console.error(e) }
  }

  const handleToggleGlobal = async () => {
    try {
      await fetch('/api/v1/admin/ip-settings', {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip_restrictions_enabled: !globalEnabled })
      })
      setGlobalEnabled(!globalEnabled)
    } catch (e) { console.error(e) }
  }

  if (loading) {
    return (
      <PageShell title="IP Restrictions" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  return (
    <PageShell
      title="IP Restrictions"
      subtitle="Manage IP allow/deny rules for admin access"
      actions={<Button onClick={() => setIsModalOpen(true)}><Plus size={14} className="mr-1" /> Add Rule</Button>}
    >
      {/* Global Toggle */}
      <GlassCard className="mb-6">
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">IP Restrictions Global Setting</h3>
              <p className="text-sm text-[var(--atum-text-muted)]">When enabled, only IPs in the allowlist can access admin endpoints</p>
            </div>
            <Toggle checked={globalEnabled} onChange={handleToggleGlobal} label={globalEnabled ? 'Enabled' : 'Disabled'} />
          </div>
        </div>
      </GlassCard>

      {/* Info Box */}
      <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
          <Info size={20} className="text-blue-400 mt-0.5" />
          <div>
            <div className="font-medium text-blue-400">How IP Restrictions Work</div>
            <ul className="text-sm text-[var(--atum-text-muted)] mt-1 space-y-1">
              <li>• Empty allowlist = Allow all (when enabled)</li>
              <li>• "deny" rules block matching IPs</li>
              <li>• Rules are evaluated top-to-bottom</li>
              <li>• Default: OFF (all IPs allowed)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Rules Table */}
      <GlassCard>
        <div className="p-6">
          <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">IP Rules</h2>
          <Table columns={columns} data={rules} emptyMessage="No IP rules configured" />
        </div>
      </GlassCard>

      {/* Add Rule Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add IP Rule" size="md">
        <div className="space-y-4">
          <Input label="IP Address / CIDR" placeholder="192.168.1.1 or 10.0.0.0/8"
            value={newRule.ip_address} onChange={(e) => setNewRule({ ...newRule, ip_address: e.target.value })} />
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--atum-text-muted)] mb-2">Rule Type</label>
            <select className="w-full px-4 py-2.5 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-lg text-[var(--atum-text)]"
              value={newRule.rule_type} onChange={(e) => setNewRule({ ...newRule, rule_type: e.target.value })}>
              <option value="allow">Allow</option>
              <option value="deny">Deny</option>
            </select>
          </div>
          <Input label="Description" placeholder="Optional description"
            value={newRule.description} onChange={(e) => setNewRule({ ...newRule, description: e.target.value })} />
        </div>
        <ModalFooter>
          <Button variant="secondary" onClick={() => setIsModalOpen(false)}>Cancel</Button>
          <Button onClick={handleAddRule}>Add Rule</Button>
        </ModalFooter>
      </Modal>
    </PageShell>
  )
}
