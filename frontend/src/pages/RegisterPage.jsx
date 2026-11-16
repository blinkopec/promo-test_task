import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";
import { useAuth } from "../auth/AuthContext";

export default function Register() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [form, setForm] = useState({
    username: "",
    password: "",
    password_confirm: "",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  function onChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setErrors({});

    if (form.password !== form.password_confirm) {
      setErrors({ password_confirm: ["Пароли не совпадают."] });
      return;
    }

    setSubmitting(true);
    const { ok, status, data } = await apiFetch("/api/auth/register/", {
      method: "POST",
      body: JSON.stringify(form),
    });
    setSubmitting(false);

    if (ok) {
      if (setUser && data) setUser(data);
      navigate("/dashboard");
      return;
    }

    if (status === 400 && data) {
      setErrors(data.errors || data);
    } else {
      setErrors({
        non_field_errors: [
          "Не удалось зарегистрироваться. Попробуйте ещё раз.",
        ],
      });
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Регистрация</h1>
        <p className="subtitle">Создайте аккаунт, чтобы регистрировать чеки</p>

        <form onSubmit={onSubmit} noValidate>
          <div className="field">
            <label htmlFor="username">Имя пользователя</label>
            <input
              id="username"
              name="username"
              value={form.username}
              onChange={onChange}
              autoComplete="username"
              required
            />
            {errors.username && (
              <div className="error-message">{errors.username[0]}</div>
            )}
          </div>

          <div className="field">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              name="password"
              value={form.password}
              onChange={onChange}
              autoComplete="new-password"
              required
            />
            {errors.password && (
              <div className="error-message">{errors.password[0]}</div>
            )}
          </div>

          <div className="field">
            <label htmlFor="password_confirm">Повторите пароль</label>
            <input
              id="password_confirm"
              type="password"
              name="password_confirm"
              value={form.password_confirm}
              onChange={onChange}
              autoComplete="new-password"
              required
            />
            {errors.password_confirm && (
              <div className="error-message">{errors.password_confirm[0]}</div>
            )}
          </div>

          <div className="error-slot">
            {errors.non_field_errors && (
              <div className="error-message">{errors.non_field_errors[0]}</div>
            )}
          </div>

          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Регистрация…" : "Зарегистрироваться"}
          </button>
        </form>

        <p className="subtitle">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
}
