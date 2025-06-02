'use client';

import React, { FormEvent, useState } from 'react';
import { User, Calendar, Users, Weight, Ruler } from 'lucide-react';

type Props = {
  defaultValues?: {
    first_name?: string;
    last_name?: string;
    birth_date?: string;
    gender?: string;
    weight?: string;
    height?: string;
  };
  onBack?: () => void;
};

export default function HealthProfileForm({ defaultValues = {}, onBack }: Props) {
  const [form, setForm] = useState({
    first_name: defaultValues.first_name || '',
    last_name:  defaultValues.last_name  || '',
    birth_date: defaultValues.birth_date || '',
    gender:     defaultValues.gender     || '',
    weight:     defaultValues.weight     || '',
    height:     defaultValues.height     || '',
  });

  const [touched, setTouched] = useState({
    f: false,
    d: false,
    g: false,
    w: false,
    h: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    // field keys: first_name -> 'f', birth_date -> 'd', gender -> 'g', weight -> 'w', height -> 'h'
    const key = { first_name: 'f', birth_date: 'd', gender: 'g', weight: 'w', height: 'h' }[e.target.name];
    if (key) setTouched({ ...touched, [key]: true });
  };

  // Validaciones
  const validName   = form.first_name.trim() !== '';
  const validDate   = /^\d{4}-\d{2}-\d{2}$/.test(form.birth_date);
  const validGender = ['male','female','other'].includes(form.gender);
  const validWeight = parseFloat(form.weight) > 0;
  const validHeight = parseFloat(form.height) > 0;
  const isValid     = validName && validDate && validGender && validWeight && validHeight;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!isValid) {
      setTouched({ f: true, d: true, g: true, w: true, h: true });
      return;
    }
    // Aquí envías `form` al backend
    console.log('Perfil final:', form);
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6">
      <h2 className="text-2xl font-bold text-primary text-center">
        Completa tu perfil de salud
      </h2>

      {/* Nombre */}
      <div>
          <div className="relative">
        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
        <input
          name="first_name"
          placeholder="Nombre"
          value={form.first_name}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full pl-10 p-2 rounded border ${
            touched.f && !validName ? 'border-secondary' : 'border-border'
          } focus:outline-none focus:ring-2 focus:ring-primary transition`}
          required
        />
        </div>
        {touched.f && !validName && (
          <p className="text-secondary text-xs mt-1">
            El nombre es obligatorio.
          </p>
        )}
      </div>

      {/* Apellidos */}
      <div className="relative">
        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
        <input
          name="last_name"
          placeholder="Apellidos (opcional)"
          value={form.last_name}
          onChange={handleChange}
          className="w-full pl-10 p-2 rounded border border-border focus:outline-none focus:ring-2 focus:ring-primary transition"
        />
      </div>

      {/* Fecha de nacimiento */}
      <div>
          <div className="relative">
        <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
        <input
          name="birth_date"
          type="date"
          value={form.birth_date}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full pl-10 p-2 rounded border ${
            touched.d && !validDate ? 'border-secondary' : 'border-border'
          } focus:outline-none focus:ring-2 focus:ring-primary transition`}
          required
        />
        </div>
        {touched.d && !validDate && (
          <p className="text-secondary text-xs mt-1">
            Introduce una fecha válida.
          </p>
        )}
      </div>

      {/* Género */}
      <div>
          <div className="relative">
        <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
        <select
          name="gender"
          value={form.gender}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full pl-10 p-2 rounded border ${
            touched.g && !validGender ? 'border-secondary' : 'border-border'
          } focus:outline-none focus:ring-2 focus:ring-primary transition`}
          required
        >
          <option value="">Selecciona género</option>
          <option value="male">Masculino</option>
          <option value="female">Femenino</option>
          <option value="other">Otro</option>
        </select>
        </div>
        {touched.g && !validGender && (
          <p className="text-secondary text-xs mt-1">
            Debes elegir un género.
          </p>
        )}
      </div>

      {/* Peso */}
      <div>
          <div className="relative">
        <Weight className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary w-[22px]" />
        <input
          name="weight"
          type="number"
          placeholder="Peso (kg)"
          value={form.weight}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full pl-10 p-2 rounded border ${
            touched.w && !validWeight ? 'border-secondary' : 'border-border'
          } focus:outline-none focus:ring-2 focus:ring-primary transition`}
          required
        />
        </div>
        {touched.w && !validWeight && (
          <p className="text-secondary text-xs mt-1">
            Introduce un peso válido.
          </p>
        )}
      </div>

      {/* Altura */}
      <div>
          <div className="relative">
        <Ruler className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary w-[22px]" />
        <input
          name="height"
          type="number"
          placeholder="Altura (cm)"
          value={form.height}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`w-full pl-10 p-2 rounded border ${
            touched.h && !validHeight ? 'border-secondary' : 'border-border'
          } focus:outline-none focus:ring-2 focus:ring-primary transition`}
          required
        />
        </div>
        {touched.h && !validHeight && (
          <p className="text-secondary text-xs mt-1">
            Introduce una altura válida.
          </p>
        )}
      </div>

      {/* Botones */}
      <div className="space-y-4">
        <button
          type="submit"
          disabled={!isValid}
          className="w-full bg-primary text-surface py-2 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
        >
          Registrar
        </button>
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            className="w-full text-secondary hover:underline"
          >
            ← Volver
          </button>
        )}
      </div>
    </form>
  );
}
