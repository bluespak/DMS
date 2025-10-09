import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSwitch, updateSwitch, checkIn } from '../services/api';
import { useAuth } from '../utils/AuthContext';

function SwitchDetails() {
  const { id } = useParams();
  const [switchData, setSwitchData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchSwitch();
  }, [id, user, navigate]);

  const fetchSwitch = async () => {
    try {
      const response = await getSwitch(id);
      setSwitchData(response.data);
    } catch (err) {
      setError('Failed to load switch details');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    try {
      await checkIn(id);
      fetchSwitch();
    } catch (err) {
      alert('Failed to check in: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleToggleActive = async () => {
    try {
      await updateSwitch(id, { is_active: !switchData.is_active });
      fetchSwitch();
    } catch (err) {
      alert('Failed to update switch');
    }
  };

  const getDaysUntilTrigger = () => {
    if (!switchData) return 0;
    const lastCheckInDate = new Date(switchData.last_check_in);
    const deadline = new Date(
      lastCheckInDate.getTime() + switchData.check_in_interval_days * 24 * 60 * 60 * 1000
    );
    const now = new Date();
    const daysLeft = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
    return daysLeft;
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error || !switchData) {
    return (
      <div className="error-container">
        <div className="error-message">{error || 'Switch not found'}</div>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const daysLeft = getDaysUntilTrigger();
  const isUrgent = daysLeft <= 2 && !switchData.is_triggered;

  return (
    <div className="switch-details">
      <div className="details-header">
        <h1>{switchData.name}</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
            Back to Dashboard
          </button>
        </div>
      </div>

      <div className="details-content">
        <div className="info-section">
          <h2>Switch Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Status:</label>
              <span>
                {switchData.is_triggered ? (
                  <span className="badge badge-danger">Triggered</span>
                ) : switchData.is_active ? (
                  <span className="badge badge-success">Active</span>
                ) : (
                  <span className="badge badge-secondary">Inactive</span>
                )}
              </span>
            </div>
            <div className="info-item">
              <label>Check-in Interval:</label>
              <span>{switchData.check_in_interval_days} days</span>
            </div>
            <div className="info-item">
              <label>Last Check-in:</label>
              <span>{new Date(switchData.last_check_in).toLocaleString()}</span>
            </div>
            {!switchData.is_triggered && (
              <div className="info-item">
                <label>Days until trigger:</label>
                <span className={isUrgent ? 'urgent-text' : ''}>{daysLeft} days</span>
              </div>
            )}
            {switchData.is_triggered && (
              <div className="info-item">
                <label>Triggered at:</label>
                <span>{new Date(switchData.triggered_at).toLocaleString()}</span>
              </div>
            )}
            <div className="info-item">
              <label>Created:</label>
              <span>{new Date(switchData.created_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="action-buttons">
            {!switchData.is_triggered && switchData.is_active && (
              <button onClick={handleCheckIn} className="btn btn-success">
                Check In Now
              </button>
            )}
            {!switchData.is_triggered && (
              <button onClick={handleToggleActive} className="btn btn-secondary">
                {switchData.is_active ? 'Deactivate' : 'Activate'}
              </button>
            )}
          </div>
        </div>

        <div className="messages-section">
          <h2>Messages ({switchData.messages.length})</h2>
          {switchData.messages.map((message, index) => (
            <div key={message.id} className="message-detail-card">
              <div className="message-detail-header">
                <h3>Message {index + 1}</h3>
                {message.is_sent && (
                  <span className="badge badge-success">Sent</span>
                )}
              </div>
              <div className="message-detail-content">
                <div className="message-field">
                  <label>Recipient:</label>
                  <span>{message.recipient_email}</span>
                </div>
                <div className="message-field">
                  <label>Subject:</label>
                  <span>{message.subject}</span>
                </div>
                <div className="message-field">
                  <label>Body:</label>
                  <pre>{message.body}</pre>
                </div>
                {message.is_sent && (
                  <div className="message-field">
                    <label>Sent at:</label>
                    <span>{new Date(message.sent_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SwitchDetails;
