import React from 'react';
import { Link } from 'react-router-dom';

export default function PortalKnowledgeBase() {
  return (
    <div className="min-h-screen bg-[var(--atum-bg)] text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Knowledge Base</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3 text-[var(--atum-accent-gold)]">Getting Started</h3>
            <p className="text-[var(--atum-text-1)]">Learn the basics of using our platform</p>
          </div>
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3 text-[var(--atum-accent-gold)]">FAQs</h3>
            <p className="text-[var(--atum-text-1)]">Frequently asked questions</p>
          </div>
          <div className="glass-panel rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-3 text-[var(--atum-accent-gold)]">Troubleshooting</h3>
            <p className="text-[var(--atum-text-1)]">Common issues and solutions</p>
          </div>
        </div>
      </div>
    </div>
  );
}
