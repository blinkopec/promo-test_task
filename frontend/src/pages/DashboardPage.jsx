import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';
import Header from '../components/Header'

export default function DashboardPage() {
    const navigate = useNavigate();

    const [receipts, setReceipts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [totalCount, setTotalCount] = useState(0);

    useEffect(() => {
        (async () => {
            await apiFetch('/api/csrf/');

            const {ok, data} = await apiFetch(`/api/receipts/?page=${currentPage}`);

            if (ok && data) {
                setReceipts(data.results || []);
                setTotalCount(data.count || 0);
                setTotalPages(Math.ceil((data.count || 0) / 10));
            } else {
                setError('Не удалось загрузить чеки');
            }

            setLoading(false);
        })();
    }, [currentPage]);
    return (
        <>
            <Header/>
            <div className="dashboard-page">
                <div className="dashboard-card">
                    <div className="dashboard-header">
                        <h1>История чеков</h1>
                        <div className="badge">Чеков внесено: {totalCount} шт</div>
                    </div>

                    {loading && <div className="dashboard-loading">Загрузка...</div>}

                    {error && <div className="error-message">{error}</div>}

                    {!loading && !error && receipts.length === 0 && (
                        <div className="empty-state">
                            <div className="empty-icon">📄</div>
                            <h2>Здесь будет история ваших чеков</h2>
                            <p className="subtitle">Вы не добавили еще ни одного чека</p>
                            <button
                                className="btn-primary btn-inline"
                                onClick={() => navigate('/receipts/create')}
                            >
                                Зарегистрировать чек
                            </button>
                        </div>
                    )}

                    {!loading && !error && receipts.length > 0 && (
                        <table className="receipts-table">
                        <thead>
                            <tr>
                            <th>Дата покупки</th>
                            <th>Статус</th>
                            <th>Сумма чека</th>
                            <th>Дата регистрации</th>
                            <th>Информация</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                            <td>00:00 00.00.0000</td>
                            <td><span className="status status-pending">В обработке</span></td>
                            <td>12 000 ₽</td>
                            <td>00:00 00.00.0000</td>
                            <td>Чек в обработке</td>
                            </tr>
                        </tbody>
                        </table>
                    )}

                    <div className="dashboard-footer">
                        <div className="info-message">
                            ℹ️ Иногда проверка вашего чека может занять до 5 рабочих дней
                        </div>
                        <button className="btn-primary btn-inline"
                            onClick={() => navigate('/receipts/create')}>
                                Зарегистрировать чек
                        </button>
                    </div>

                    </div>
            </div>
        </>
    );
}