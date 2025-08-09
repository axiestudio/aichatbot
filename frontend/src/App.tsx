import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AxieStudioLanding from './pages/AxieStudioLanding'
import ChatInterface from './pages/ChatInterface'
import AdminDashboard from './pages/AdminDashboard'
import AdminLogin from './pages/AdminLogin'
import SuperAdminDashboard from './pages/SuperAdminDashboard'
import SuperAdminLogin from './pages/SuperAdminLogin'
import PublicNavigation from './components/PublicNavigation'
import { useAuthStore } from './stores/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()
  const location = useLocation()

  // Check if user is super admin
  const isSuperAdmin = localStorage.getItem('superAdminToken')

  // Show public navigation on public pages
  const showPublicNav = ['/', '/chat'].includes(location.pathname) || location.pathname.startsWith('/chat/')

  return (
    <div className="min-h-screen bg-gray-50">
      {showPublicNav && <PublicNavigation />}
      <Routes>
        {/* Public chat interface - embeddable */}
        <Route path="/chat" element={<ChatInterface />} />
        <Route path="/chat/:configId" element={<ChatInterface />} />

        {/* Admin routes */}
        <Route
          path="/admin/login"
          element={isAuthenticated ? <Navigate to="/admin" /> : <AdminLogin />}
        />
        <Route
          path="/admin/*"
          element={isAuthenticated ? <AdminDashboard /> : <Navigate to="/admin/login" />}
        />

        {/* Super Admin routes */}
        <Route
          path="/super-admin/login"
          element={isSuperAdmin ? <Navigate to="/super-admin" /> : <SuperAdminLogin />}
        />
        <Route
          path="/super-admin/*"
          element={isSuperAdmin ? <SuperAdminDashboard /> : <Navigate to="/super-admin/login" />}
        />

        {/* Landing page - New Axie Studio branded landing */}
        <Route path="/" element={<AxieStudioLanding />} />

        {/* Old landing page for reference */}
        <Route path="/old-landing" element={<LandingPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  )
}

export default App
