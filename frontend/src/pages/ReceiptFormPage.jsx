import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../api';
import Header from '../components/Header';

export default function ReceiptFormPage() {
  const navigate = useNavigate();

  const [config, setConfig] = useState({ promo_start: '', promo_end: '' });
  const [form, setForm] = useState({
    fn: '',
    fd: '',
    fp: '',
    purchase_datetime: '',
    amount: '',
  });
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    (async () => {
      await apiFetch('/api/csrf/');
      const { data } = await apiFetch('/api/config/');
      if (data) setConfig(data);
    })();
  }, []);

  function setField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function isDigits(str, min, max) {
    if (str.length < min || str.length > max) return false;
    for (const ch of str) {
      if (ch < '0' || ch > '9') return false;
    }
    return true;
  }

  function validate() {
    const e = {};

    if (!isDigits(form.fn, 16, 16)) {
      e.fn = 'ФН должен содержать 16 цифр.';
    }

    if (!isDigits(form.fd, 1, 10)) {
      e.fd = 'ФД должен содержать от 1 до 10 цифр.';
    }

    if (!isDigits(form.fp, 1, 10)) {
      e.fp = 'ФП должен содержать от 1 до 10 цифр.';
    }

    if (!form.purchase_datetime) {
      e.purchase_datetime = 'Укажите дату и время покупки.';
    }

    if (!form.amount || Number(form.amount) < 1000) {
      e.amount = 'Сумма должна быть не меньше 1000 ₽.';
    }

    return e;
  }

  async function onSubmit(e) {
    e.preventDefault();
    setGeneralError('');

    const clientErrors = validate();
    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      return;
    }

    setSubmitting(true);

    const { ok, data } = await apiFetch('/api/receipts/', {
      method: 'POST',
      body: JSON.stringify(form),
    });

    setSubmitting(false);

    if (ok && data?.success) {
      setSuccess(true);
      return;
    }

    const serverErrors = {};
    let general = '';

    if (data?.errors) {
      for (const [key, messages] of Object.entries(data.errors)) {
        const text = Array.isArray(messages) ? messages.join(' ') : String(messages);
        if (key === '__all__' || key === 'non_field_errors') {
          general = text;
        } else {
          serverErrors[key] = text;
        }
      }
    }

    setErrors(serverErrors);
    if (general) setGeneralError(general);
    else if (!data?.errors) setGeneralError('Не удалось отправить чек.');
  }

  if (success) {
    return (
      <>
        <Header />
        <div className="receipt-form-page">
          <div className="success-card">
            <div className="success-icon">✓</div>
            <h1>Ваш чек загружен</h1>
            <p className="subtitle">
              Мы уже начали анализировать ваши покупки. Это займет всего пару секунд.
            </p>
            <button
              className="btn-primary btn-inline"
              onClick={() => navigate('/dashboard')}
            >
              На главную
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="receipt-form-page">
        <div className="receipt-form-card">
          <button
            className="close-btn"
            onClick={() => navigate('/dashboard')}
            aria-label="Закрыть"
          >
            ×
          </button>

          <h1>Регистрация чека</h1>
          <p className="subtitle">Введите необходимые данные с чека</p>

          {config.promo_start && config.promo_end && (
            <div className="promo-period">
              Период акции: {config.promo_start} — {config.promo_end}
            </div>
          )}

          {generalError && <div className="error-message">{generalError}</div>}

          <form onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="fn">ФН</label>
              <input
                id="fn"
                type="text"
                placeholder="Введите ФН"
                value={form.fn}
                onChange={(e) => setField('fn', e.target.value)}
              />
              {errors.fn && <div className="error">{errors.fn}</div>}
            </div>

            <div className="field">
              <label htmlFor="fd">Номер чека</label>
              <input
                id="fd"
                type="text"
                placeholder="Введите номер чека (ФД)"
                value={form.fd}
                onChange={(e) => setField('fd', e.target.value)}
              />
              {errors.fd && <div className="error">{errors.fd}</div>}
            </div>

            <div className="field">
              <label htmlFor="fp">ФП</label>
              <input
                id="fp"
                type="text"
                placeholder="Введите ФП"
                value={form.fp}
                onChange={(e) => setField('fp', e.target.value)}
              />
              {errors.fp && <div className="error">{errors.fp}</div>}
            </div>

            <div className="field">
              <label htmlFor="purchase_datetime">Дата покупки</label>
              <input
                id="purchase_datetime"
                type="datetime-local"
                value={form.purchase_datetime}
                onChange={(e) => setField('purchase_datetime', e.target.value)}
              />
              {errors.purchase_datetime && (
                <div className="error">{errors.purchase_datetime}</div>
              )}
            </div>

            <div className="field">
              <label htmlFor="amount">Сумма</label>
              <input
                id="amount"
                type="number"
                step="0.01"
                placeholder="0.00 ₽"
                value={form.amount}
                onChange={(e) => setField('amount', e.target.value)}
              />
              {errors.amount && <div className="error">{errors.amount}</div>}
            </div>

            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Отправка...' : 'Загрузить'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}