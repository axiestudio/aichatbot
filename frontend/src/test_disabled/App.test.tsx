import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

// Mock the auth store
vi.mock('../stores/authStore', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

// Mock components to avoid complex rendering
vi.mock('../pages/LandingPage', () => ({
  default: () => <div data-testid="landing-page">Landing Page</div>,
}));

vi.mock('../pages/ChatInterface', () => ({
  default: () => <div data-testid="chat-interface">Chat Interface</div>,
}));

vi.mock('../pages/AdminDashboard', () => ({
  default: () => <div data-testid="admin-dashboard">Admin Dashboard</div>,
}));

vi.mock('../pages/AdminLogin', () => ({
  default: () => <div data-testid="admin-login">Admin Login</div>,
}));

vi.mock('../components/PublicNavigation', () => ({
  default: () => <div data-testid="public-navigation">Public Navigation</div>,
}));

const renderApp = (initialRoute = '/') => {
  window.history.pushState({}, 'Test page', initialRoute);
  
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
};

describe('App', () => {
  it('renders landing page on root route', () => {
    renderApp('/');
    expect(screen.getByTestId('landing-page')).toBeInTheDocument();
    expect(screen.getByTestId('public-navigation')).toBeInTheDocument();
  });

  it('renders chat interface on /chat route', () => {
    renderApp('/chat');
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    expect(screen.getByTestId('public-navigation')).toBeInTheDocument();
  });

  it('renders admin login on /admin/login route', () => {
    renderApp('/admin/login');
    expect(screen.getByTestId('admin-login')).toBeInTheDocument();
    expect(screen.queryByTestId('public-navigation')).not.toBeInTheDocument();
  });

  it('redirects unknown routes to home', () => {
    renderApp('/unknown-route');
    expect(screen.getByTestId('landing-page')).toBeInTheDocument();
  });
});
