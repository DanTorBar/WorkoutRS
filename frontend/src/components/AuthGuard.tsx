import React, { useEffect, useState } from "react";

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode; // Optional: custom fallback/modal
}

export default function AuthGuard({ children, fallback }: AuthGuardProps) {
  const [isAuth, setIsAuth] = useState<boolean | null>(null);

  useEffect(() => {
    // Puedes cambiar esto por tu lógica real de autenticación
    const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
    setIsAuth(!!token);
  }, []);

  if (!isAuth) {
    // Modal de acceso restringido
    return fallback ? (
      fallback
    ) : (
      <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
        <div className="bg-white rounded-lg p-8 shadow-lg text-center max-w-xs">
          <h2 className="text-xl font-bold mb-2 text-primary">Acceso restringido</h2>
          <p className="mb-4 text-text">Debes iniciar sesión para ver esta página.</p>
          <a
            href="/login"
            className="inline-block bg-primary text-white px-4 py-2 rounded hover:bg-primary/80 transition"
          >
            Ir a login
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
