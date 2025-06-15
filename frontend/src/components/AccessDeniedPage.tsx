import Link from "next/link";
import { FaUserLock } from "react-icons/fa6";
import { useRouter } from "next/navigation";


export default function AccessDeniedPage() {
  const router = useRouter();
  const currentPath = typeof window !== "undefined" ? window.location.pathname + window.location.search : "/";
  return (
    <main
      className="relative min-h-[calc(100vh-5rem)] bg-gradient-to-br from-bg to-surface flex items-center justify-center p-6 overflow-hidden"
    >
      <div className="relative w-full max-w-md bg-surface rounded-2xl shadow-2xl p-8 z-10 border-2 border-primary">
        <div className="flex flex-col items-center mb-4">
          <FaUserLock className="text-5xl text-primary mb-2" />
          <h2 className="text-2xl font-bold text-primary mb-2 text-center">
            Acceso restringido
          </h2>
        </div>
        <p className="mb-6 text-text text-center text-base">
          Debes iniciar sesión para ver esta página.
        </p>
        <Link
          href={`/login?callbackUrl=${encodeURIComponent(currentPath)}`}
          className="w-full block bg-primary text-surface py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 text-center"
        >
          Ir al inicio de sesión
        </Link>
      </div>
    </main>
  );
}
