import { useEffect, useState } from 'react';
import { apiFetch } from '../api';
import Header from '../components/Header';

export default function ReceiptFormPage() {
  const [config, setConfig] = useState({ promo_start: '', promo_end: ''})
  const [form, setForm] = useState({
    fn: '',
    fd: '',
    fp: '',
    purchase_datetime: '',
    amount: '',
  });

  useEffect(() => {
    (async () => {
      await apiFetch('/api/csrf/');
      const {data} = await apiFetch('/api/config');
      if (data) setConfig(data);
    })();
  }, []);

  function setField(name, value) {
    setForm((prev) => ({ ...prev, [name]:value}));
  }

  return (
    <>
      <Header />
      <div className="receipt-form-page">
        <div className="receipt-form-card">
          <button className="close-btn" aria-label="Закрыть">×</button>

          <h1>Регистрация чека</h1>
          <p className="subtitle">Введите необходимые данные с чека</p>

          <div className="promo-period">
             Период акции: {config.promo_start} — {config.promo_end}
          </div>

          <form>
            <div className="field">
              <label htmlFor="fn">ФН</label>
              <input id="fn" type="text" placeholder="Введите ФН" 
                value={form.fn}
                onChange={(e) => setField('fn', e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="fd">Номер чека</label>
              <input id="fd" type="text" placeholder="Введите номер чека (ФД)" 
                  value={form.fd}
                  onChange={(e) => setField('fd', e.target.value)}    
              />
            </div>

            <div className="field">
              <label htmlFor="fp">ФП</label>
              <input id="fp" type="text" placeholder="Введите ФП" 
                  value={form.fp}
                  onChange={(e) => setField('fp', e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="purchase_datetime">Дата покупки</label>
              <input id="purchase_datetime" type="datetime-local" 
                value={form.purchase_datetime}
                onChange={(e) => setField('purchase_datetime', e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="amount">Сумма</label>
              <input id="amount" type="number" step="0.01" placeholder="0.00 ₽" 
                value={form.amount}
                onChange={(e) => setField('amount', e.target.value)}
              />
            </div>

            <button type="button" className="btn-primary">Загрузить</button>
          </form>
        </div>
      </div>
    </>
  );
}