import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSwitch } from '../services/api';
import { useAuth } from '../utils/AuthContext';

function CreateSwitch() {
  const [name, setName] = useState('');
  const [checkInIntervalDays, setCheckInIntervalDays] = useState(7);
  const [messages, setMessages] = useState([
    { recipient_email: '', subject: '', body: '' },
  ]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  if (!user) {
    navigate('/login');
    return null;
  }

  const handleAddMessage = () => {
    setMessages([...messages, { recipient_email: '', subject: '', body: '' }]);
  };

  const handleRemoveMessage = (index) => {
    const newMessages = messages.filter((_, i) => i !== index);
    setMessages(newMessages);
  };

  const handleMessageChange = (index, field, value) => {
    const newMessages = [...messages];
    newMessages[index][field] = value;
    setMessages(newMessages);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate
    if (!name.trim()) {
      setError('Switch name is required');
      return;
    }

    if (checkInIntervalDays < 1) {
      setError('Check-in interval must be at least 1 day');
      return;
    }

    if (messages.length === 0) {
      setError('At least one message is required');
      return;
    }

    for (const msg of messages) {
      if (!msg.recipient_email || !msg.subject || !msg.body) {
        setError('All message fields are required');
        return;
      }
    }

    setLoading(true);

    try {
      await createSwitch({
        name,
        check_in_interval_days: parseInt(checkInIntervalDays),
        messages,
      });
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create switch');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-switch-container">
      <div className="create-switch-card">
        <h2>Create New Switch</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Switch Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g., Emergency Contact"
            />
          </div>

          <div className="form-group">
            <label htmlFor="interval">Check-in Interval (days)</label>
            <input
              type="number"
              id="interval"
              value={checkInIntervalDays}
              onChange={(e) => setCheckInIntervalDays(e.target.value)}
              required
              min="1"
            />
            <small>
              You must check in every {checkInIntervalDays} days to prevent messages from being sent.
            </small>
          </div>

          <div className="messages-section">
            <h3>Messages</h3>
            {messages.map((message, index) => (
              <div key={index} className="message-card">
                <div className="message-header">
                  <h4>Message {index + 1}</h4>
                  {messages.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveMessage(index)}
                      className="btn btn-danger btn-small"
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div className="form-group">
                  <label>Recipient Email</label>
                  <input
                    type="email"
                    value={message.recipient_email}
                    onChange={(e) =>
                      handleMessageChange(index, 'recipient_email', e.target.value)
                    }
                    required
                    placeholder="recipient@example.com"
                  />
                </div>

                <div className="form-group">
                  <label>Subject</label>
                  <input
                    type="text"
                    value={message.subject}
                    onChange={(e) =>
                      handleMessageChange(index, 'subject', e.target.value)
                    }
                    required
                    placeholder="Message subject"
                  />
                </div>

                <div className="form-group">
                  <label>Message Body</label>
                  <textarea
                    value={message.body}
                    onChange={(e) =>
                      handleMessageChange(index, 'body', e.target.value)
                    }
                    required
                    rows="6"
                    placeholder="Your message content..."
                  />
                </div>
              </div>
            ))}

            <button
              type="button"
              onClick={handleAddMessage}
              className="btn btn-secondary"
            >
              Add Another Message
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Switch'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateSwitch;
