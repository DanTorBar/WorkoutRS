'use client';

import React, { useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

export default function FileUploader({
  serviceType,
  onNext,
  onBack,
}: {
  serviceType: 'google' | 'apple' | 'fitbit' | 'garmin';
  onNext: (data: any) => void;
  onBack: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const instructions: Record<string, string> = {
    google: 'Exporta tu archivo .zip desde Google Fit: abre la app > Configuración > Exportar datos.',
    apple: 'Usa Apple Health en iPhone: exporta tus datos de salud a un ZIP desde la app Salud.',
    fitbit: 'En Fitbit, ve a Cuenta > Sistema > Exportar tus datos en un archivo ZIP.',
    garmin: 'Desde Garmin Connect, ve a Configuración > Exportar datos y descarga el ZIP.',
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    const fd = new FormData();
    fd.append('file', file);
    fd.append('source', serviceType);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}imports/`,
        { method: 'POST', body: fd }
      );
      if (!res.ok) throw new Error('Error al procesar el archivo');
      const data = await res.json();
      onNext(data);
    } catch (err: any) {
      setError(err.message || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-primary text-center">
        {instructions[serviceType]}
      </h2>
      <div
        className="border-2 border-dashed border-border rounded-xl p-10 text-center hover:bg-bg transition relative"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        {loading ? (
          <Loader2 className="mx-auto animate-spin h-8 w-8 text-primary" />
        ) : (
          <p className="text-text">Arrastra aquí tu archivo .zip</p>
        )}
        {error && (
          <div className="flex items-center justify-center mt-4 text-secondary">
            <AlertCircle className="mr-2 h-5 w-5" />
            <span>{error}</span>
          </div>
        )}
      </div>
      <div className="flex justify-between">
        <button onClick={onBack} className="text-secondary hover:underline">
          ← Volver
        </button>
      </div>
    </div>
  );
}
