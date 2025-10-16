import React, { useState } from 'react';
import { toast } from 'react-toastify';
import './LoginPage.css';
import api from '../services/api';


const LoginPage = ({ onLogin, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    user_id: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  // const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.user_id || !formData.password) {
      toast.error('사용자 ID와 비밀번호를 모두 입력해주세요.');
      return;
    }

  setLoading(true);
  // setError('');

    try {
      const response = await api.post('/api/auth/login', formData);
      const data = response.data;

      if (data.success) {
        // 토큰을 localStorage에 저장
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        toast.success('로그인 성공!');
        // 부모 컴포넌트에 로그인 성공 알림
        onLogin(data.user, data.token);
      } else {
        toast.error(data.message || '로그인에 실패했습니다.');
      }
    } catch (err) {
      if (err.response && err.response.status === 401) {
        toast.error('아이디 또는 비밀번호가 올바르지 않습니다.');
      } else {
        toast.error('서버 연결 오류가 발생했습니다.');
      }
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>🎯 DMS 로그인</h1>
          <p>Digital Memory Service에 오신 것을 환영합니다</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {/* 에러 메시지 영역은 toast로 대체됨 */}

          <div className="form-group">
            <label htmlFor="user_id">사용자 ID</label>
            <input
              type="text"
              id="user_id"
              name="user_id"
              value={formData.user_id}
              onChange={handleChange}
              placeholder="사용자 ID를 입력하세요"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="비밀번호를 입력하세요"
              required
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? '⏳ 로그인 중...' : '🔐 로그인'}
          </button>
        </form>

        <div className="login-footer">
          <p>계정이 없으신가요?</p>
          <button 
            onClick={onSwitchToRegister}
            className="register-link-button"
            disabled={loading}
          >
            회원가입하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;