// React 라이브러리를 가져옵니다
import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// CSS 파일을 가져옵니다 (스타일링용)
import './App.css';

// API 서비스를 가져옵니다
import { userInfoAPI } from './services/userInfoAPI';
import { willAPI } from './services/willAPI';
import { recipientsAPI } from './services/recipientsAPI';
import { dispatchLogAPI } from './services/dispatchLogAPI';
import { triggerAPI } from './services/triggerAPI';

// 환경설정을 가져옵니다
import config from './config/config';

// 로그 시스템을 가져옵니다
import logger from './utils/logger';
import './utils/logFileManager'; // 로그 파일 관리자 초기화

// 홈페이지 컴포넌트를 가져옵니다
import DeadManSwitchHome from './components/DeadManSwitchHome';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import WillEditor from './components/WillEditor';

// App이라는 함수형 컴포넌트를 만듭니다
// 이것이 우리의 메인 컴포넌트입니다
function App() {
  // 페이지 상태 관리
  const [currentView, setCurrentView] = useState('home'); // 현재 보여줄 페이지
  
  // 인증 상태 관리
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [authToken, setAuthToken] = useState(null);
  
  // 햄버거 메뉴 상태
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  // React 상태(State) 관리
  const [users, setUsers] = useState([]); // 사용자 목록
  const [loading, setLoading] = useState(false); // 로딩 상태
  const [error, setError] = useState(null); // 에러 상태
  const [successMessage, setSuccessMessage] = useState(null); // 성공 메시지 상태
  const [editingUser, setEditingUser] = useState(null); // 수정 중인 사용자
  
  // Will 관련 상태
  const [selectedUserWills, setSelectedUserWills] = useState([]); // 선택된 사용자의 Will 목록
  const [showWillModal, setShowWillModal] = useState(false); // Will 모달 표시 여부
  const [currentWillUser, setCurrentWillUser] = useState(null); // Will을 조회 중인 사용자
  const [currentUserWill, setCurrentUserWill] = useState(null); // 현재 사용자의 Will (편집용)
  
  // 수신인 관련 상태
  const [willRecipients, setWillRecipients] = useState({}); // Will ID별 수신인 목록 {willId: recipients}
  
  // DispatchLog 관련 상태
  const [willDispatchLogs, setWillDispatchLogs] = useState({}); // Will ID별 DispatchLog 목록 {willId: logs}
  
  // 트리거 관련 상태
  const [showTriggerModal, setShowTriggerModal] = useState(false); // 트리거 모달 표시 여부
  const [currentTriggerUser, setCurrentTriggerUser] = useState(null); // 트리거를 조회 중인 사용자
  const [userTriggers, setUserTriggers] = useState([]); // 사용자의 트리거 목록
  const [editingTrigger, setEditingTrigger] = useState(null); // 수정 중인 트리거
  const [showAddTriggerModal, setShowAddTriggerModal] = useState(false); // 트리거 추가 모달 표시 여부
  
  // 페이지네이션 상태 - 환경변수에서 설정값 가져오기
  const [currentPage, setCurrentPage] = useState(1); // 현재 페이지
  const [usersPerPage] = useState(config.pagination.usersPerPage); // 페이지당 사용자 수 (환경변수)

  // 사용자 목록을 가져오는 함수
  const fetchUsers = async () => {
    logger.data('info', '사용자 목록 조회 시작');
    
    try {
      setLoading(true); // 로딩 시작
      setError(null); // 에러 초기화
      
      logger.server('info', 'GET /api/userinfo - 사용자 목록 요청 시작');
      const response = await userInfoAPI.getAllUsers();
      
      logger.logApiCall('GET', '/api/userinfo', null, response);
      
      // Flask API는 {success: true, data: [...], count: N} 형식으로 반환
      if (response.success && response.data) {
        logger.data('success', `사용자 목록 조회 성공 - ${response.data.length}명`, {
          count: response.data.length,
          firstUser: response.data[0]
        });
        setUsers(response.data); // 실제 사용자 배열을 상태에 저장
      } else {
        logger.data('warn', '응답에 사용자 데이터가 없음', response);
        setUsers([]); // 데이터가 없으면 빈 배열
      }
      
    } catch (err) {
      logger.error('사용자 목록 조회 실패', err);
      setError(err.message || '사용자 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false); // 로딩 종료
      logger.data('info', '사용자 목록 조회 완료');
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
      
      // 목록 새로고침
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
      
      const response = await userInfoAPI.updateUser(editingUser.user_id, editingUser);
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
  
  // 페이지 버튼 범위 계산 (최대 버튼 수 제한)
  const maxPageButtons = config.pagination.maxPageButtons;
  const getPageNumbers = () => {
    if (totalPages <= maxPageButtons) {
      // 총 페이지가 최대 버튼 수보다 적으면 모든 페이지 표시
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    
    const halfButtons = Math.floor(maxPageButtons / 2);
    let startPage = Math.max(1, currentPage - halfButtons);
    let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);
    
    // 끝 페이지가 조정되면 시작 페이지도 재조정
    if (endPage - startPage + 1 < maxPageButtons) {
      startPage = Math.max(1, endPage - maxPageButtons + 1);
    }
    
    return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
  };

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

  // 특정 Will의 수신인 조회
  const fetchWillRecipients = async (willId) => {
    try {
      console.log(`� [DEBUG] Will ID ${willId}의 수신인 조회 시작...`);
      console.log(`🔍 [DEBUG] API 호출: /api/recipients/will/${willId}`);
      
      const response = await recipientsAPI.getRecipientsByWillId(willId);
      console.log('🔍 [DEBUG] 수신인 API 응답:', response);
      
      if (response.success) {
        console.log(`🔍 [DEBUG] 수신인 데이터:`, response.recipients);
        setWillRecipients(prev => {
          const newState = {
            ...prev,
            [willId]: response.recipients
          };
          console.log(`🔍 [DEBUG] willRecipients 상태 업데이트:`, newState);
          return newState;
        });
        console.log(`📊 수신인 개수: ${response.count}명`);
      } else {
        console.log('⚠️ 수신인 데이터 없음, 에러:', response.error);
        setWillRecipients(prev => ({
          ...prev,
          [willId]: []
        }));
      }
      
    } catch (err) {
      console.error('❌ 수신인 조회 실패:', err);
      setWillRecipients(prev => ({
        ...prev,
        [willId]: []
      }));
    }
  };

  // 특정 Will의 DispatchLog 조회
  const fetchWillDispatchLogs = async (willId) => {
    try {
      console.log(`📋 Will ID ${willId}의 DispatchLog 조회 시작...`);
      
      const response = await dispatchLogAPI.getDispatchLogsByWillId(willId);
      console.log('✅ DispatchLog 응답:', response);
      
      if (response.success) {
        setWillDispatchLogs(prev => ({
          ...prev,
          [willId]: response.logs
        }));
        console.log(`📊 DispatchLog 개수: ${response.count}개`);
      } else {
        console.log('⚠️ DispatchLog 데이터 없음');
        setWillDispatchLogs(prev => ({
          ...prev,
          [willId]: []
        }));
      }
      
    } catch (err) {
      console.error('❌ DispatchLog 조회 실패:', err);
      setWillDispatchLogs(prev => ({
        ...prev,
        [willId]: []
      }));
    }
  };

  // 사용자의 Will 목록 조회
  const fetchUserWills = async (user) => {
    try {
      setLoading(true);
      setError(null);
      
  console.log(`📜 ${user.firstname} ${user.lastname}의 Will 목록 조회 시작...`);
      
      const response = await willAPI.getWillsByUserId(user.user_id);
      console.log('✅ Will 응답:', response);
      
      if (response.success && response.data) {
        setSelectedUserWills(response.data);
        setCurrentWillUser(user);
        setShowWillModal(true);
        
        // 각 Will의 수신인과 DispatchLog도 함께 조회
        response.data.forEach(will => {
          fetchWillRecipients(will.id);
          fetchWillDispatchLogs(will.id);
        });
        
        console.log(`📊 Will 개수: ${response.data.length}개`);
      } else {
        setSelectedUserWills([]);
        setCurrentWillUser(user);
        setShowWillModal(true);
        console.log('⚠️ Will 데이터가 없습니다');
      }
      
    } catch (err) {
      console.error('❌ Will 조회 실패:', err);
  setError(`${user.firstname} ${user.lastname}의 Will 정보를 불러오는데 실패했습니다.`);
    } finally {
      setLoading(false);
    }
  };

  // Will 모달 닫기
  const closeWillModal = () => {
    setShowWillModal(false);
    setSelectedUserWills([]);
    setCurrentWillUser(null);
    setWillRecipients({}); // 수신인 데이터도 초기화
    setWillDispatchLogs({}); // DispatchLog 데이터도 초기화
  };

  // 사용자의 트리거 목록 조회
  const fetchUserTriggers = async (user) => {
    try {
      setLoading(true);
      setError(null);
      
  console.log(`⏰ ${user.firstname} ${user.lastname}의 트리거 목록 조회 시작...`);
      
      const response = await triggerAPI.getTriggersByUserId(user.user_id);
      console.log('✅ 트리거 응답:', response);
      
      if (response && response.success) {
        setUserTriggers(response.triggers || []);
        setCurrentTriggerUser(user);
        setShowTriggerModal(true);
        console.log(`📊 트리거 개수: ${response.count || response.triggers?.length || 0}개`);
      } else {
        // 응답은 있지만 success가 false인 경우
        setUserTriggers([]);
        setCurrentTriggerUser(user);
        setShowTriggerModal(true);
        console.log('⚠️ 트리거 데이터가 없거나 조회에 실패했습니다:', response?.message || response?.error);
        
        if (response?.message || response?.error) {
          setError(`트리거 조회 실패: ${response.message || response.error}`);
        }
      }
      
    } catch (err) {
      console.error('❌ 트리거 조회 실패:', err);
      const errorMessage = err.response?.data?.message || err.message || '네트워크 오류가 발생했습니다.';
  setError(`${user.firstname} ${user.lastname}의 트리거 정보를 불러오는데 실패했습니다. 오류: ${errorMessage}`);
      
      // 오류가 발생해도 모달은 열어서 사용자가 새 트리거를 추가할 수 있도록 함
      setUserTriggers([]);
      setCurrentTriggerUser(user);
      setShowTriggerModal(true);
    } finally {
      setLoading(false);
    }
  };

  // 트리거 모달 닫기
  const closeTriggerModal = () => {
    setShowTriggerModal(false);
    setUserTriggers([]);
    setCurrentTriggerUser(null);
    setEditingTrigger(null);
    setShowAddTriggerModal(false);
  };

  // 새 트리거 추가 모달 열기
  const openAddTriggerModal = () => {
    setEditingTrigger({
      user_id: currentTriggerUser.user_id,
      trigger_type: '',
      trigger_date: '',
      status: 'pending'
    });
    setShowAddTriggerModal(true);
  };

  // 새 트리거 추가 모달 닫기
  const closeAddTriggerModal = () => {
    setShowAddTriggerModal(false);
    setEditingTrigger(null);
  };

  // 트리거 수정 시작
  const startEditTrigger = (trigger) => {
    setEditingTrigger({
      ...trigger,
      trigger_date: trigger.trigger_date ? trigger.trigger_date.split('T')[0] : '',
      trigger_time: trigger.trigger_date ? trigger.trigger_date.split('T')[1]?.split('.')[0] : ''
    });
    setShowAddTriggerModal(true);
  };

  // 트리거 저장 (생성/수정)
  const saveTrigger = async () => {
    if (!editingTrigger || !editingTrigger.trigger_type || !editingTrigger.trigger_date) {
      logger.warn('data', '트리거 저장 실패 - 필수 필드 누락', {
        trigger_type: editingTrigger?.trigger_type,
        trigger_date: editingTrigger?.trigger_date
      });
      alert('트리거 타입과 날짜를 입력해주세요.');
      return;
    }
    
    const isUpdate = editingTrigger.trigger_id;
    const actionType = isUpdate ? '수정' : '생성';
    
    logger.logUserAction(`트리거 ${actionType} 시작`, 'trigger-form', {
      triggerId: editingTrigger.trigger_id,
      userId: currentTriggerUser.user_id,
      triggerType: editingTrigger.trigger_type
    });
    
    // 트리거 데이터 준비 (catch 블록에서도 접근 가능하도록 try 블록 밖에 정의)
    const triggerData = {
      user_id: editingTrigger.user_id || currentTriggerUser.user_id,
      trigger_type: editingTrigger.trigger_type || 'manual', // 사용자가 선택한 타입 사용
      trigger_date: editingTrigger.trigger_date,
      status: editingTrigger.status || 'pending'
    };

    try {
      setLoading(true);
      setError(null);
      
      logger.data('info', `트리거 ${actionType} 데이터 준비 완료`, triggerData);
      
      let response;
      
      if (isUpdate) {
        // 기존 트리거 수정
        logger.server('info', `PUT /api/triggers/${editingTrigger.trigger_id} - 트리거 수정 요청`);
        response = await triggerAPI.updateTrigger(editingTrigger.trigger_id, triggerData);
        logger.logApiCall('PUT', `/api/triggers/${editingTrigger.trigger_id}`, triggerData, response);
      } else {
        // 새 트리거 생성
        logger.server('info', 'POST /api/triggers - 트리거 생성 요청');
        response = await triggerAPI.createTrigger(triggerData);
        logger.logApiCall('POST', '/api/triggers', triggerData, response);
      }
      
      // 서버 응답 확인 및 메시지 표시
      if (response && response.success) {
        const triggerId = response.trigger?.trigger_id || editingTrigger.trigger_id;
        
        logger.success('data', `트리거 ${actionType} 성공`, {
          triggerId,
          userId: currentTriggerUser.user_id,
          triggerType: triggerData.trigger_type,
          triggerDate: triggerData.trigger_date
        });
        
        // 성공 메시지
        alert(
          isUpdate 
            ? `✅ 트리거가 성공적으로 수정되었습니다!\n트리거 ID: ${triggerId}` 
            : `✅ 새 트리거가 성공적으로 생성되었습니다!\n트리거 ID: ${triggerId || 'N/A'}`
        );
        
        // 모달 닫기 및 상태 초기화
        closeAddTriggerModal();
        
        // 트리거 목록 강제 새로고침 (캐시 방지)
        logger.data('info', '트리거 목록 새로고침 시작');
        const refreshResponse = await triggerAPI.getTriggersByUserId(currentTriggerUser.user_id);
        if (refreshResponse && refreshResponse.success) {
          setUserTriggers(refreshResponse.triggers || []);
          logger.success('data', `트리거 목록 새로고침 완료 - ${refreshResponse.triggers?.length || 0}개`);
        }
        
      } else {
        // 서버에서 실패 응답을 받은 경우
        const errorMsg = response?.message || response?.error || '알 수 없는 오류가 발생했습니다.';
        
        logger.error(`트리거 ${actionType} 실패 - 서버 응답 오류`, {
          response,
          errorMsg,
          triggerId: editingTrigger.trigger_id
        });
        
        alert(
          isUpdate 
            ? `❌ 트리거 수정에 실패했습니다.\n오류: ${errorMsg}` 
            : `❌ 트리거 생성에 실패했습니다.\n오류: ${errorMsg}`
        );
        setError(errorMsg);
      }
      
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || '네트워크 오류가 발생했습니다.';
      
      logger.error(`트리거 ${actionType} 실패 - 예외 발생`, {
        error: err,
        errorMessage,
        triggerData,
        triggerId: editingTrigger.trigger_id
      });
      
      alert(
        isUpdate 
          ? `❌ 트리거 수정 중 오류가 발생했습니다.\n오류: ${errorMessage}` 
          : `❌ 트리거 생성 중 오류가 발생했습니다.\n오류: ${errorMessage}`
      );
      
      setError(isUpdate ? '트리거 수정에 실패했습니다.' : '트리거 생성에 실패했습니다.');
    } finally {
      setLoading(false);
      logger.data('info', `트리거 ${actionType} 프로세스 완료`);
    }
  };

  // 트리거 입력 변경 처리
  const handleTriggerInputChange = (e) => {
    const { name, value } = e.target;
    setEditingTrigger(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 인증 관련 함수들
  const handleLogin = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    setIsAuthenticated(true);
    setCurrentView('home');
    logger.system('info', '사용자 로그인 성공', { userId: user.user_id });
  };

  const handleRegister = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    setIsAuthenticated(true);
    setCurrentView('home');
    logger.system('info', '사용자 회원가입 및 로그인 성공', { userId: user.user_id });
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setAuthToken(null);
    setIsAuthenticated(false);
    setCurrentView('home');
    logger.system('info', '사용자 로그아웃');
  };

  // "내 스위치 만들기" 버튼 클릭 핸들러
  const handleCreateSwitch = async () => {
    if (!isAuthenticated) {
      // 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
      setCurrentView('login');
      logger.system('info', '미인증 사용자 로그인 페이지로 리다이렉트');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // 현재 사용자의 Will이 있는지 확인
      logger.system('info', '사용자 Will 조회 시작', { userId: currentUser.user_id });
      const response = await willAPI.getWillsByUserId(currentUser.user_id);
      
      if (response.success && response.data && response.data.length > 0) {
        // 기존 Will이 있으면 편집 모드
        const existingWill = response.data[0]; // 첫 번째 Will 사용
        
        // 수신자 정보도 함께 가져오기
        const recipientsResponse = await recipientsAPI.getRecipientsByWillId(existingWill.id);
        if (recipientsResponse.success) {
          existingWill.recipients = recipientsResponse.recipients;
        }
        
        setCurrentUserWill(existingWill);
        logger.system('info', '기존 Will 편집 모드', { willId: existingWill.id });
      } else {
        // 새로운 Will 생성 모드
        setCurrentUserWill(null);
        logger.system('info', '새 Will 생성 모드');
      }

      setCurrentView('will-editor');
      
    } catch (err) {
      logger.error('Will 조회 실패', err);
      setError('Will 정보를 불러오는데 실패했습니다: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Will 저장 함수
  const saveWill = async (willData) => {
    try {
      setLoading(true);
      setError(null);

      let response;
      
      if (currentUserWill && currentUserWill.id) {
        // 기존 Will 수정
        logger.system('info', 'Will 수정 시작', { willId: currentUserWill.id });
        response = await willAPI.updateWill(currentUserWill.id, willData);
      } else {
        // 새 Will 생성
        logger.system('info', '새 Will 생성 시작');
        response = await willAPI.createWill(willData);
      }

      if (response.success) {
        setSuccessMessage(currentUserWill ? 'Will이 성공적으로 수정되었습니다!' : 'Will이 성공적으로 생성되었습니다!');
        setCurrentView('home');
        setCurrentUserWill(null);
        logger.system('success', 'Will 저장 성공');
      } else {
        throw new Error(response.message || 'Will 저장에 실패했습니다');
      }

    } catch (err) {
      logger.error('Will 저장 실패', err);
      throw err; // WillEditor에서 에러를 처리하도록 재발생
    } finally {
      setLoading(false);
    }
  };

  // Will 편집 취소
  const cancelWillEdit = () => {
    setCurrentView('home');
    setCurrentUserWill(null);
    logger.system('info', 'Will 편집 취소');
  };

  // 토큰 검증 함수
  const verifyToken = async (token) => {
    try {
      const response = await fetch('/api/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data.success ? data.user : null;
    } catch (err) {
      console.error('Token verification error:', err);
      return null;
    }
  };

  // 메뉴 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isMenuOpen && !event.target.closest('.nav-controls')) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMenuOpen]);

  // 컴포넌트가 처음 렌더링될 때 실행
  useEffect(() => {
    
    logger.system('info', 'DMS Frontend 애플리케이션 시작', {
      environment: process.env.NODE_ENV,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });
    
    logger.system('info', '페이지네이션 설정 로드', {
      usersPerPage: config.pagination.usersPerPage,
      maxPageButtons: config.pagination.maxPageButtons,
      debugMode: config.app.debugMode
    });
    

    // 저장된 토큰 확인 및 자동 로그인
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      verifyToken(savedToken).then(user => {
        if (user) {
          setCurrentUser(JSON.parse(savedUser));
          setAuthToken(savedToken);
          setIsAuthenticated(true);
          logger.system('info', '자동 로그인 성공', { userId: user.user_id });
        } else {
          // 토큰이 유효하지 않으면 저장된 정보 삭제
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          logger.system('warn', '저장된 토큰이 유효하지 않음');
        }
      });
    }
    // loading시 사용자 목록 자동 로드 (개발용, 필요시 활성화)
    fetchUsers();
    
    // 개발 모드에서 페이지네이션 설정 정보 출력
    if (config.app.debugMode) {
      logger.debug('system', '디버그 모드 활성화', {
        usersPerPage: config.pagination.usersPerPage,
        maxPageButtons: config.pagination.maxPageButtons,
        environment: process.env.NODE_ENV
      });
    }
  }, []); // 빈 배열 = 한 번만 실행

  // 현재 페이지를 결정하는 함수
  const getCurrentPage = () => {
    // 인증되지 않은 사용자도 홈페이지는 볼 수 있도록 허용
    if (!isAuthenticated && (currentView === 'admin' || currentView === 'will-editor')) {
      return 'login'; // 관리자 페이지나 유언장 편집 접근 시에만 로그인으로 리다이렉트
    }
    
    return currentView;
  };

  return (
    <div className="App">
      {/* 글로벌 로딩 인디케이터 */}
      {loading && <div className="loading">⏳ 로딩 중...</div>}
      
      {/* 글로벌 에러 메시지 */}
      {error && (
        <div className="error-message">
          <p>❌ 오류가 발생했습니다:</p>
          <p>{error}</p>
          <button onClick={() => {
            setError(null);
            logger.system('info', '사용자가 오류 메시지를 닫음');
          }}>닫기</button>
        </div>
      )}
      
      {/* 성공 메시지 */}
      {successMessage && (
        <div className="success-message">
          <p>✅ {successMessage}</p>
          <button onClick={() => {
            setSuccessMessage(null);
            logger.system('info', '사용자가 성공 메시지를 닫음');
          }}>닫기</button>
        </div>
      )}

      {/* 네비게이션 헤더 - 햄버거 메뉴 스타일 */}
      <div className="nav-header">
        <h1 className="app-title">🎯 Dead Man's Switch (DMS)</h1>
        
        {isAuthenticated ? (
          <div className="nav-controls">
            {/* 사용자 정보 표시 */}
            <div className="user-info-display">
              <span className="user-name">{currentUser?.FirstName || currentUser?.firstname} {currentUser?.LastName || currentUser?.lastname}</span>
              <span className="user-id">({currentUser?.user_id})</span>
            </div>
            
            {/* 햄버거 메뉴 버튼 */}
            <button 
              className="hamburger-menu"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="메뉴 열기/닫기"
            >
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
            </button>
            
            {/* 드롭다운 메뉴 */}
            {isMenuOpen && (
              <div className="dropdown-menu">
                <button 
                  onClick={() => {
                    setCurrentView('home');
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'home' ? 'active' : ''}`}
                >
                  🏠 홈
                </button>
                <button 
                  onClick={() => {
                    handleCreateSwitch();
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'will-editor' ? 'active' : ''}`}
                >
                  📝 내 유언장
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('admin');
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'admin' ? 'active' : ''}`}
                >
                  👥 관리자
                </button>
                <hr className="dropdown-divider" />
                <button 
                  onClick={() => {
                    handleLogout();
                    setIsMenuOpen(false);
                  }}
                  className="dropdown-item logout"
                >
                  🚪 로그아웃
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="nav-controls">
            {/* 햄버거 메뉴 버튼 */}
            <button 
              className="hamburger-menu"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="메뉴 열기/닫기"
            >
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
            </button>
            
            {/* 드롭다운 메뉴 */}
            {isMenuOpen && (
              <div className="dropdown-menu">
                <button 
                  onClick={() => {
                    setCurrentView('home');
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'home' ? 'active' : ''}`}
                >
                  🏠 홈
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('login');
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'login' ? 'active' : ''}`}
                >
                  🔐 로그인
                </button>
                <button 
                  onClick={() => {
                    setCurrentView('register');
                    setIsMenuOpen(false);
                  }}
                  className={`dropdown-item ${currentView === 'register' ? 'active' : ''}`}
                >
                  📝 회원가입
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 페이지 내용 */}
      <div className="page-content">
        {getCurrentPage() === 'home' && <DeadManSwitchHome onCreateSwitch={handleCreateSwitch} />}
        {getCurrentPage() === 'login' && <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setCurrentView('register')} />}
  {getCurrentPage() === 'register' && <RegisterPage onRegister={handleRegister} onSwitchToLogin={() => setCurrentView('login')} />}
        {getCurrentPage() === 'will-editor' && isAuthenticated && (
          <WillEditor
            user={currentUser}
            existingWill={currentUserWill}
            onSave={saveWill}
            onCancel={cancelWillEdit}
          />
        )}
        
        {getCurrentPage() === 'admin' && isAuthenticated && (
          <div className="admin-panel">
            {/* 관리자 패널 헤더 */}
            <div className="admin-header">
              <h2>👥 사용자 관리 시스템</h2>
              <p className="admin-description">
                💀 사용자 생존 상태 모니터링 및 자동 메시지 전송 관리
              </p>
            </div>
          


          {/* 로딩 상태 표시 */}
          {loading && <p>⏳ 데이터를 불러오는 중...</p>}

          {/* 에러 상태 표시 */}
          {error && (
            <div className="error-message">
              ❌ 에러: {error}
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
                    name="firstname"
                    value={editingUser.firstname}
                    onChange={handleEditInputChange}
                    placeholder="이름을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>성:</label>
                  <input
                    type="text"
                    name="lastname"
                    value={editingUser.lastname}
                    onChange={handleEditInputChange}
                    placeholder="성을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>이메일:</label>
                  <input
                    type="email"
                    name="email"
                    value={editingUser.email}
                    onChange={handleEditInputChange}
                    placeholder="이메일을 입력하세요"
                  />
                </div>
                
                <div className="form-group">
                  <label>생년월일:</label>
                  <input
                    type="date"
                    name="dob"
                    value={editingUser.dob}
                    onChange={handleEditInputChange}
                  />
                </div>
                
                <div className="form-group">
                  <label>등급:</label>
                  <select
                    name="grade"
                    value={editingUser.grade}
                    onChange={handleEditInputChange}
                  >
                    <option value="Sta">Standard</option>
                    <option value="Gol">Gold</option>
                    <option value="Pre">Premium</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions">
                <button 
                  onClick={updateUser} 
                  disabled={loading || !editingUser.firstname || !editingUser.lastname || !editingUser.email}
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

          {/* Will 모달 */}
          {showWillModal && currentWillUser && (
            <div className="modal-overlay">
              <div className="will-modal">
                <div className="modal-header">
                  <h3>📜 {currentWillUser.firstname} {currentWillUser.lastname}의 Will 정보</h3>
                  <button 
                    onClick={closeWillModal}
                    className="close-button"
                    disabled={loading}
                  >
                    ❌
                  </button>
                </div>
                
                <div className="modal-content">
                  {loading ? (
                    <p>⏳ Will 정보를 불러오는 중...</p>
                  ) : selectedUserWills.length > 0 ? (
                    <div className="will-list">
                      <p className="will-count">총 {selectedUserWills.length}개의 Will이 있습니다.</p>
                      {selectedUserWills.map((will, index) => (
                        <div key={will.id || index} className="will-item">
                          <div className="will-header">
                            <h4>📋 {currentWillUser?.firstname} {currentWillUser?.lastname}'s Will</h4>
                            <div className="will-meta">
                              <span className="will-date">📅 {new Date(will.created_at).toLocaleDateString()}</span>
                              <span className={`status-badge status-${will.status?.toLowerCase() || 'pending'}`}>
                                {will.status || 'PENDING'}
                              </span>
                            </div>
                          </div>
                          <div className="will-content">
                            <p><strong>제목:</strong> {will.subject || '제목 없음'}</p>
                            
                            {/* 수신인 섹션 - 간단한 타일식 표시 */}
                            <div className="recipients-section">
                              <div className="recipients-row">
                                <p className="recipients-label"><strong>수신인:</strong></p>
                                <div className="recipients-tiles">
                                  {willRecipients[will.id] ? (
                                    willRecipients[will.id].length > 0 ? (
                                      willRecipients[will.id].map((recipient, idx) => (
                                        <div key={idx} className="recipient-tile-simple">
                                          👤 {recipient.recipient_name}
                                        </div>
                                      ))
                                    ) : (
                                      <div className="no-recipients">
                                        📭 등록된 수신인이 없습니다.
                                      </div>
                                    )
                                  ) : (
                                    <div className="recipients-loading">
                                      ⏳ 수신인 정보를 불러오는 중...
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                            
                            <p><strong>내용:</strong></p>
                            <div className="will-text">
                              {will.body ? (
                                <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0}}>
                                  {will.body}
                                </pre>
                              ) : (
                                '내용이 없습니다.'
                              )}
                            </div>
                            
                            {will.trigger_date && (
                              <p><strong>발송일:</strong> {new Date(will.trigger_date).toLocaleDateString()}</p>
                            )}

                            {/* DispatchLog 섹션 */}
                            <div className="dispatchlog-section">
                              <p><strong>발송 기록:</strong></p>
                              <div className="dispatchlog-list">
                                {willDispatchLogs[will.id] ? (
                                  willDispatchLogs[will.id].length > 0 ? (
                                    willDispatchLogs[will.id].map((log, idx) => (
                                      <div key={idx} className="dispatchlog-item">
                                        <span className="log-date">
                                          📅 {log.sent_at ? new Date(log.sent_at).toLocaleDateString() : '미발송'}
                                        </span>
                                        <span className="log-time">
                                          🕐 {log.sent_at ? new Date(log.sent_at).toLocaleTimeString() : '-'}
                                        </span>
                                        <span className="log-recipient">👤 {log.recipient_name}</span>
                                        <span className={`log-status status-${log.status?.toLowerCase() || 'pending'}`}>
                                          {log.status?.toUpperCase() || 'PENDING'}
                                        </span>
                                      </div>
                                    ))
                                  ) : (
                                    <div className="no-logs">
                                      📭 발송 기록이 없습니다.
                                    </div>
                                  )
                                ) : (
                                  <div className="logs-loading">
                                    ⏳ 발송 기록을 불러오는 중...
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-will">
                      <p>📭 등록된 Will이 없습니다.</p>
                      <p>이 사용자는 아직 Will을 작성하지 않았습니다.</p>
                    </div>
                  )}
                </div>
                
                <div className="modal-footer">
                  <button 
                    onClick={closeWillModal}
                    className="cancel-button"
                  >
                    닫기
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 트리거 모달 */}
          {showTriggerModal && currentTriggerUser && (
            <div className="modal-overlay">
              <div className="trigger-modal">
                <div className="modal-header">
                  <h3>⏰ {currentTriggerUser.firstname} {currentTriggerUser.lastname}의 트리거 관리</h3>
                  <button 
                    onClick={closeTriggerModal}
                    className="close-button"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="modal-content">
                  {/* 트리거 이력 섹션 */}
                  <div className="trigger-history">
                    <div className="trigger-history-header">
                      <h4>📋 트리거 이력</h4>
                      <button 
                        onClick={openAddTriggerModal}
                        className="add-trigger-button"
                        title="새 트리거 추가"
                      >
                        ➕
                      </button>
                    </div>
                    
                    {userTriggers.length > 0 ? (
                      <div className="trigger-simple-list">
                        {userTriggers.map((trigger, index) => (
                          <div key={trigger.trigger_id || index} className="trigger-simple-item">
                            <span className="trigger-info-text">
                              Type: {trigger.trigger_type || 'manual'} | 
                              Date: {trigger.trigger_date ? new Date(trigger.trigger_date).toLocaleDateString('ko-KR') : '날짜 없음'} | 
                              Status: <span className={`status ${trigger.status?.toLowerCase()}`}>
                                {trigger.status === 'completed' ? '완료' : 
                                 trigger.status === 'pending' ? '대기중' : 
                                 trigger.status === 'failed' ? '실패' : trigger.status || 'pending'}
                              </span>
                            </span>
                            {trigger.status === 'pending' && (
                              <button 
                                onClick={() => startEditTrigger(trigger)}
                                className="edit-trigger-button-simple"
                                title="트리거 편집"
                              >
                                수정
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="no-triggers">
                        <p>🔍 등록된 트리거가 없습니다.</p>
                      </div>
                    )}
                  </div>


                </div>
                
                <div className="modal-footer">
                  <button 
                    onClick={closeTriggerModal}
                    className="cancel-button"
                  >
                    닫기
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 트리거 추가/수정 모달 */}
          {showAddTriggerModal && currentTriggerUser && editingTrigger && (
            <div className="modal-overlay">
              <div className="trigger-add-modal">
                <div className="modal-header">
                  <h3>
                    {editingTrigger.trigger_id ? '✏️ 트리거 수정' : '➕ 새 트리거 추가'}
                    <span className="user-info"> - {currentTriggerUser.firstname} {currentTriggerUser.lastname}</span>
                  </h3>
                  <button 
                    onClick={closeAddTriggerModal}
                    className="close-button"
                    disabled={loading}
                  >
                    ✕
                  </button>
                </div>
                
                <div className="modal-content">
                  <div className="trigger-form">
                    <div className="form-row">
                      <div className="form-group">
                        <label>트리거 타입:</label>
                        <select 
                          name="trigger_type"
                          value={editingTrigger.trigger_type || ''}
                          onChange={handleTriggerInputChange}
                          className="form-control"
                          disabled={loading}
                        >
                          <option value="">타입 선택</option>
                          <option value="email">📧 이메일</option>
                          <option value="sms">📱 SMS</option>
                          <option value="notification">🔔 알림</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label>트리거 날짜:</label>
                        <input 
                          type="date"
                          name="trigger_date"
                          value={editingTrigger.trigger_date || ''}
                          onChange={handleTriggerInputChange}
                          className="form-control"
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="form-group">
                      <label>상태:</label>
                      <select 
                        name="status"
                        value={editingTrigger.status || 'pending'}
                        onChange={handleTriggerInputChange}
                        className="form-control"
                        disabled={loading}
                      >
                        <option value="pending">⏳ 대기중</option>
                        <option value="completed">✅ 완료</option>
                        <option value="failed">❌ 실패</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div className="modal-footer">
                  <button 
                    onClick={saveTrigger}
                    className="save-button"
                    disabled={loading || !editingTrigger.trigger_type || !editingTrigger.trigger_date}
                  >
                    {loading 
                      ? '⏳ 저장 중...' 
                      : editingTrigger.trigger_id ? '💾 수정 완료' : '➕ 트리거 추가'
                    }
                  </button>
                  <button 
                    onClick={closeAddTriggerModal}
                    className="cancel-button"
                    disabled={loading}
                  >
                    ❌ 취소
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 사용자 목록 표시 */}
          {!loading && !error && (
            <div className="users-list">
              <div className="list-header">
                <div className="list-title-row">
                  <h3>👥 사용자 목록 (전체 {users.length}명)</h3>
                  <button 
                    onClick={fetchUsers} 
                    disabled={loading}
                    className="refresh-button-inline"
                  >
                    {loading ? '⏳ 새로고침 중...' : '🔄 목록 새로고침'}
                  </button>
                </div>
                <div className="page-info">
                  📄 페이지 {currentPage} / {totalPages} • 페이지당 {usersPerPage}명 표시
                  {users.length > 0 && (
                    <div className="range-info">
                      (현재 {indexOfFirstUser + 1}-{Math.min(indexOfLastUser, users.length)}번째 표시)
                    </div>
                  )}
                </div>
              </div>
              
              {users.length > 0 ? (
                <div>
                  {/* 리스트 헤더 */}
                  <div className="users-table-header">
                    <div className="table-row header-row">
                      <div className="col-id">ID</div>
                      <div className="col-name">이름</div>
                      <div className="col-email">이메일</div>
                      <div className="col-grade">등급</div>
                      <div className="col-dob">생년월일</div>
                      <div className="col-created">가입일</div>
                      <div className="col-actions">액션</div>
                    </div>
                  </div>
                  
                  {/* 사용자 리스트 */}
                  <div className="users-table">
                    { currentUsers.map((user, index) => (
                      <div key={user.user_id || user.id || index} className="table-row user-row">
                        <div className="user-info">
                          <span className="user-id">#{user.id}</span>
                        </div>
                        <div className="col-name">
                          <div className="user-name">
                            <strong>{user.firstname} {user.lastname}</strong>
                          </div>
                        </div>
                        <div className="col-email">
                          <span className="user-email">📧 {user.email}</span>
                        </div>
                        <div className="col-grade">
                          <span className={`grade-badge grade-${user.grade ? user.grade.toLowerCase() : ''}`}> 
                            🏆 {user.grade === 'Pre' ? 'Premium' : user.grade === 'Gol' ? 'Gold' : user.grade === 'Sta' ? 'Standard' : user.grade}
                          </span>
                        </div>
                        <div className="col-dob">
                          <span className="user-dob">� {user.DOB}</span>
                        </div>
                        <div className="col-created">
                          <span className="user-created">📅 {new Date(user.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="col-actions">
                          <div className="action-buttons-inline">
                            <button 
                              onClick={() => fetchUserWills(user)}
                              className="will-button-small"
                              disabled={loading}
                              title="Will 정보 조회"
                            >
                              📜
                            </button>
                            <button 
                              onClick={() => fetchUserTriggers(user)}
                              className="trigger-button-small"
                              disabled={loading}
                              title="트리거 관리"
                            >
                              ⏰
                            </button>
                            <button 
                              onClick={() => setEditingUser(user)}
                              className="edit-button-small"
                              disabled={loading}
                              title="사용자 정보 수정"
                            >
                              ✏️
                            </button>
                            <button 
                              onClick={() => deleteUser(user.user_id, `${user.firstname} ${user.lastname}`)}
                              className="delete-button-small"
                              disabled={loading}
                              title="사용자 삭제"
                            >
                              🗑️
                            </button>
                          </div>
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
                        {/* 첫 페이지로 가기 (현재 페이지가 시작 범위보다 멀 때) */}
                        {getPageNumbers()[0] > 1 && (
                          <>
                            <button
                              onClick={() => paginate(1)}
                              className="page-number"
                            >
                              1
                            </button>
                            {getPageNumbers()[0] > 2 && <span className="page-ellipsis">...</span>}
                          </>
                        )}
                        
                        {/* 페이지 번호 버튼들 */}
                        {getPageNumbers().map((number) => (
                          <button
                            key={number}
                            onClick={() => paginate(number)}
                            className={`page-number ${currentPage === number ? 'active' : ''}`}
                          >
                            {number}
                          </button>
                        ))}
                        
                        {/* 마지막 페이지로 가기 (현재 페이지가 끝 범위보다 멀 때) */}
                        {getPageNumbers()[getPageNumbers().length - 1] < totalPages && (
                          <>
                            {getPageNumbers()[getPageNumbers().length - 1] < totalPages - 1 && <span className="page-ellipsis">...</span>}
                            <button
                              onClick={() => paginate(totalPages)}
                              className="page-number"
                            >
                              {totalPages}
                            </button>
                          </>
                        )}
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
                </div>
              ) : (
                <p>📭 등록된 사용자가 없습니다.</p>
              )}
            </div>
          )}
          </div>
        )}
      </div>
      {/* 기존 App 렌더링 코드 */}
      <ToastContainer />
    </div>
  );
};

// 이 컴포넌트를 다른 파일에서 사용할 수 있도록 내보냅니다
export default App;