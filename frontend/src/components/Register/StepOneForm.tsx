"use client";

import React, { FormEvent, useState } from "react";
import { User, Mail, Lock } from "lucide-react";

export default function StepOneForm({ onNext }: { onNext: (form: any) => void }) {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [touched, setTouched] = useState({ u: false, e: false, p: false });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) =>
    setTouched({ ...touched, [e.target.name[0]]: true });

  const validEmail = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email);
  const validPass = form.password.length >= 8;
  const validUser = form.username.trim() !== "";
  const isValid = validUser && validEmail && validPass;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (isValid) onNext(form);
    else setTouched({ u: true, e: true, p: true });
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} noValidate className="space-y-6">
        <h2 className="text-2xl font-bold text-primary text-center">
          ¡Crea tu cuenta!
        </h2>

        {/* Usuario */}
        <div>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="username"
              placeholder="Nombre de usuario"
              value={form.username}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full pl-10 p-2 rounded border ${
                touched.u && !validUser ? "border-secondary" : "border-border"
              } focus:outline-none focus:ring-2 focus:ring-primary transition`}
            />
          </div>
          {touched.u && !validUser && (
            <p className="text-secondary text-xs mt-1">
              El nombre de usuario es obligatorio.
            </p>
          )}
        </div>

        {/* Email */}
        <div>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="email"
              type="email"
              placeholder="Correo electrónico"
              value={form.email}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full pl-10 p-2 rounded border ${
                touched.e && !validEmail ? "border-secondary" : "border-border"
              } focus:outline-none focus:ring-2 focus:ring-primary transition`}
            />
          </div>
          {touched.e && !validEmail && (
            <p className="text-secondary text-xs mt-1">
              Introduce un email válido.
            </p>
          )}
        </div>

        {/* Contraseña */}
        <div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="password"
              type="password"
              placeholder="Contraseña (mín. 8 caracteres)"
              value={form.password}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full pl-10 p-2 rounded border ${
                touched.p && !validPass ? "border-secondary" : "border-border"
              } focus:outline-none focus:ring-2 focus:ring-primary transition`}
            />
          </div>
          {touched.p && !validPass && (
            <p className="text-secondary text-xs mt-1">
              Debe tener al menos 8 caracteres.
            </p>
          )}
        </div>

        {/* Botón */}
        <button
          type="submit"
          disabled={!isValid}
          className="w-full bg-primary text-surface py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
        >
          Continuar
        </button>
      </form>
    </div>
  );
}
