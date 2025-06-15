import { useEffect } from "react";
import Link from "next/link";
import { FaUserLock } from "react-icons/fa6";
import { IoMdClose } from "react-icons/io";


interface AccessDeniedModalProps {
  onClose: () => void;
}

export default function AccessDeniedModal({ onClose }: AccessDeniedModalProps) {
  // Ruta actual para callback a login
  const currentPath =
    typeof window !== "undefined"
      ? window.location.pathname + window.location.search
      : "/";

  // Desactivar scroll del body mientras el modal esté abierto
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, []);

  const handleClose = () => {
    onClose();
  };

  const handleBackdropClick = () => {
    handleClose();
  };

  const stopPropagation = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={handleBackdropClick}
    >
      {/* Fondo semitransparente + blur */}
      <div className="absolute inset-0 bg-black bg-opacity-40 backdrop-blur-sm" />

      {/* Contenedor del modal */}
      <div
        className="relative w-full max-w-md bg-surface rounded-2xl shadow-2xl p-8 z-10 border-2 border-primary"
        onClick={stopPropagation}
      >
        {/* Botón cerrar */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-text hover:text-primary"
          aria-label="Cerrar"
        >
          <IoMdClose size={20} />
        </button>

        <div className="flex flex-col items-center mb-4">
          <FaUserLock className="text-5xl text-primary mb-2" />
          <h2 className="text-2xl font-bold text-primary mb-2 text-center">
            Acceso restringido
          </h2>
        </div>
        <p className="mb-6 text-text text-center text-base">
          Debes iniciar sesión para usar esta funcionalidad.
        </p>
        <Link
          href={`/login?callbackUrl=${encodeURIComponent(currentPath)}`}
          className="w-full block bg-primary text-surface py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 text-center"
        >
          Ir al inicio de sesión
        </Link>
      </div>
    </div>
  );
}
