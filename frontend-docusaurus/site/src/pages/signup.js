/**
 * Signup page - User registration with background questionnaire
 */
import React from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { SignupForm } from '../components/AuthForms';
import { useAuth } from '../contexts/AuthContext';

export default function SignupPage() {
  const history = useHistory();
  const { isAuthenticated, loading } = useAuth();

  // Redirect if already logged in
  React.useEffect(() => {
    if (!loading && isAuthenticated) {
      history.push('/');
    }
  }, [isAuthenticated, loading, history]);

  const handleSuccess = () => {
    history.push('/');
  };

  const handleSwitchToLogin = () => {
    history.push('/signin');
  };

  // Show loading while checking auth
  if (loading) {
    return (
      <Layout title="Create Account">
        <main style={{
          padding: '48px 24px',
          minHeight: 'calc(100vh - 60px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Loading...</div>
          </div>
        </main>
      </Layout>
    );
  }

  return (
    <Layout
      title="Create Account"
      description="Create your account to start learning Physical AI & Humanoid Robotics"
    >
      <main style={{
        padding: '48px 24px',
        minHeight: 'calc(100vh - 60px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--ifm-background-color)'
      }}>
        <SignupForm
          onSuccess={handleSuccess}
          onSwitchToLogin={handleSwitchToLogin}
        />
      </main>
    </Layout>
  );
}
