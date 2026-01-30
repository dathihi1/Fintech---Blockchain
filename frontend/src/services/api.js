import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// NLP API
export const analyzeText = async (text) => {
    const response = await api.post('/nlp/analyze', { text });
    return response.data;
};

export const getKeywords = async () => {
    const response = await api.get('/nlp/keywords');
    return response.data;
};

export const getEmotionTypes = async () => {
    const response = await api.get('/nlp/emotions');
    return response.data;
};

// Alerts API
export const analyzeBehavior = async (data) => {
    const response = await api.post('/alerts/analyze', data);
    return response.data;
};

export const getAlerts = async (userId, activeOnly = false) => {
    const response = await api.get('/alerts', {
        params: { user_id: userId, active_only: activeOnly }
    });
    return response.data;
};

export const acknowledgeAlert = async (alertId) => {
    const response = await api.post(`/alerts/${alertId}/acknowledge`);
    return response.data;
};

// Trades API
export const createTrade = async (tradeData) => {
    const response = await api.post('/trades/', tradeData);
    return response.data;
};

export const getTrades = async (userId, limit = 50) => {
    const response = await api.get('/trades/', {
        params: { user_id: userId, limit }
    });
    return response.data;
};

export const updateTrade = async (tradeId, data) => {
    const response = await api.patch(`/trades/${tradeId}`, data);
    return response.data;
};

export const closeTrade = async (tradeId, exitPrice, exitNotes = null) => {
    const response = await api.patch(`/trades/${tradeId}`, {
        exit_price: exitPrice,
        notes: exitNotes
    });
    return response.data;
};

// Analysis API
export const getPassiveAnalysis = async (userId, limit = 100) => {
    const response = await api.get('/analysis/passive', {
        params: { limit }
    });
    return response.data;
};

export const getAnalysisSummary = async (userId) => {
    const response = await api.get(`/analysis/summary/${userId}`);
    return response.data;
};

export const getTradeStats = async (userId) => {
    const response = await api.get('/analysis/stats');
    return response.data;
};

export const getAlertStats = async (userId) => {
    const response = await api.get('/alerts/stats');
    return response.data;
};

// Symbols API
export const searchSymbols = async (query, limit = 10) => {
    const response = await api.get('/symbols/search', {
        params: { q: query, limit }
    });
    return response.data;
};

export const getPopularSymbols = async (limit = 20) => {
    const response = await api.get('/symbols/popular', {
        params: { limit }
    });
    return response.data;
};

export const getUserSymbols = async (userId) => {
    const response = await api.get(`/symbols/user/${userId}`);
    return response.data;
};

export default api;

