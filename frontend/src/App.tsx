import { Routes, Route, Navigate } from 'react-router-dom'
import ChatInterface from './pages/ChatInterface'
import AdminDashboard from './pages/AdminDashboard'
import AdminLogin from './pages/AdminLogin'
import { useAuthStore } from './stores/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50">
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
        
        {/* Default redirects */}
        <Route path="/" element={<Navigate to="/chat" />} />
        <Route path="*" element={<Navigate to="/chat" />} />
      </Routes>
    </div>
  )
}

export default App
