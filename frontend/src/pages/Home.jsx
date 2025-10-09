import { Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';

function Home() {
  const { user } = useAuth();

  return (
    <div className="home">
      <div className="hero">
        <h1>Dead Man's Switch</h1>
        <p className="subtitle">
          Peace of mind for you and your loved ones
        </p>
        <p className="description">
          A Dead Man's Switch ensures that important messages are delivered if you
          fail to check in regularly. Perfect for emergency communications, password
          recovery, or final messages to loved ones.
        </p>
        <div className="cta-buttons">
          {user ? (
            <Link to="/dashboard" className="btn btn-primary">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary">
                Get Started
              </Link>
              <Link to="/login" className="btn btn-secondary">
                Login
              </Link>
            </>
          )}
        </div>
      </div>

      <div className="features">
        <h2>How It Works</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>Create a Switch</h3>
            <p>
              Set up a dead man's switch with messages to be sent and a check-in
              interval.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⏰</div>
            <h3>Check In Regularly</h3>
            <p>
              Check in before your deadline to prevent messages from being sent.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📧</div>
            <h3>Automatic Delivery</h3>
            <p>
              If you miss a check-in, your messages are automatically delivered to
              recipients.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
