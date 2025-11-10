import axios from "axios";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE,
    withCredentials: true,
});

// Add token from localStorage to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('spotify_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;