// DispatchLog API 서비스
import config from '../config/config';

const API_BASE_URL = config.api.baseUrl;

export const dispatchLogAPI = {
  // 특정 Will의 DispatchLog 목록 조회
  getDispatchLogsByWillId: async (willId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dispatch-logs/will/${willId}`, {
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
          logs: data.data,
          count: data.count
        };
      } else {
        throw new Error(data.message || 'DispatchLog 데이터를 가져오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching dispatch logs:', error);
      return {
        success: false,
        error: error.message,
        logs: [],
        count: 0
      };
    }
  },

  // 모든 DispatchLog 조회
  getAllDispatchLogs: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dispatch-logs`, {
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
          logs: data.data,
          count: data.count
        };
      } else {
        throw new Error(data.message || 'DispatchLog 목록을 가져오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching all dispatch logs:', error);
      return {
        success: false,
        error: error.message,
        logs: [],
        count: 0
      };
    }
  }
};

export default dispatchLogAPI;