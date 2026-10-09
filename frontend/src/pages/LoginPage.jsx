import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
    const {login} = useAuth();
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    async function onSubmit(e) {
        e.preventDefault();
        setError('');
        setSubmitting(true);

        const res = await login(username, password);

        setSubmitting(false);

        if (res.ok) {
            navigate('/dashboard');
        } else {
            setError(res.error);
        }
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>Вход</h1>
                <p className="subtitle">Войдите, чтобы зарегистрировать чек</p>

                <form onSubmit={onSubmit}>
                    <div className="field">
                        <label htmlFor="username">Логин</label>
                        <input id="username" type="text" placeholder="Введите логин"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>

                    <div className="field">
                        <label htmlFor="password">Пароль</label>
                        <input id="password" type="password" placeholder="Введите пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <div className="error-slot">
                        {error && <div className="error-message">{error}</div>}
                    </div>

                    <button type="submit" className="btn-primary" disabled={submitting}>
                        {submitting ? "Вход..." : "Войти"}
                    </button>
                </form>
            </div>
        </div>
    );
}