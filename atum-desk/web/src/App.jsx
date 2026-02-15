import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import DeskLayout from './components/Layout/DeskLayout'

// Landing
import LandingPage from './pages/LandingPage'
import OverviewPage from './pages/landing/OverviewPage'
import ComparePage from './pages/landing/ComparePage'
import SecurityPage from './pages/landing/SecurityPage'
import AIPage from './pages/landing/AIPage'
import PricingPage from './pages/landing/PricingPage'
import DemoPage from './pages/landing/DemoPage'

// Portal (Customer)
import PortalLogin from './pages/portal/PortalLogin'
import PortalTickets from './pages/portal/PortalTickets'
import PortalTicketNew from './pages/portal/PortalTicketNew'
import PortalTicketDetail from './pages/portal/PortalTicketDetail'

// Desk (Staff)
import DeskLogin from './pages/desk/DeskLogin'
import DeskDashboard from './pages/desk/DeskDashboard'
import DeskInbox from './pages/desk/DeskInbox'
import DeskTicketDetail from './pages/desk/DeskTicketDetail'
import DeskKnowledgeBase from './pages/desk/DeskKnowledgeBase'
import DeskArticleEditor from './pages/desk/DeskArticleEditor'
import DeskProblemList from './pages/desk/DeskProblemList'
import DeskChangeList from './pages/desk/DeskChangeList'
import DeskAssetList from './pages/desk/DeskAssetList'

// NEW: Enhanced Pages
import DeskMonitoring from './pages/desk/DeskMonitoring'
import DeskPlaybooks from './pages/desk/DeskPlaybooks'
import DeskAuditLog from './pages/desk/DeskAuditLog'
import DeskWorkflows from './pages/desk/DeskWorkflows'
import DeskSLAAlerts from './pages/desk/DeskSLAAlerts'
import AdminSecurity from './pages/admin/AdminSecurity'
import AdminDashboard from './pages/desk/AdminDashboard'
import AdminJobQueue from './pages/desk/admin/AdminJobQueue'
import AdminIPRestrictions from './pages/desk/admin/AdminIPRestrictions'
import AdminAIControl from './pages/desk/admin/AdminAIControl'
import AdminFormsStudio from './pages/desk/admin/AdminFormsStudio'
import AdminOrgManagement from './pages/desk/admin/AdminOrgManagement'

// AI Pages
import AIAnalyticsHub from './pages/desk/ai/AIAnalyticsHub'
import AISmartInsights from './pages/desk/ai/AISmartInsights'
import AIAgentAssist from './pages/desk/ai/AIAgentAssist'
import AISLAPrediction from './pages/desk/ai/AISLAPrediction'

// NEW: Security & Governance Pages
import DeskKBSuggestions from './pages/desk/DeskKBSuggestions'
import DeskIncidents from './pages/desk/DeskIncidents'
import DeskPostmortems from './pages/desk/DeskPostmortems'
import AdminPolicyCenter from './pages/admin/AdminPolicyCenter'

// Portal Pages
import PortalHelpCenter from './pages/portal/PortalHelpCenter'

// Command Palette
import CommandPalette from './components/CommandPalette'

function App() {
  return (
    <>
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#0B1020',
          color: '#fff',
          border: '1px solid rgba(212,175,55,0.15)',
          fontSize: '13px',
          borderRadius: '8px',
        }
      }} />

      {/* Command Palette — global Ctrl+K */}
      <CommandPalette />

      <Routes>
        {/* ── Landing / Marketing ── */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/compare/legacy-itsm" element={<ComparePage />} />
        <Route path="/security" element={<SecurityPage />} />
        <Route path="/ai" element={<AIPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/demo" element={<DemoPage />} />

        {/* ── Portal (Customer) ── */}
        <Route path="/portal" element={<Navigate to="/portal/login" replace />} />
        <Route path="/portal/login" element={<PortalLogin />} />
        <Route path="/portal/tickets" element={<PortalTickets />} />
        <Route path="/portal/tickets/new" element={<PortalTicketNew />} />
        <Route path="/portal/tickets/:id" element={<PortalTicketDetail />} />
        <Route path="/portal/help" element={<PortalHelpCenter />} />

        {/* ── Desk (Staff) - Auth Routes ── */}
        <Route path="/desk" element={<Navigate to="/desk/login" replace />} />
        <Route path="/desk/login" element={<DeskLogin />} />

        {/* ── Desk (Protected Layout) ── */}
        <Route element={<DeskLayout />}>
          <Route path="/desk/dashboard" element={<DeskDashboard />} />
          <Route path="/desk/inbox" element={<DeskInbox />} />
          <Route path="/desk/tickets/:id" element={<DeskTicketDetail />} />

          {/* KB */}
          <Route path="/desk/kb" element={<DeskKnowledgeBase />} />
          <Route path="/desk/kb/new" element={<DeskArticleEditor />} />
          <Route path="/desk/kb/:id" element={<DeskArticleEditor />} />

          {/* Phase 2 Modules */}
          <Route path="/desk/problems" element={<DeskProblemList />} />
          <Route path="/desk/changes" element={<DeskChangeList />} />
          <Route path="/desk/assets" element={<DeskAssetList />} />

          {/* Operations & Governance */}
          <Route path="/desk/monitoring" element={<DeskMonitoring />} />
          <Route path="/desk/workflows" element={<DeskWorkflows />} />
          <Route path="/desk/playbooks" element={<DeskPlaybooks />} />
          <Route path="/desk/audit" element={<DeskAuditLog />} />
          <Route path="/desk/sla-alerts" element={<DeskSLAAlerts />} />
          <Route path="/desk/incidents" element={<DeskIncidents />} />
          <Route path="/desk/postmortems" element={<DeskPostmortems />} />

          {/* Admin */}
          <Route path="/desk/admin/security" element={<AdminSecurity />} />
          <Route path="/desk/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/desk/admin/queues" element={<AdminJobQueue />} />
          <Route path="/desk/admin/ip-restrictions" element={<AdminIPRestrictions />} />
          <Route path="/desk/admin/ai" element={<AdminAIControl />} />
          <Route path="/desk/admin/forms" element={<AdminFormsStudio />} />
          <Route path="/desk/admin/org" element={<AdminOrgManagement />} />
          <Route path="/desk/admin/policies" element={<AdminPolicyCenter />} />

          {/* AI */}
          <Route path="/desk/ai/analytics" element={<AIAnalyticsHub />} />
          <Route path="/desk/ai/insights" element={<AISmartInsights />} />
          <Route path="/desk/ai/assist" element={<AIAgentAssist />} />
          <Route path="/desk/ai/sla" element={<AISLAPrediction />} />

          <Route path="/desk/kb-suggestions" element={<DeskKBSuggestions />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
