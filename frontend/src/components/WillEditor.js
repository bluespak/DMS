import React, { useState, useEffect } from 'react';
import './WillEditor.css';
import { triggerAPI } from '../services/triggerAPI';

const WillEditor = ({ user, onSave, onCancel, existingWill = null }) => {
  const [formData, setFormData] = useState({
    subject: '',
    body: '',
    recipients: [{ name: '', email: '' }]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 트리거 관련 상태
  const [triggerData, setTriggerData] = useState({
    trigger_type: 'inactivity',
    trigger_date: '',
    trigger_value: '3'
  });
  const [existingTrigger, setExistingTrigger] = useState(null);

  // 기존 Will 데이터가 있으면 폼에 로드
  useEffect(() => {
    if (existingWill) {
      setFormData({
        subject: existingWill.subject || '',
        body: existingWill.body || '',
        recipients: existingWill.recipients && existingWill.recipients.length > 0 
          ? existingWill.recipients.map(r => ({ name: r.recipient_name, email: r.recipient_email }))
          : [{ name: '', email: '' }]
      });
    }
  }, [existingWill]);

  // 사용자의 대기중인 트리거 로드
  useEffect(() => {
    const loadPendingTrigger = async () => {
      if (!user?.user_id) {
        console.log('❌ 트리거 로드: 사용자 정보 없음');
        return;
      }
      
      console.log('🔍 트리거 로드 시작:', user.user_id);
      
      try {
        const response = await triggerAPI.getPendingTriggerByUserId(user.user_id);
        console.log('📨 트리거 API 응답:', response);
        
        if (response.success && response.trigger) {
          console.log('✅ 기존 트리거 발견:', response.trigger);
          setExistingTrigger(response.trigger);
          setTriggerData({
            trigger_type: response.trigger.trigger_type || 'inactivity',
            trigger_date: response.trigger.trigger_date || '',
            trigger_value: response.trigger.trigger_value || '3'
          });
        } else {
          console.log('ℹ️ 기존 트리거 없음');
          setExistingTrigger(null);
        }
      } catch (error) {
        console.error('❌ 트리거 로드 실패:', error);
      }
    };

    loadPendingTrigger();
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTriggerChange = (e) => {
    const { name, value } = e.target;
    setTriggerData(prev => {
      const newData = { ...prev, [name]: value };
      
      // 비활성 기간 선택 시 자동으로 날짜 계산
      if (name === 'trigger_type' && value === 'inactivity') {
        const days = parseInt(newData.trigger_value) || 3;
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + days);
        newData.trigger_date = futureDate.toISOString().split('T')[0];
      }
      
      // 트리거 값 변경 시 비활성 기간이면 날짜 재계산
      if (name === 'trigger_value' && newData.trigger_type === 'inactivity') {
        const days = parseInt(value) || 3;
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + days);
        newData.trigger_date = futureDate.toISOString().split('T')[0];
      }
      
      return newData;
    });
  };

  // 남은 날수 계산 함수
  const calculateRemainingDays = (triggerDate) => {
    if (!triggerDate) return null;
    
    const today = new Date();
    const target = new Date(triggerDate);
    const diffTime = target - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  };

  const handleRecipientChange = (index, field, value) => {
    const newRecipients = [...formData.recipients];
    newRecipients[index][field] = value;
    setFormData(prev => ({
      ...prev,
      recipients: newRecipients
    }));
  };

  const addRecipient = () => {
    console.log('➕ 수신자 추가 클릭, 현재 수신자 수:', formData.recipients.length);
    setFormData(prev => {
      const newRecipients = [...prev.recipients, { name: '', email: '' }];
      console.log('✅ 새 수신자 목록:', newRecipients);
      return {
        ...prev,
        recipients: newRecipients
      };
    });
  };

  const removeRecipient = (index) => {
    if (formData.recipients.length > 1) {
      const newRecipients = formData.recipients.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        recipients: newRecipients
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 사용자 정보 확인
    if (!user || !user.user_id) {
      setError('사용자 정보가 없습니다. 다시 로그인해주세요');
      return;
    }
    
    // 폼 유효성 검사
    if (!formData.subject.trim()) {
      setError('제목을 입력해주세요');
      return;
    }
    
    if (!formData.body.trim()) {
      setError('내용을 입력해주세요');
      return;
    }

    // 유효한 수신자가 있는지 확인
    const validRecipients = formData.recipients.filter(r => r.name.trim() && r.email.trim());
    if (validRecipients.length === 0) {
      setError('최소 1명의 수신자를 입력해주세요');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const willData = {
        subject: formData.subject.trim(),
        body: formData.body.trim(),
        user_id: user.user_id,
        recipients: validRecipients
      };

      // 유언장 저장
      await onSave(willData);

      // 트리거 처리
      console.log('🔍 트리거 저장 시작:', { triggerData, existingTrigger });
      
      // 트리거 날짜 자동 계산 (비활성 기간인 경우)
      let finalTriggerDate = triggerData.trigger_date;
      if (triggerData.trigger_type === 'inactivity') {
        const days = parseInt(triggerData.trigger_value) || 3;
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + days);
        finalTriggerDate = futureDate.toISOString().split('T')[0];
      }

      const triggerPayload = {
        user_id: user.user_id,
        trigger_type: triggerData.trigger_type,
        trigger_date: finalTriggerDate,
        trigger_value: triggerData.trigger_value,
        description: triggerData.description || '',
        status: 'pending'
      };

      console.log('📦 트리거 페이로드:', triggerPayload);

      try {
        if (existingTrigger) {
          // 기존 트리거 수정
          console.log('🔄 기존 트리거 수정:', existingTrigger.trigger_id);
          const updateResult = await triggerAPI.updateTrigger(existingTrigger.trigger_id, triggerPayload);
          console.log('✅ 트리거 수정 결과:', updateResult);
        } else {
          // 새 트리거 생성
          console.log('➕ 새 트리거 생성');
          const createResult = await triggerAPI.createTrigger(triggerPayload);
          console.log('✅ 트리거 생성 결과:', createResult);
        }
      } catch (triggerError) {
        console.error('❌ 트리거 저장 실패:', triggerError);
        // 트리거 저장 실패는 에러로 표시하지만 유언장은 저장된 상태
        setError(`유언장은 저장되었지만 트리거 설정에 실패했습니다: ${triggerError.message}`);
      }
    } catch (err) {
      setError(err.message || '저장 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="will-editor">
      <div className="will-editor-header">
        <h2>{existingWill ? '📝 유언장 수정' : '📝 유언장 작성'}</h2>
        <p className="user-info">
          작성자: {user?.firstname || user?.FirstName} {user?.lastname || user?.LastName} ({user?.user_id})
        </p>
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="will-form">
        {/* 제목 입력 */}
        <div>
          <label htmlFor="subject">📋 제목</label>
          <input
            type="text"
            id="subject"
            name="subject"
            className="will-input"
            value={formData.subject}
            onChange={handleInputChange}
            placeholder="유언장의 제목을 입력하세요"
            disabled={loading}
            maxLength={200}
          />
        </div>

        {/* 수신자 목록 */}
        <div>
          <label>👥 수신자 목록</label>
          <div className="recipients-section">
            {formData.recipients.map((recipient, index) => (
              <div key={index} className="recipient-item">
                <div className="recipient-inputs">
                  <input
                    type="text"
                    className="will-input"
                    placeholder="수신자 이름"
                    value={recipient.name}
                    onChange={(e) => handleRecipientChange(index, 'name', e.target.value)}
                    disabled={loading}
                  />
                  <input
                    type="email"
                    className="will-input"
                    placeholder="수신자 이메일"
                    value={recipient.email}
                    onChange={(e) => handleRecipientChange(index, 'email', e.target.value)}
                    disabled={loading}
                  />
                  {formData.recipients.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeRecipient(index)}
                      className="remove-recipient-btn"
                      disabled={loading}
                    >
                      ❌
                    </button>
                  )}
                </div>
              </div>
            ))}
            <button
              type="button"
              onClick={addRecipient}
              className="add-recipient-btn"
              disabled={loading}
            >
              ➕ 수신자 추가
            </button>
          </div>
        </div>

        {/* 내용 입력 */}
        <div className="form-group">
          <label htmlFor="body">📄 내용</label>
          <textarea
            id="body"
            name="body"
            className="will-input"
            value={formData.body}
            onChange={handleInputChange}
            placeholder="전달하고 싶은 메시지를 입력하세요..."
            rows={10}
            disabled={loading}
          />
        </div>

        {/* 트리거 설정 */}
        <div className="form-group">
          <label>⏰ 트리거 설정</label>
          <div className="trigger-section">
            <div className="trigger-info">
              <p>📝 트리거는 유언장이 자동으로 발송될 조건을 설정합니다. 대기중인 트리거는 하나만 설정할 수 있습니다.</p>
              {existingTrigger && (
                <p className="existing-trigger-notice">
                  ✅ 현재 대기중인 트리거가 있습니다. 수정하거나 새로운 날짜를 설정할 수 있습니다.
                </p>
              )}
            </div>
            
            <div className="trigger-form">
              <div className="trigger-row">
                <div className="trigger-field">
                  <label htmlFor="trigger_type">트리거 종류</label>
                  <select
                    id="trigger_type"
                    name="trigger_type"
                    className="will-input"
                    value={triggerData.trigger_type}
                    onChange={handleTriggerChange}
                    disabled={loading}
                  >
                    <option value="inactivity">비활성 기간</option>
                    <option value="date">특정 날짜</option>
                    <option value="manual">수동 발송</option>
                  </select>
                </div>
                
                {/* 특정 날짜 선택 시만 날짜 입력 표시 */}
                {triggerData.trigger_type === 'date' && (
                  <div className="trigger-field">
                    <label htmlFor="trigger_date">트리거 날짜</label>
                    <input
                      type="date"
                      id="trigger_date"
                      name="trigger_date"
                      className="will-input"
                      value={triggerData.trigger_date}
                      onChange={handleTriggerChange}
                      disabled={loading}
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                )}
              </div>
              
              {/* 비활성 기간 선택 시만 트리거 값 표시 */}
              {triggerData.trigger_type === 'inactivity' && (
                <div className="trigger-row">
                  <div className="trigger-field">
                    <label htmlFor="trigger_value">비활성 기간 (일)</label>
                    <input
                      type="number"
                      id="trigger_value"
                      name="trigger_value"
                      className="will-input"
                      value={triggerData.trigger_value}
                      onChange={handleTriggerChange}
                      placeholder="예: 3 (3일 후)"
                      disabled={loading}
                      min="1"
                      max="365"
                    />
                  </div>
                </div>
              )}
              
              {/* 계산된 트리거 날짜와 남은 날수 표시 */}
              {triggerData.trigger_date && (
                <div className="trigger-info-display">
                  <div className="trigger-date-info">
                    <span className="trigger-date-label">📅 트리거 예정일: </span>
                    <span className="trigger-date-value">{triggerData.trigger_date}</span>
                    {(() => {
                      const remainingDays = calculateRemainingDays(triggerData.trigger_date);
                      if (remainingDays !== null) {
                        return (
                          <span className={`remaining-days ${remainingDays <= 3 ? 'urgent' : remainingDays <= 7 ? 'warning' : 'normal'}`}>
                            {remainingDays > 0 ? ` (${remainingDays}일 후)` : remainingDays === 0 ? ' (오늘)' : ` (${Math.abs(remainingDays)}일 지남)`}
                          </span>
                        );
                      }
                      return null;
                    })()}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 버튼 그룹 */}
        <div className="form-actions">
          <button
            type="submit"
            className="save-btn"
            disabled={loading}
          >
            {loading ? '⏳ 저장 중...' : (existingWill ? '💾 수정 완료' : '💾 저장하기')}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="cancel-btn"
            disabled={loading}
          >
            ❌ 취소
          </button>
        </div>
      </form>
    </div>
  );
};

export default WillEditor;