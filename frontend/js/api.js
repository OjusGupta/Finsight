// frontend/js/api.js
const API_BASE = '/api/v1';

async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Fetch Error:', error);
        throw error;
    }
}

window.api = {
    getStores: () => fetchAPI('/stores/'),
    getSales: () => fetchAPI('/sales/'),
    getAnomalies: () => fetchAPI('/anomalies/'),
    getDailyMetrics: () => fetchAPI('/analytics/daily-store/'),
    chat: (message) => fetchAPI('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ message })
    })
};
