// React 라이브러리를 가져옵니다
import React, { useState, useEffect } from 'react';

// CSS 파일을 가져옵니다 (스타일링용)
import './App.css';

// API 서비스를 가져옵니다
import { userInfoAPI } from './services/userInfoAPI';

// App이라는 함수형 컴포넌트를 만듭니다
// 이것이 우리의 메인 컴포넌트입니다
function App() {
  // React 상태(State) 관리
  const [users, setUsers] = useState([]); // 사용자 목록
  const [loading, setLoading] = useState(false); // 로딩 상태
  const [error, setError] = useState(null); // 에러 상태
  const [showAddForm, setShowAddForm] = useState(false); // 추가 폼 표시 여부
  const [editingUser, setEditingUser] = useState(null); // 수정 중인 사용자
  
  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1); // 현재 페이지
  const [usersPerPage] = useState(10); // 페이지당 사용자 수
  
  // 새 사용자 폼 데이터
  const [newUser, setNewUser] = useState({
    FirstName: '',
    LastName: '',
    Email: '',
    DOB: '',
    Grade: 'Standard'
  });

  // 사용자 목록을 가져오는 함수
  const fetchUsers = async () => {
    try {
      setLoading(true); // 로딩 시작
      setError(null); // 에러 초기화
      
      console.log('🚀 사용자 목록 요청 시작...');
      const response = await userInfoAPI.getAllUsers();
      
      console.log('✅ 받은 응답:', response);
      console.log('✅ 사용자 데이터:', response.data);
      
      // Flask API는 {success: true, data: [...], count: N} 형식으로 반환
      if (response.success && response.data) {
        console.log('📊 사용자 수:', response.data.length);
        console.log('👤 첫 번째 사용자:', response.data[0]);
        setUsers(response.data); // 실제 사용자 배열을 상태에 저장
      } else {
        console.log('⚠️ 응답에 데이터가 없습니다:', response);
        setUsers([]); // 데이터가 없으면 빈 배열
      }
      
    } catch (err) {
      console.error('❌ API 호출 실패:', err);
      setError(err.message || '사용자 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false); // 로딩 종료
    }
  };

  // 새 사용자 추가 함수
  const addUser = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🆕 새 사용자 추가 시작:', newUser);
      
      const response = await userInfoAPI.createUser(newUser);
      console.log('✅ 사용자 추가 성공:', response);
      
      // 폼 초기화
      setNewUser({
        FirstName: '',
        LastName: '',
        Email: '',
        DOB: '',
        Grade: 'Standard'
      });
      setShowAddForm(false);
      
      // 목록 새로고침 및 첫 페이지로 이동
      await fetchUsers();
      resetToFirstPage();
      
    } catch (err) {
      console.error('❌ 사용자 추가 실패:', err);
      setError(err.message || '사용자 추가에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 사용자 삭제 함수
  const deleteUser = async (userId, userName) => {
    if (!window.confirm(`정말로 ${userName} 사용자를 삭제하시겠습니까?`)) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('🗑️ 사용자 삭제 시작:', userId);
      
      const response = await userInfoAPI.deleteUser(userId);
      console.log('✅ 사용자 삭제 성공:', response);
      
      // 목록 새로고침 및 페이지 조정
      await fetchUsers();
      
      // 현재 페이지에 사용자가 없으면 이전 페이지로 이동
      const remainingUsers = users.length - 1;
      const maxPage = Math.ceil(remainingUsers / usersPerPage);
      if (currentPage > maxPage && maxPage > 0) {
        setCurrentPage(maxPage);
      }
      
    } catch (err) {
      console.error('❌ 사용자 삭제 실패:', err);
      setError(err.message || '사용자 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 사용자 수정 함수
  const updateUser = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('✏️ 사용자 수정 시작:', editingUser);
      
      const response = await userInfoAPI.updateUser(editingUser.id, editingUser);
      console.log('✅ 사용자 수정 성공:', response);
      
      setEditingUser(null);
      
      // 목록 새로고침
      await fetchUsers();
      
    } catch (err) {
      console.error('❌ 사용자 수정 실패:', err);
      setError(err.message || '사용자 수정에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 새 사용자 폼 입력 변경 처리
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewUser(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 수정 사용자 폼 입력 변경 처리
  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditingUser(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 페이지네이션 계산
  const indexOfLastUser = currentPage * usersPerPage;
  const indexOfFirstUser = indexOfLastUser - usersPerPage;
  const currentUsers = users.slice(indexOfFirstUser, indexOfLastUser);
  const totalPages = Math.ceil(users.length / usersPerPage);

  // 페이지 변경 함수
  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    console.log(`📄 페이지 ${pageNumber}로 이동`);
  };

  // 이전 페이지
  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // 다음 페이지
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // 사용자 추가/수정/삭제 후 첫 페이지로 이동
  const resetToFirstPage = () => {
    setCurrentPage(1);
  };

  // 컴포넌트가 처음 렌더링될 때 사용자 목록 가져오기
  useEffect(() => {
    fetchUsers();
  }, []); // 빈 배열 = 한 번만 실행

  return (
    <div className="App">
      {/* 헤더 섹션 */}
      <header className="App-header">
        <h1>🎯 DMS - Digital Memory Service</h1>
        <p>
          React.js를 처음 배우는 개발자의 첫 번째 프로젝트입니다! 
        </p>
        
        {/* API 테스트 섹션 */}
        <div className="api-section">
          <h2>📡 Backend API 연결 테스트</h2>
          
          {/* 액션 버튼들 */}
          <div className="action-buttons">
            <button 
              onClick={fetchUsers} 
              disabled={loading}
              className="refresh-button"
            >
              {loading ? '⏳ 로딩 중...' : '🔄 사용자 목록 새로고침'}
            </button>
            
            <button 
              onClick={() => setShowAddForm(!showAddForm)} 
              disabled={loading}
              className="add-button"
            >
              {showAddForm ? '❌ 추가 취소' : '➕ 새 사용자 추가'}
            </button>
          </div>

          {/* 로딩 상태 표시 */}
          {loading && <p>⏳ 데이터를 불러오는 중...</p>}

          {/* 에러 상태 표시 */}
          {error && (
            <div className="error-message">
              ❌ 에러: {error}
            </div>
          )}

          {/* 새 사용자 추가 폼 */}
          {showAddForm && (
            <div className="add-user-form">
              <h3>➕ 새 사용자 추가</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>이름:</label>
                  <input
                    type="text"
                    name="FirstName"
                    value={newUser.FirstName}
                    onChange={handleInputChange}
                    placeholder="이름을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>성:</label>
                  <input
                    type="text"
                    name="LastName"
                    value={newUser.LastName}
                    onChange={handleInputChange}
                    placeholder="성을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>이메일:</label>
                  <input
                    type="email"
                    name="Email"
                    value={newUser.Email}
                    onChange={handleInputChange}
                    placeholder="이메일을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>생년월일:</label>
                  <input
                    type="date"
                    name="DOB"
                    value={newUser.DOB}
                    onChange={handleInputChange}
                  />
                </div>
                
                <div className="form-group">
                  <label>등급:</label>
                  <select
                    name="Grade"
                    value={newUser.Grade}
                    onChange={handleInputChange}
                  >
                    <option value="Standard">Standard</option>
                    <option value="Gold">Gold</option>
                    <option value="Premium">Premium</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions">
                <button 
                  onClick={addUser} 
                  disabled={loading || !newUser.FirstName || !newUser.LastName || !newUser.Email}
                  className="save-button"
                >
                  💾 사용자 추가
                </button>
                <button 
                  onClick={() => setShowAddForm(false)} 
                  disabled={loading}
                  className="cancel-button"
                >
                  ❌ 취소
                </button>
              </div>
            </div>
          )}

          {/* 사용자 수정 폼 */}
          {editingUser && (
            <div className="edit-user-form">
              <h3>✏️ 사용자 정보 수정</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label>이름:</label>
                  <input
                    type="text"
                    name="FirstName"
                    value={editingUser.FirstName}
                    onChange={handleEditInputChange}
                    placeholder="이름을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>성:</label>
                  <input
                    type="text"
                    name="LastName"
                    value={editingUser.LastName}
                    onChange={handleEditInputChange}
                    placeholder="성을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>이메일:</label>
                  <input
                    type="email"
                    name="Email"
                    value={editingUser.Email}
                    onChange={handleEditInputChange}
                    placeholder="이메일을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>생년월일:</label>
                  <input
                    type="date"
                    name="DOB"
                    value={editingUser.DOB}
                    onChange={handleEditInputChange}
                  />
                </div>
                
                <div className="form-group">
                  <label>등급:</label>
                  <select
                    name="Grade"
                    value={editingUser.Grade}
                    onChange={handleEditInputChange}
                  >
                    <option value="Standard">Standard</option>
                    <option value="Gold">Gold</option>
                    <option value="Premium">Premium</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions">
                <button 
                  onClick={updateUser} 
                  disabled={loading || !editingUser.FirstName || !editingUser.LastName || !editingUser.Email}
                  className="save-button"
                >
                  💾 수정 저장
                </button>
                <button 
                  onClick={() => setEditingUser(null)} 
                  disabled={loading}
                  className="cancel-button"
                >
                  ❌ 취소
                </button>
              </div>
            </div>
          )}

          {/* 사용자 목록 표시 */}
          {!loading && !error && (
            <div className="users-list">
              <div className="list-header">
                <h3>👥 사용자 목록 (전체 {users.length}명)</h3>
                <div className="page-info">
                  📄 페이지 {currentPage} / {totalPages} 
                  {users.length > 0 && (
                    <span> (현재 {indexOfFirstUser + 1}-{Math.min(indexOfLastUser, users.length)}번째 표시)</span>
                  )}
                </div>
              </div>
              
              {users.length > 0 ? (
                <>
                  <div className="users-grid">
                    {currentUsers.map((user, index) => (
                      <div key={user.id || index} className="user-card">
                        <div className="user-info">
                          <h4>{user.FirstName} {user.LastName}</h4>
                          <p>📧 {user.Email}</p>
                          <p>🎂 생일: {user.DOB}</p>
                          <p>🏆 등급: {user.Grade}</p>
                          <p>🆔 ID: {user.id}</p>
                          <p>📅 가입일: {new Date(user.created_at).toLocaleDateString()}</p>
                        </div>
                        
                        <div className="user-actions">
                          <button 
                            onClick={() => setEditingUser(user)}
                            className="edit-button"
                            disabled={loading}
                          >
                            ✏️ 수정
                          </button>
                          <button 
                            onClick={() => deleteUser(user.id, `${user.FirstName} ${user.LastName}`)}
                            className="delete-button"
                            disabled={loading}
                          >
                            🗑️ 삭제
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* 페이지네이션 컨트롤 */}
                  {totalPages > 1 && (
                    <div className="pagination">
                      <button 
                        onClick={prevPage}
                        disabled={currentPage === 1}
                        className="pagination-button"
                      >
                        ◀ 이전
                      </button>
                      
                      <div className="page-numbers">
                        {Array.from({ length: totalPages }, (_, i) => i + 1).map((number) => (
                          <button
                            key={number}
                            onClick={() => paginate(number)}
                            className={`page-number ${currentPage === number ? 'active' : ''}`}
                          >
                            {number}
                          </button>
                        ))}
                      </div>
                      
                      <button 
                        onClick={nextPage}
                        disabled={currentPage === totalPages}
                        className="pagination-button"
                      >
                        다음 ▶
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <p>📭 등록된 사용자가 없습니다.</p>
              )}
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

// 이 컴포넌트를 다른 파일에서 사용할 수 있도록 내보냅니다
export default App;