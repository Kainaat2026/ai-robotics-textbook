/**
 * Progress page - Shows user's learning progress dashboard
 */
import React from 'react';
import Layout from '@theme/Layout';
import ProgressDashboard from '../components/ProgressDashboard';

export default function ProgressPage() {
  return (
    <Layout
      title="My Progress"
      description="Track your learning progress through the Physical AI & Humanoid Robotics curriculum"
    >
      <main style={{ padding: '24px 0' }}>
        <ProgressDashboard />
      </main>
    </Layout>
  );
}
