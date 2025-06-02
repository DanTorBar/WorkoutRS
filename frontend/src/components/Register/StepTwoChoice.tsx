'use client';

import React from 'react';
import { Upload, Pencil } from 'lucide-react';

export default function StepTwoChoice({
  onSelect,
  onBack,
}: {
  onSelect: (v: 'file' | 'manual') => void;
  onBack: () => void;
}) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-primary text-center">
        Configura tu perfil de salud
      </h2>
      <div className="grid grid-cols-1 gap-4">
        <div
          onClick={() => onSelect('file')}
          className="cursor-pointer border border-border rounded-lg p-6 flex items-center gap-4 hover:shadow-lg transition"
        >
          <Upload className="w-6 h-6 text-primary" />
          <span className="text-text">Subir archivo .zip (servicios externos)</span>
        </div>
        <div
          onClick={() => onSelect('manual')}
          className="cursor-pointer border border-border rounded-lg p-6 flex items-center gap-4 hover:shadow-lg transition"
        >
          <Pencil className="w-6 h-6 text-primary" />
          <span className="text-text">Introducir datos manualmente</span>
        </div>
      </div>
      <button onClick={onBack} className="text-secondary hover:underline">
        ← Volver
      </button>
    </div>
  );
}
