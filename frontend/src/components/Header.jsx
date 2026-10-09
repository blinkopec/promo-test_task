import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Header() {
    const {user, logout} = useAuth();
    const navigate = useNavigate();

    async function handleLogout() {
        await logout();
        navigate('/login')
    }

    return (
        <header className='header'>
            <div className='header-left'>
                <div className="logo-box">ЛОГО</div>
                <button className="link-btn">← На сайт</button>
            </div>
            <nav className='header-nav'>
                <span className='nav-item active'>Личный кабинет</span>
                <span className="nav-item">Правила</span>
                <span className="nav-item">Профиль</span>
            </nav>
            <div className="header-right">
        <button className="icon-btn" aria-label="Уведомления">🔔</button>
        <div className="user-info">
            <div className="avatar">{user?.username?.[0]?.toUpperCase() || '?'}</div>
            <div className="user-text">
                <div className="user-name">{user?.username || 'Гость'}</div>
                <div className="user-email">email@example.com</div>
            </div>
            </div>
            <button className="btn-logout" onClick={handleLogout}>Выйти</button>
        </div>
        </header>
    )
}