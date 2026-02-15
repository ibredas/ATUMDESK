import React, { useState } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { ShieldCheck, Key, Network, Save } from 'lucide-react'

export default function AdminSecurity() {
    const [settings, setSettings] = useState({
        require_2fa: false,
        password_min_length: 12,
        password_require_uppercase: true,
        password_require_lowercase: true,
        password_require_digit: true,
        password_require_special: true,
        ip_allowlist_enabled: false,
        allowed_ips: []
    })

    return (
        <PageShell title="Security Settings" icon={ShieldCheck}>
            <GlassCard className="mb-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Key size={18} className="text-[var(--atum-accent-gold)]" /> Two-Factor Authentication (2FA)</h2>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="font-medium">Require 2FA for all users</p>
                        <p className="text-sm text-[var(--atum-text-muted)]">When enabled, all users must set up TOTP 2FA</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" checked={settings.require_2fa} onChange={(e) => setSettings({ ...settings, require_2fa: e.target.checked })} />
                        <div className="w-11 h-6 bg-[var(--atum-surface-2)] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                </div>
            </GlassCard>

            <GlassCard className="mb-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><ShieldCheck size={18} className="text-[var(--atum-accent-gold)]" /> Password Policy</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Minimum Length</label>
                        <input type="number" className="atum-input w-20" value={settings.password_min_length} onChange={(e) => setSettings({ ...settings, password_min_length: parseInt(e.target.value) })} />
                    </div>
                    {[
                        ['password_require_uppercase', 'Require Uppercase'],
                        ['password_require_lowercase', 'Require Lowercase'],
                        ['password_require_digit', 'Require Numbers'],
                        ['password_require_special', 'Require Special Characters'],
                    ].map(([key, label]) => (
                        <div key={key} className="flex items-center justify-between">
                            <label className="font-medium">{label}</label>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" className="sr-only peer" checked={settings[key]} onChange={(e) => setSettings({ ...settings, [key]: e.target.checked })} />
                                <div className="w-11 h-6 bg-[var(--atum-surface-2)] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                            </label>
                        </div>
                    ))}
                </div>
            </GlassCard>

            <GlassCard className="mb-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Network size={18} className="text-[var(--atum-accent-gold)]" /> IP Restrictions</h2>
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <p className="font-medium">Enable IP Allowlist</p>
                        <p className="text-sm text-[var(--atum-text-muted)]">Restrict access to specific IP addresses</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" checked={settings.ip_allowlist_enabled} onChange={(e) => setSettings({ ...settings, ip_allowlist_enabled: e.target.checked })} />
                        <div className="w-11 h-6 bg-[var(--atum-surface-2)] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                </div>
                {settings.ip_allowlist_enabled && (
                    <textarea className="atum-input w-full" rows={4} placeholder="Enter IP addresses, one per line (e.g., 192.168.1.0/24)" defaultValue={settings.allowed_ips.join('\n')} />
                )}
            </GlassCard>

            <button className="btn-gold flex items-center gap-2"><Save size={16} /> Save Settings</button>
        </PageShell>
    )
}
