/**
 * Signin page - User login
 */
import React from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { SigninForm } from '../components/AuthForms';
import { useAuth } from '../contexts/AuthContext';

export default function SigninPage() {
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

  const handleSwitchToSignup = () => {
    history.push('/signup');
  };

  // Show loading while checking auth
  if (loading) {
    return (
      <Layout title="Sign In">
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
      title="Sign In"
      description="Sign in to continue your learning journey in Physical AI & Humanoid Robotics"
    >
      <main style={{
        padding: '48px 24px',
        minHeight: 'calc(100vh - 60px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--ifm-background-color)'
      }}>
        <SigninForm
          onSuccess={handleSuccess}
          onSwitchToSignup={handleSwitchToSignup}
        />
      </main>
    </Layout>
  );
}
