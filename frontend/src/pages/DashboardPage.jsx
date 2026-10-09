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
                    <>
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
                            {receipts.map((receipt) => (
                            <tr key={receipt.id}>
                                <td>{new Date(receipt.purchase_datetime).toLocaleString('ru-RU')}</td>
                                <td>
                                <span className={`status status-${receipt.status}`}>
                                    {receipt.status_display}
                                </span>
                                </td>
                                <td>{receipt.amount} ₽</td>
                                <td>{new Date(receipt.created_at).toLocaleString('ru-RU')}</td>
                                <td>
                                {receipt.status === 'rejected'
                                    ? receipt.rejection_reason
                                    : receipt.status === 'pending'
                                    ? 'Чек в обработке'
                                    : 'Чек принят'}
                                </td>
                            </tr>
                            ))}
                        </tbody>
                        </table>

                        {totalPages > 1 && (
                        <div className="pagination">
                            <button
                            className="page-btn"
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage(currentPage - 1)}
                            >
                            ‹
                            </button>

                            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                            <button
                                key={page}
                                className={`page-btn ${page === currentPage ? 'active' : ''}`}
                                onClick={() => setCurrentPage(page)}
                            >
                                {page}
                            </button>
                            ))}

                            <button
                            className="page-btn"
                            disabled={currentPage === totalPages}
                            onClick={() => setCurrentPage(currentPage + 1)}
                            >
                            ›
                            </button>
                        </div>
                        )}
                    </>
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