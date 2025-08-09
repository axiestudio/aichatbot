import React from 'react';
import AxieHero from '../components/landing/AxieHero';
import AxieFeatures from '../components/landing/AxieFeatures';
import AxieDemo from '../components/landing/AxieDemo';
import AxieEmbedding from '../components/landing/AxieEmbedding';
import AxieStats from '../components/landing/AxieStats';
import AxieGetStarted from '../components/landing/AxieGetStarted';
import AxieFooter from '../components/landing/AxieFooter';

const AxieStudioLanding = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <AxieHero />
      <AxieFeatures />
      <AxieDemo />
      <AxieEmbedding />
      <AxieStats />
      <AxieGetStarted />
      <AxieFooter />
    </div>
  );
};

export default AxieStudioLanding;
