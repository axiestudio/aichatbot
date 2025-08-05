import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LandingPage from '../pages/LandingPage';

const renderLandingPage = () => {
  return render(
    <BrowserRouter>
      <LandingPage />
    </BrowserRouter>
  );
};

describe('LandingPage', () => {
  it('renders main heading', () => {
    renderLandingPage();
    expect(screen.getByText(/Enterprise-Grade/i)).toBeInTheDocument();
    expect(screen.getByText(/AI Chatbot Platform/i)).toBeInTheDocument();
  });

  it('renders key features section', () => {
    renderLandingPage();
    expect(screen.getByText(/Why Choose Our Platform/i)).toBeInTheDocument();
    expect(screen.getByText(/Intelligent Conversations/i)).toBeInTheDocument();
    expect(screen.getByText(/Lightning Fast/i)).toBeInTheDocument();
    expect(screen.getByText(/Enterprise Security/i)).toBeInTheDocument();
  });

  it('renders performance stats', () => {
    renderLandingPage();
    expect(screen.getByText('99.9%')).toBeInTheDocument();
    expect(screen.getByText('Uptime')).toBeInTheDocument();
    expect(screen.getByText('<200ms')).toBeInTheDocument();
    expect(screen.getByText('Response Time')).toBeInTheDocument();
  });

  it('renders technical specifications', () => {
    renderLandingPage();
    expect(screen.getByText(/Enterprise Architecture/i)).toBeInTheDocument();
    expect(screen.getByText(/React 18 \+ TypeScript/i)).toBeInTheDocument();
    expect(screen.getByText(/FastAPI \+ Python/i)).toBeInTheDocument();
  });

  it('renders testimonials section', () => {
    renderLandingPage();
    expect(screen.getByText(/Trusted by Industry Leaders/i)).toBeInTheDocument();
    expect(screen.getByText(/Sarah Chen/i)).toBeInTheDocument();
    expect(screen.getByText(/CTO, TechCorp/i)).toBeInTheDocument();
  });

  it('renders call-to-action buttons', () => {
    renderLandingPage();
    const tryDemoButtons = screen.getAllByText(/Try.*Demo/i);
    const adminButtons = screen.getAllByText(/Admin/i);
    
    expect(tryDemoButtons.length).toBeGreaterThan(0);
    expect(adminButtons.length).toBeGreaterThan(0);
  });

  it('renders footer', () => {
    renderLandingPage();
    expect(screen.getByText(/Enterprise AI Chatbot Platform/i)).toBeInTheDocument();
    expect(screen.getByText(/Built with ❤️ by DevOps Engineering Team/i)).toBeInTheDocument();
    expect(screen.getByText(/© 2024 All rights reserved/i)).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    renderLandingPage();
    const mainHeading = screen.getByRole('heading', { level: 1 });
    expect(mainHeading).toBeInTheDocument();
    
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
