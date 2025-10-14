import React, { useState } from 'react';
import './RegisterPage.css';

const RegisterPage = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    user_id: '',
    password: '',
    confirmPassword: '',
    email: '',
    firstname: '',
    lastname: '',
    grade: 'Standard',
    DOB: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 필수 필드 확인
    const requiredFields = ['user_id', 'password', 'email', 'firstname', 'lastname'];
    for (const field of requiredFields) {
      if (!formData[field]) {
        setError(`${field}는 필수 입력 항목입니다.`);
        return;
      }
    }

    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    // 비밀번호 길이 확인
    if (formData.password.length < 6) {
      setError('비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const registerData = { ...formData };
      delete registerData.confirmPassword; // 확인 비밀번호는 제외

      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerData),
      });

      const data = await response.json();

      if (data.success) {
        // 토큰을 localStorage에 저장
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // 부모 컴포넌트에 회원가입 성공 알림
        onRegister(data.user, data.token);
      } else {
        setError(data.message || '회원가입에 실패했습니다.');
      }
    } catch (err) {
      setError('서버 연결 오류가 발생했습니다.');
      console.error('Register error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <h1>✨ DMS 회원가입</h1>
          <p>Digital Memory Service에 가입하여 소중한 기억을 보호하세요</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="user_id">사용자 ID *</label>
              <input
                type="text"
                id="user_id"
                name="user_id"
                value={formData.user_id}
                onChange={handleChange}
                placeholder="사용자 ID"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">이메일 *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="이메일 주소"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstname">이름 *</label>
              <input
                type="text"
                id="firstname"
                name="firstname"
                value={formData.firstname}
                onChange={handleChange}
                placeholder="이름"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="lastname">성 *</label>
              <input
                type="text"
                id="lastname"
                name="lastname"
                value={formData.lastname}
                onChange={handleChange}
                placeholder="성"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">비밀번호 *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="비밀번호 (최소 6자)"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">비밀번호 확인 *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="비밀번호 재입력"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="grade">등급</label>
              <select
                id="grade"
                name="grade"
                value={formData.grade}
                onChange={handleChange}
                disabled={loading}
              >
                <option value="Standard">Standard</option>
                <option value="Gold">Gold</option>
                <option value="Premium">Premium</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="DOB">생년월일</label>
              <input
                type="date"
                id="DOB"
                name="DOB"
                value={formData.DOB}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="register-button"
            disabled={loading}
          >
            {loading ? '⏳ 회원가입 중...' : '🎯 회원가입 완료'}
          </button>
        </form>

        <div className="register-footer">
          <p>이미 계정이 있으신가요?</p>
          <button 
            onClick={onSwitchToLogin}
            className="login-link-button"
            disabled={loading}
          >
            로그인하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;