import Header from '../components/Header'

export default function DashboardPage() {

    return (
        <>
            <Header/>
            <div className="dashboard-page">
                <div className="dashboard-card">
                    <div className="dashboard-header">
                        <h1>История чеков</h1>
                        <div className="badge">Чеков внесено: 0 шт</div>
                    </div>

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


                    <div className="dashboard-footer">
                        <div className="info-message">
                            ℹ️ Иногда проверка вашего чека может занять до 5 рабочих дней
                        </div>
                        <button className="btn-primary btn-inline">Зарегистрировать чек</button>
                    </div>

                </div>
            </div>
        </>
    );
}