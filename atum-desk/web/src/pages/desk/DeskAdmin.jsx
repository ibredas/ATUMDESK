import React from 'react';

export default function DeskAdmin() {
  return (
    <div className="min-h-screen bg-[var(--bg-0)] text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3">Users</h3>
            <p className="text-[var(--text-1)]">Manage user accounts</p>
          </div>
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3">Organizations</h3>
            <p className="text-[var(--text-1)]">Manage organizations</p>
          </div>
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3">Settings</h3>
            <p className="text-[var(--text-1)]">System configuration</p>
          </div>
        </div>
      </div>
    </div>
  );
}
