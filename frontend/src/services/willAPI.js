// Will API 서비스
// Flask backend의 Will 관련 API 호출을 담당합니다

import api from './api';

export const willAPI = {
  // ✅ 모든 Will 조회 (문서에 따라 수정)
  getAllWills: async () => {
    try {
      const response = await api.get('/api/wills');
      return response.data;
    } catch (error) {
      console.error('Will 목록 조회 실패:', error);
      throw error;
    }
  },

  // ✅ 특정 Will 상세 조회
  getWillById: async (willId) => {
    try {
      const response = await api.get(`/api/wills/${willId}`);
      return response.data;
    } catch (error) {
      console.error(`Will ${willId} 조회 실패:`, error);
      throw error;
    }
  },

  // 🔄 특정 사용자의 Will 조회 (모든 Will을 가져와서 필터링)
  getWillsByUserId: async (userId) => {
    try {
      console.log(`📜 사용자 ${userId}의 Will 조회 시작...`);
      
      // 모든 Will을 가져와서 해당 사용자의 Will을 필터링
      const response = await api.get('/api/wills');
      
      // Flask API 응답 구조: { success: true, data: [...], count: ... }
      if (response.data && response.data.success && response.data.data) {
        // 사용자 ID로 필터링 (user_id를 문자열로 비교)
        const userWills = response.data.data.filter(will => 
          will.user_id === userId
        );
        
        console.log(`✅ 사용자 ${userId}의 Will ${userWills.length}개 발견`);
        console.log('📋 발견된 Will 목록:', userWills);
        
        // 각 Will 객체의 필드를 상세히 출력
        userWills.forEach((will, index) => {
          console.log(`📄 Will ${index + 1}:`, {
            id: will.id,
            subject: will.subject,
            body: will.body ? will.body.substring(0, 100) + '...' : 'No body',
            created_at: will.created_at,
            user_id: will.user_id
          });
        });
        
        return {
          success: true,
          data: userWills,
          count: userWills.length
        };
      }
      
      return {
        success: true,
        data: [],
        count: 0
      };
      
    } catch (error) {
      console.error(`사용자 ${userId}의 Will 목록 조회 실패:`, error);
      throw error;
    }
  },

  // ✅ 새 Will 생성
  createWill: async (willData) => {
    try {
      const response = await api.post('/api/wills', willData);
      return response.data;
    } catch (error) {
      console.error('Will 생성 실패:', error);
      throw error;
    }
  },

  // ✅ Will 수정
  updateWill: async (willId, willData) => {
    try {
      const response = await api.put(`/api/wills/${willId}`, willData);
      return response.data;
    } catch (error) {
      console.error(`Will ${willId} 수정 실패:`, error);
      throw error;
    }
  },

  // ✅ Will 삭제
  deleteWill: async (willId) => {
    try {
      const response = await api.delete(`/api/wills/${willId}`);
      return response.data;
    } catch (error) {
      console.error(`Will ${willId} 삭제 실패:`, error);
      throw error;
    }
  }
};