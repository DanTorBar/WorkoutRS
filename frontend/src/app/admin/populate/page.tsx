"use client";

import { useState, useEffect, Fragment } from "react";
import { useRouter } from "next/navigation";
import { Dialog, Transition, TransitionChild } from "@headlessui/react";

export default function AdminPopulatePage() {
  const router = useRouter();
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  const [showConfirm, setShowConfirm] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  // Verificar token y rol admin
  useEffect(() => {
    const checkAdmin = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        router.push("/");
        return;
      }
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}users/me/`, {
          method: "GET",
          headers: {
            Authorization: `Token ${token}`,
          },
        });
        if (!res.ok) {
          throw new Error("No autenticado");
        }
        const data = await res.json();
        if (data.is_staff) {
          setIsAdmin(true);
        } else {
          router.push("/");
        }
      } catch (err) {
        console.error("Error comprobando admin:", err);
        router.push("/");
      } finally {
        setLoadingAuth(false);
      }
    };
    checkAdmin();
  }, [router]);

  const handleStartPopulate = () => {
    setResultMessage(null);
    setShowConfirm(true);
  };

  const doPopulate = async () => {
    setProcessing(true);
    setResultMessage(null);
    try {
      const token = localStorage.getItem("authToken");
      if (!token) throw new Error("Token no encontrado");
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}core/populate/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
        }
      );
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Error ${res.status}: ${text}`);
      }
      setResultMessage("Operación completada con éxito. Redirigiendo al inicio.");
    } catch (err: any) {
      console.error("Error al poblar:", err);
      setResultMessage(`Error: ${err.message}`);
    } finally {
      setProcessing(false);
      setShowConfirm(false);
      await new Promise((resolve) => setTimeout(resolve, 1500));
      router.push("/");

    }
  };

  if (loadingAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Verificando permisos...</p>
      </div>
    );
  }

  if (!isAdmin) {
    // Mientras no redirige, opcional mostrar nada
    return null;
  }

  return (
    <div className="max-w-xl mx-auto py-16 px-4 flex flex-col items-center text-center text-primary">
      <svg
        viewBox="0 0 24 24"
        height={200}
        width={200}
        className="mb-8"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
        <g
          id="SVGRepo_tracerCarrier"
          stroke-linecap="round"
          stroke-linejoin="round"
        ></g>
        <g id="SVGRepo_iconCarrier">
          {" "}
          <path
            d="M4 18V6"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          ></path>{" "}
          <path
            d="M20 6V18"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          ></path>{" "}
          <path
            d="M12 10C16.4183 10 20 8.20914 20 6C20 3.79086 16.4183 2 12 2C7.58172 2 4 3.79086 4 6C4 8.20914 7.58172 10 12 10Z"
            stroke="currentColor"
            stroke-width="1.5"
          ></path>{" "}
          <path
            d="M20 12C20 14.2091 16.4183 16 12 16C7.58172 16 4 14.2091 4 12"
            stroke="currentColor"
            stroke-width="1.5"
          ></path>{" "}
          <path
            d="M20 18C20 20.2091 16.4183 22 12 22C7.58172 22 4 20.2091 4 18"
            stroke="currentColor"
            stroke-width="1.5"
          ></path>{" "}
        </g>
      </svg>
      <h1 className="text-2xl font-bold mb-4 text-text">
        Poblar Base de Datos
      </h1>
      <p className="mb-6 text-gray-700">
        Desde aquí puedes iniciar el proceso de poblar la base de datos. Este
        proceso puede tardar varios minutos y consumir recursos.
      </p>

      {resultMessage && (
        <div
          className={`mb-4 p-3 rounded ${
            resultMessage.startsWith("Error")
              ? "bg-red-100 text-red-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {resultMessage}
        </div>
      )}

      <button
        onClick={handleStartPopulate}
        disabled={processing}
        className={`px-4 py-2 rounded font-semibold ${
          processing
            ? "bg-gray-300 text-gray-600 cursor-not-allowed"
            : "bg-primary text-white hover:opacity-90"
        }`}
      >
        {processing ? "Procesando..." : "Iniciar poblar Base de Datos"}
      </button>

      {/* Confirmación mediante Dialog de Headless UI */}
      <Transition appear show={showConfirm} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-50"
          onClose={() => {
            if (!processing) setShowConfirm(false);
          }}
        >
          <TransitionChild
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30" />
          </TransitionChild>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <TransitionChild
                as={Fragment}
                enter="ease-out duration-200"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-150"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    Confirmar operación
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="text-sm text-gray-700">
                      Esta operación tardará varios minutos y puede consumir
                      muchos recursos del servidor. ¿Estás seguro de que quieres
                      continuar?
                    </p>
                  </div>

                  <div className="mt-4 flex justify-end space-x-2">
                    <button
                      type="button"
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                      onClick={() => setShowConfirm(false)}
                      disabled={processing}
                    >
                      Cancelar
                    </button>
                    <button
                      type="button"
                      className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary"
                      onClick={doPopulate}
                      disabled={processing}
                    >
                      {processing ? "Iniciando..." : "Sí, poblar"}
                    </button>
                  </div>
                </Dialog.Panel>
              </TransitionChild>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}
