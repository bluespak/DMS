import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSwitches, deleteSwitch, checkIn } from '../services/api';
import { useAuth } from '../utils/AuthContext';

function Dashboard() {
  const [switches, setSwitches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchSwitches();
  }, [user, navigate]);

  const fetchSwitches = async () => {
    try {
      const response = await getSwitches();
      setSwitches(response.data);
    } catch (err) {
      setError('Failed to load switches');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (switchId) => {
    try {
      await checkIn(switchId);
      fetchSwitches();
    } catch (err) {
      alert('Failed to check in: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (switchId) => {
    if (!window.confirm('Are you sure you want to delete this switch?')) {
      return;
    }
    try {
      await deleteSwitch(switchId);
      fetchSwitches();
    } catch (err) {
      alert('Failed to delete switch');
    }
  };

  const getDaysUntilTrigger = (lastCheckIn, intervalDays) => {
    const lastCheckInDate = new Date(lastCheckIn);
    const deadline = new Date(lastCheckInDate.getTime() + intervalDays * 24 * 60 * 60 * 1000);
    const now = new Date();
    const daysLeft = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
    return daysLeft;
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>My Switches</h1>
        <button
          onClick={() => navigate('/create-switch')}
          className="btn btn-primary"
        >
          Create New Switch
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {switches.length === 0 ? (
        <div className="empty-state">
          <p>You don't have any switches yet.</p>
          <button
            onClick={() => navigate('/create-switch')}
            className="btn btn-primary"
          >
            Create Your First Switch
          </button>
        </div>
      ) : (
        <div className="switches-grid">
          {switches.map((sw) => {
            const daysLeft = getDaysUntilTrigger(sw.last_check_in, sw.check_in_interval_days);
            const isUrgent = daysLeft <= 2 && !sw.is_triggered;
            
            return (
              <div key={sw.id} className={`switch-card ${sw.is_triggered ? 'triggered' : ''} ${isUrgent ? 'urgent' : ''}`}>
                <div className="switch-header">
                  <h3>{sw.name}</h3>
                  <div className="switch-status">
                    {sw.is_triggered ? (
                      <span className="badge badge-danger">Triggered</span>
                    ) : sw.is_active ? (
                      <span className="badge badge-success">Active</span>
                    ) : (
                      <span className="badge badge-secondary">Inactive</span>
                    )}
                  </div>
                </div>
                
                <div className="switch-info">
                  <p>
                    <strong>Check-in Interval:</strong> {sw.check_in_interval_days} days
                  </p>
                  <p>
                    <strong>Last Check-in:</strong>{' '}
                    {new Date(sw.last_check_in).toLocaleString()}
                  </p>
                  {!sw.is_triggered && (
                    <p className={isUrgent ? 'urgent-text' : ''}>
                      <strong>Days until trigger:</strong> {daysLeft} days
                    </p>
                  )}
                  {sw.is_triggered && (
                    <p>
                      <strong>Triggered at:</strong>{' '}
                      {new Date(sw.triggered_at).toLocaleString()}
                    </p>
                  )}
                  <p>
                    <strong>Messages:</strong> {sw.messages.length}
                  </p>
                </div>
                
                <div className="switch-actions">
                  {!sw.is_triggered && sw.is_active && (
                    <button
                      onClick={() => handleCheckIn(sw.id)}
                      className="btn btn-success"
                    >
                      Check In
                    </button>
                  )}
                  <button
                    onClick={() => navigate(`/switch/${sw.id}`)}
                    className="btn btn-secondary"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleDelete(sw.id)}
                    className="btn btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
