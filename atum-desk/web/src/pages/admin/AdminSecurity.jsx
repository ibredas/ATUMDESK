import React, { useState, useEffect } from 'react'

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
    const [loading, setLoading] = useState(false)

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">Security Settings</h1>
            
            {/* 2FA Settings */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-6 mb-6">
                <h2 className="text-lg font-semibold mb-4">Two-Factor Authentication (2FA)</h2>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="font-medium">Require 2FA for all users</p>
                        <p className="text-sm text-[var(--text-muted)]">
                            When enabled, all users must set up TOTP 2FA
                        </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                            type="checkbox" 
                            className="sr-only peer"
                            checked={settings.require_2fa}
                            onChange={(e) => setSettings({...settings, require_2fa: e.target.checked})}
                        />
                        <div className="w-11 h-6 bg-[var(--bg)] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                </div>
            </div>

            {/* Password Policy */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-6 mb-6">
                <h2 className="text-lg font-semibold mb-4">Password Policy</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Minimum Length</label>
                        <input 
                            type="number" 
                            className="w-20 px-3 py-2 bg-[var(--bg)] border border-[var(--border)] rounded"
                            value={settings.password_min_length}
                            onChange={(e) => setSettings({...settings, password_min_length: parseInt(e.target.value)})}
                        />
                    </div>
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Require Uppercase</label>
                        <input 
                            type="checkbox" 
                            checked={settings.password_require_uppercase}
                            onChange={(e) => setSettings({...settings, password_require_uppercase: e.target.checked})}
                        />
                    </div>
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Require Lowercase</label>
                        <input 
                            type="checkbox" 
                            checked={settings.password_require_lowercase}
                            onChange={(e) => setSettings({...settings, password_require_lowercase: e.target.checked})}
                        />
                    </div>
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Require Numbers</label>
                        <input 
                            type="checkbox" 
                            checked={settings.password_require_digit}
                            onChange={(e) => setSettings({...settings, password_require_digit: e.target.checked})}
                        />
                    </div>
                    <div className="flex items-center justify-between">
                        <label className="font-medium">Require Special Characters</label>
                        <input 
                            type="checkbox" 
                            checked={settings.password_require_special}
                            onChange={(e) => setSettings({...settings, password_require_special: e.target.checked})}
                        />
                    </div>
                </div>
            </div>

            {/* IP Restrictions */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-6 mb-6">
                <h2 className="text-lg font-semibold mb-4">IP Restrictions</h2>
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <p className="font-medium">Enable IP Allowlist</p>
                        <p className="text-sm text-[var(--text-muted)]">
                            Restrict access to specific IP addresses
                        </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                            type="checkbox" 
                            className="sr-only peer"
                            checked={settings.ip_allowlist_enabled}
                            onChange={(e) => setSettings({...settings, ip_allowlist_enabled: e.target.checked})}
                        />
                        <div className="w-11 h-6 bg-[var(--bg)] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                </div>
                {settings.ip_allowlist_enabled && (
                    <textarea
                        className="w-full px-3 py-2 bg-[var(--bg)] border border-[var(--border)] rounded"
                        rows={4}
                        placeholder="Enter IP addresses, one per line (e.g., 192.168.1.0/24)"
                        defaultValue={settings.allowed_ips.join('\n')}
                    />
                )}
            </div>

            <button className="px-6 py-2 bg-[var(--accent-gold)] text-black rounded-lg font-medium">
                Save Settings
            </button>
        </div>
    )
}
