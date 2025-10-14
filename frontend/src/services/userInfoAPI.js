// UserInfo API 호출 함수들
import api from './api';

// UserInfo API 함수들
export const userInfoAPI = {
  // ✅ 모든 사용자 조회
  getAllUsers: async () => {
    try {
      const response = await api.get('/api/users');
      return response.data; // Flask에서 반환하는 데이터
    } catch (error) {
      console.error('사용자 목록 조회 실패:', error);
      throw error;
    }
  },

  // ✅ 특정 사용자 조회
  getUserById: async (userId) => {
    try {
      const response = await api.get(`/api/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error(`사용자 ${userId} 조회 실패:`, error);
      throw error;
    }
  },

  // ✅ 새 사용자 생성
  createUser: async (userData) => {
    try {
      const response = await api.post('/api/users', userData);
      return response.data;
    } catch (error) {
      console.error('사용자 생성 실패:', error);
      throw error;
    }
  },

  // ✅ 사용자 정보 수정
  updateUser: async (userId, userData) => {
    try {
      const response = await api.put(`/api/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      console.error(`사용자 ${userId} 수정 실패:`, error);
      throw error;
    }
  },

  // ✅ 사용자 삭제
  deleteUser: async (userId) => {
    try {
      const response = await api.delete(`/api/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error(`사용자 ${userId} 삭제 실패:`, error);
      throw error;
    }
  }
};

export default userInfoAPI;