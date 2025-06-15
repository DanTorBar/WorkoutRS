// File: src/app/login/page.tsx
"use client";

import React, { FormEvent, useState } from "react";
import { User, Lock } from "lucide-react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";

export default function LoginPage() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [touched, setTouched] = useState({ u: false, p: false });
  const [error, setError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setTouched({ ...touched, [e.target.name[0]]: true });
  };

  const validUsername = form.username.trim().length > 0;
  const validPass = form.password.length >= 6;
  const isValid = validUsername && validPass;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!isValid) {
      setTouched({ u: true, p: true });
      setError("Por favor, completa todos los campos correctamente.");
      return;
    }
    try {
      setError(null);
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}users/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json();
        if (data.detail) {
          setError(data.detail);
        } else {
          setError("Credenciales inválidas. Por favor, inténtalo de nuevo.");
        }
        return;
      }
      const data = await res.json();
      localStorage.setItem("authToken", data.token);
      window.dispatchEvent(new Event("login"));
      const callbackUrl = searchParams.get("callbackUrl");
      if (callbackUrl) {
        router.push(callbackUrl);
      } else {
        router.push("/");
      }
    } catch (err: any) {
      setError("Ocurrió un error inesperado. Por favor, inténtalo más tarde.");
    }
  };

  return (
    <main
      className="
        relative min-h-[calc(100vh-5rem)]
        bg-gradient-to-br from-bg to-surface
        flex items-center justify-center p-6 overflow-hidden
      "
    >

      <div className="relative w-full max-w-md bg-surface rounded-2xl shadow-2xl p-8 z-10">
        <h2 className="text-2xl font-bold text-primary text-center mb-6">
          Iniciar Sesión
        </h2>
        {error && <p className="text-secondary text-center mb-4">{error}</p>}
        <form onSubmit={handleSubmit} noValidate className="space-y-6">
          {/* Nombre de usuario */}
          <div>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
              <input
                name="username"
                type="text"
                placeholder="Nombre de usuario"
                value={form.username}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`w-full pl-10 p-2 rounded border ${
                  touched.u && !validUsername
                    ? "border-secondary"
                    : "border-border"
                } focus:outline-none focus:ring-2 focus:ring-primary transition`}
                required
              />
            </div>
            {touched.u && !validUsername && (
              <p className="text-secondary text-xs mt-1">
                Introduce un nombre de usuario válido.
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
                placeholder="Contraseña"
                value={form.password}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`w-full pl-10 p-2 rounded border ${
                  touched.p && !validPass ? "border-secondary" : "border-border"
                } focus:outline-none focus:ring-2 focus:ring-primary transition`}
                required
              />
            </div>
            {touched.p && !validPass && (
              <p className="text-secondary text-xs mt-1">
                Mínimo 6 caracteres.
              </p>
            )}
          </div>

          {/* Botón */}
          <button
            type="submit"
            disabled={!isValid}
            className="w-full bg-primary text-surface py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
          >
            Entrar
          </button>
        </form>

        <div className="mt-4 flex justify-center text-sm">
          <Link
            href="/forgot-password"
            className="text-primary hover:text-primary"
          >
            ¿Olvidaste tu contraseña?
          </Link>
        </div>
        <div className="my-6 flex items-center">
          <hr className="flex-grow border-t-2 border-primary" />
          <span className="mx-4 text-primary font-semibold">O</span>
          <hr className="flex-grow border-t-2 border-primary" />
        </div>
        <div className="mt-6 text-center bg-secondary/10 p-4 rounded-lg">
          <p className="text-sm text-text font-medium">
            ¿No tienes cuenta?{" "}
            <Link
              href="/registro"
              className="text-primary font-bold hover:underline"
            >
              Regístrate aquí
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
