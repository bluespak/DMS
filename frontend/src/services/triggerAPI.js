// 트리거 API 서비스
import config from '../config/config';

const API_BASE_URL = config.api.baseUrl;

export const triggerAPI = {
  // 특정 사용자의 트리거 목록 조회
  getTriggersByUserId: async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/triggers/user/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          triggers: data.data,
          count: data.count
        };
      } else {
        throw new Error(data.message || '트리거 데이터를 가져오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching triggers:', error);
      return {
        success: false,
        error: error.message,
        triggers: [],
        count: 0
      };
    }
  },

  // 특정 사용자의 대기중인 트리거 조회
  getPendingTriggerByUserId: async (userId) => {
    try {
      console.log('🔍 대기중인 트리거 조회 API 호출:', { url: `${API_BASE_URL}/api/triggers/user/${userId}/pending`, userId });
      
      const response = await fetch(`${API_BASE_URL}/api/triggers/user/${userId}/pending`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('📥 대기중인 트리거 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 대기중인 트리거 HTTP 에러:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 대기중인 트리거 응답 데이터:', data);
      
      if (data.success) {
        return {
          success: true,
          trigger: data.data
        };
      } else {
        throw new Error(data.error || data.message || '대기중인 트리거 조회에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 대기중인 트리거 조회 실패:', error);
      return {
        success: false,
        error: error.message,
        trigger: null
      };
    }
  },

  // 모든 트리거 조회
  getAllTriggers: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/triggers`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          triggers: data.data,
          count: data.count
        };
      } else {
        throw new Error(data.message || '트리거 목록을 가져오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching all triggers:', error);
      return {
        success: false,
        error: error.message,
        triggers: [],
        count: 0
      };
    }
  },

  // 트리거 생성
  createTrigger: async (triggerData) => {
    try {
      console.log('📤 트리거 생성 API 호출:', { url: `${API_BASE_URL}/api/triggers`, data: triggerData });
      
      const response = await fetch(`${API_BASE_URL}/api/triggers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(triggerData),
      });

      console.log('📥 트리거 생성 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 트리거 생성 HTTP 에러:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 트리거 생성 응답 데이터:', data);
      
      if (data.success) {
        return {
          success: true,
          trigger: data.data
        };
      } else {
        throw new Error(data.error || data.message || '트리거 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 트리거 생성 실패:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // 트리거 수정
  updateTrigger: async (triggerId, triggerData) => {
    try {
      console.log('📝 트리거 수정 API 호출:', { url: `${API_BASE_URL}/api/triggers/${triggerId}`, data: triggerData });
      
      const response = await fetch(`${API_BASE_URL}/api/triggers/${triggerId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(triggerData),
      });

      console.log('📥 트리거 수정 응답 상태:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ 트리거 수정 HTTP 에러:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 트리거 수정 응답 데이터:', data);
      
      if (data.success) {
        return {
          success: true,
          trigger: data.data
        };
      } else {
        throw new Error(data.error || data.message || '트리거 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('❌ 트리거 수정 실패:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // 트리거 삭제
  deleteTrigger: async (triggerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/triggers/${triggerId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          message: data.message
        };
      } else {
        throw new Error(data.message || '트리거 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error deleting trigger:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default triggerAPI;