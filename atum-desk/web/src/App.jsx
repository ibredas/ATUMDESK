import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Landing
import LandingPage from './pages/LandingPage'

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

function App() {
  return (
    <>
      <Toaster position="top-right" toastOptions={{
        style: {
          background: '#121212',
          color: '#fff',
          border: '1px solid rgba(212,175,55,0.15)',
          fontSize: '13px',
        }
      }} />
      <Routes>
        {/* Landing */}
        <Route path="/" element={<LandingPage />} />

        {/* Portal (Customer) */}
        <Route path="/portal" element={<Navigate to="/portal/login" replace />} />
        <Route path="/portal/login" element={<PortalLogin />} />
        <Route path="/portal/tickets" element={<PortalTickets />} />
        <Route path="/portal/tickets/new" element={<PortalTicketNew />} />
        <Route path="/portal/tickets/:id" element={<PortalTicketDetail />} />

        {/* Desk (Staff) */}
        <Route path="/desk" element={<Navigate to="/desk/login" replace />} />
        <Route path="/desk/login" element={<DeskLogin />} />
        <Route path="/desk/dashboard" element={<DeskDashboard />} />
        <Route path="/desk/inbox" element={<DeskInbox />} />
        <Route path="/desk/tickets/:id" element={<DeskTicketDetail />} />
      </Routes>
    </>
  )
}

export default App
