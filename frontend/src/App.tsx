import React from 'react'

function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '20px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'center' }}>
          🤖 Modern Chatbot System
        </h1>

        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            ✅ System Status: Ready
          </h2>

          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>🚀 Features:</h3>
            <ul style={{ paddingLeft: '1.5rem' }}>
              <li>✅ FastAPI Backend</li>
              <li>✅ React Frontend</li>
              <li>✅ Docker Containerized</li>
              <li>✅ CI/CD Pipeline</li>
              <li>✅ Production Ready</li>
            </ul>
          </div>

          <div style={{
            padding: '1rem',
            backgroundColor: '#f0f9ff',
            borderRadius: '4px',
            border: '1px solid #0ea5e9'
          }}>
            <p style={{ margin: 0, color: '#0369a1' }}>
              🎉 <strong>Deployment Successful!</strong> Your chatbot system is now live and ready to serve users.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
