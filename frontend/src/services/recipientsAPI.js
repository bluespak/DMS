// 수신인 API 서비스
import config from '../config/config';

const API_BASE_URL = config.api.baseUrl;

export const recipientsAPI = {
  // 특정 Will의 수신인 목록 조회
  getRecipientsByWillId: async (willId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipients/will/${willId}`, {
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
          recipients: data.data,
          count: data.count
        };
      } else {
        throw new Error(data.message || '수신인 데이터를 가져오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Error fetching recipients:', error);
      return {
        success: false,
        error: error.message,
        recipients: [],
        count: 0
      };
    }
  },

  // 수신인 생성
  createRecipient: async (recipientData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipients`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recipientData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          recipient: data.data
        };
      } else {
        throw new Error(data.message || '수신인 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error creating recipient:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // 수신인 수정
  updateRecipient: async (recipientId, recipientData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipients/${recipientId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recipientData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          recipient: data.data
        };
      } else {
        throw new Error(data.message || '수신인 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error updating recipient:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // 수신인 삭제
  deleteRecipient: async (recipientId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/recipients/${recipientId}`, {
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
        throw new Error(data.message || '수신인 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error deleting recipient:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default recipientsAPI;