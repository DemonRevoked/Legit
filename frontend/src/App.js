import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import SessionList from './components/SessionList';
import SessionDetail from './components/SessionDetail';
import LoginPage from './pages/LoginPage';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import './styles/App.css';

function App() {
  // Opt-in to future v7 behavior for React Router to resolve console warnings.
  const future = { v7_startTransition: true, v7_relativeSplatPath: true };

  return (
    <Router future={future}>
      <AuthProvider>
        <div className="app-container">
          <Navigation />
          <main className="content">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={<ProtectedRoute><SessionList /></ProtectedRoute>} />
              <Route path="/sessions/:id" element={<ProtectedRoute><SessionDetail /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </Router>
  );
}

// A separate component to render navigation only when authenticated
function Navigation() {
  const { token, logout } = useAuth();
  const location = useLocation();

  // Don't show navigation on the login page
  if (!token || location.pathname === '/login') {
    return null;
  }

  return (
    <nav className="main-nav">
      <ul>
        <li><span className="nav-title">SSH Honeypot Monitor</span></li>
      </ul>
      <button onClick={logout} className="logout-button">Logout</button>
    </nav>
  );
}

export default App;
