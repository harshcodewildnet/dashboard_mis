import axios from 'axios';

const API_URL = 'http://3.88.55.152:8000';

export interface User {
    email: string;
    role: string;
    department_key: string | null;
    cost_centre_parent: string | null;
}

class AuthService {
    private token: string | null = localStorage.getItem('token');
    private user: User | null = null;

    constructor() {
        if (this.token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        }
    }

    setToken(token: string) {
        this.token = token;
        localStorage.setItem('token', token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }

    getToken() {
        return this.token;
    }

    async login(email: string, pass: string) {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', pass);

        const response = await axios.post(`${API_URL}/token`, params);
        this.setToken(response.data.access_token);
        return this.fetchMe();
    }

    async fetchMe(): Promise<User> {
        const response = await axios.get(`${API_URL}/api/me`);
        this.user = response.data as User;
        return this.user;
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
    }

    isAuthenticated() {
        return !!this.token;
    }

    getUser() {
        return this.user;
    }
}

export const auth = new AuthService();
