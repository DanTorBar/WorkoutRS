'use client';

import React, { FormEvent, useState } from 'react';
import { User, Calendar, Users, Weight, Ruler } from 'lucide-react';

// Opciones extraídas del modelo backend
const GOAL_CHOICES = [
  "Mejora de la resistencia",
  "Pérdida de peso",
  "Mantenimiento de la salud",
  "Mejorar la salud mental",
  "Aumentar la fuerza",
  "Ganancia muscular",
  "Preparación deportiva",
  "Mejora de la flexibilidad",
  "Mejorar la movilidad",
  "Mejorar la postura",
  "Rehabilitación tras lesión"
];
const CONDITION_CHOICES = [
  "Ninguna",
  "Hipertensión",
  "Diabetes",
  "Asma",
  "Dolor de espalda",
  "Lesión de rodilla",
  "Embarazo",
  "Osteoporosis",
  "Artritis",
  "Enfermedad cardíaca",
  "Sobrepeso",
  "Ansiedad",
  "Depresión",
  "EPOC",
  "Escoliosis",
  "Lesión",
  "Otra"
];
const EQUIPMENT_CHOICES = [
  "Mancuernas",
  "Barras",
  "Máquinas",
  "Poleas",
  "Bandas elásticas",
  "Kettlebell",
  "TRX",
  "Banco",
  "Esterilla",
  "Cuerda saltadora",
  "Balón medicinal"
];
const ENVIRONMENT_CHOICES = [
  "Casa",
  "Gimnasio",
  "Aire libre"
];
const ACTIVITY_LEVEL_CHOICES = [
  { value: 0, label: "0 – Sedentario (poca o ninguna actividad)" },
  { value: 1, label: "1 – Muy bajo (actividad ligera ocasional)" },
  { value: 2, label: "2 – Bajo (ejercicio ligero 1-2 días/semana)" },
  { value: 3, label: "3 – Moderado (ejercicio moderado 3-4 días/semana)" },
  { value: 4, label: "4 – Alto (ejercicio vigoroso 4-5 días/semana)" },
  { value: 5, label: "5 – Muy alto (ejercicio muy intenso diario)" },
];

// Icono para indicar autocompletado
const AutoIcon = () => (
  <span
    title="Obtenido de la importación."
    className="ml-2 text-primary/80 align-middle inline-flex items-center"
    style={{ cursor: 'help', verticalAlign: 'middle' }}
  >
    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor" className="inline-block align-middle"><path d="M10 2l2.39 4.84L18 7.27l-4 3.89L14.78 18 10 15.27 5.22 18 6 11.16l-4-3.89 5.61-.43z"/></svg>
    <span className="sr-only">Campo autocompletado</span>
  </span>
);

// Mejor tipado y manejo seguro para los checkboxes multi-select
const MULTI_FIELDS = ['goals', 'conditions', 'equipment', 'environment'] as const;

type MultiField = typeof MULTI_FIELDS[number];

type FormType = {
  first_name: string;
  last_name: string;
  birth_date: string;
  gender: string;
  weight: string;
  height: string;
  goals: string[];
  conditions: string[];
  equipment: string[];
  environment: string[];
  neat_level: number;
  cardio_mod_level: number;
  cardio_vig_level: number;
  strength_level: number;
};

export default function HealthProfileForm({ defaultValues = {}, onBack, onSubmit, loading, error }: any) {
  const [step, setStep] = useState(0); // 0: básicos, 1: físicos, 2: objetivos, 3: entorno/equipamiento, 4: actividad
  const [form, setForm] = useState<FormType>({
    first_name: defaultValues.first_name || '',
    last_name:  defaultValues.last_name  || '',
    birth_date: (defaultValues.birth_date || defaultValues.date_of_birth || '').slice(0, 10),
    gender:     defaultValues.gender ? String(defaultValues.gender).toLowerCase() : '',
    weight:     defaultValues.weight     || '',
    height:     defaultValues.height     || '',
    goals:      defaultValues.goals ? (Array.isArray(defaultValues.goals) ? defaultValues.goals : defaultValues.goals.split(',')) : [],
    conditions: defaultValues.conditions ? (Array.isArray(defaultValues.conditions) ? defaultValues.conditions : defaultValues.conditions.split(',')) : [],
    equipment:  defaultValues.equipment ? (Array.isArray(defaultValues.equipment) ? defaultValues.equipment : defaultValues.equipment.split(',')) : [],
    environment: defaultValues.environment ? (Array.isArray(defaultValues.environment) ? defaultValues.environment : defaultValues.environment.split(',')) : [],
    neat_level: defaultValues.neat_level ?? 0,
    cardio_mod_level: defaultValues.cardio_mod_level ?? 0,
    cardio_vig_level: defaultValues.cardio_vig_level ?? 0,
    strength_level: defaultValues.strength_level ?? 0,
  });

  React.useEffect(() => {
    setForm(f => ({
      ...f,
      ...Object.fromEntries(
        Object.entries(defaultValues).filter(
          ([k, v]) =>
            v &&
            (
              !f[k as keyof typeof f] ||
              (typeof f[k as keyof typeof f] === 'string' && f[k as keyof typeof f] === '') ||
              (
                (Array.isArray(f[k as keyof typeof f]) && (f[k as keyof typeof f] as any[]).length === 0) ||
                (typeof f[k as keyof typeof f] === 'string' && (f[k as keyof typeof f] as string).length === 0) ||
                (typeof f[k as keyof typeof f] === 'number' && !f[k as keyof typeof f])
              )
            )
        )
      ),
      birth_date: (defaultValues.birth_date || defaultValues.date_of_birth || '').slice(0, 10),
      gender: defaultValues.gender ? String(defaultValues.gender).toLowerCase() : f.gender,
    }));
  }, [defaultValues]);

  // Detecta qué campos han sido autocompletados
  const autoFilled = React.useMemo(() => ({
    neat_level: defaultValues.imported_neat_min !== undefined,
    cardio_mod_level: defaultValues.imported_cardio_mod_min !== undefined,
    cardio_vig_level: defaultValues.imported_cardio_vig_min !== undefined,
    strength_level: defaultValues.imported_strength_min !== undefined,
  }), [defaultValues]);

  // Validaciones por paso
  const validStep = [
    // Paso 0: básicos
    form.first_name.trim() !== '' && /^\d{4}-\d{2}-\d{2}$/.test(form.birth_date) && ['masculino','femenino','otro','desconocido'].includes(form.gender),
    // Paso 1: físicos
    parseFloat(form.weight) > 0 && parseFloat(form.height) > 0,
    // Paso 2: objetivos/condiciones
    form.goals.length > 0,
    // Paso 3: entorno/equipamiento
    form.environment.length > 0 && form.equipment.length > 0,
    // Paso 4: actividad
    [form.neat_level, form.cardio_mod_level, form.cardio_vig_level, form.strength_level].every(v => v >= 0 && v <= 5),
  ];

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox' && MULTI_FIELDS.includes(name as MultiField)) {
      const checked = (e.target as HTMLInputElement).checked;
      setForm(f => {
        const arr = Array.isArray(f[name as MultiField]) ? f[name as MultiField] : [];
        return {
          ...f,
          [name]: checked ? [...arr, value] : arr.filter((v: string) => v !== value)
        };
      });
    } else {
      setForm(f => ({ ...f, [name]: value }));
    }
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setForm(f => ({ ...f, [e.target.name]: Number(e.target.value) }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!validStep[step]) return;
    if (step < 4) setStep(step + 1);
    else if (onSubmit) {
      // Convierte arrays a string separados por coma para el backend
      onSubmit({
        ...form,
        goals: Array.isArray(form.goals) ? form.goals.join(',') : form.goals,
        conditions: Array.isArray(form.conditions) ? form.conditions.join(',') : form.conditions,
        equipment: Array.isArray(form.equipment) ? form.equipment.join(',') : form.equipment,
        environment: Array.isArray(form.environment) ? form.environment.join(',') : form.environment,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6">
      <h2 className="text-2xl font-bold text-primary text-center">
        Completa tu perfil de salud
      </h2>
      {step === 0 && (
        <>
          {/* Nombre, Apellidos, Fecha, Género */}
          <div className="relative mb-2">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="first_name"
              placeholder="Nombre"
              value={form.first_name}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
              required
            />
            {autoFilled.first_name && <AutoIcon />}
          </div>
          <div className="relative mb-2">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="last_name"
              placeholder="Apellidos (opcional)"
              value={form.last_name}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
            />
            {autoFilled.last_name && <AutoIcon />}
          </div>
          <div className="relative mb-2">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <input
              name="birth_date"
              type="date"
              value={form.birth_date}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
              required
            />
            {autoFilled.birth_date && <AutoIcon />}
          </div>
          <div className="relative mb-2">
            <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary" />
            <select
              name="gender"
              value={form.gender}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
              required
            >
              <option value="">Selecciona género</option>
              <option value="masculino">Masculino</option>
              <option value="femenino">Femenino</option>
              <option value="otro">Otro</option>
              <option value="desconocido">Desconocido</option>
            </select>
            {autoFilled.gender && <AutoIcon />}
          </div>
        </>
      )}
      {step === 1 && (
        <>
          {/* Peso, Altura */}
          <div className="relative mb-2 flex items-center">
            <Weight className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary w-[22px]" />
            <input
              name="weight"
              type="number"
              placeholder="Peso (kg)"
              value={form.weight}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
              required
            />
            {autoFilled.weight && <AutoIcon />}
          </div>
          <div className="relative mb-2 flex items-center">
            <Ruler className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary w-[22px]" />
            <input
              name="height"
              type="number"
              placeholder="Altura (cm)"
              value={form.height}
              onChange={handleChange}
              className="w-full pl-10 p-2 rounded border border-border"
              required
            />
            {autoFilled.height && <AutoIcon />}
          </div>
        </>
      )}
      {step === 2 && (
        <>
          {/* Objetivos y condiciones (multi) */}
          <div className="mb-4">
            <label className="block font-semibold mb-1">Objetivos</label>
            <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto pr-2 rounded-lg border border-border bg-gradient-to-b from-white/90 to-gray-100/80 shadow-inner custom-scrollbar px-3 py-2">
              {GOAL_CHOICES.map(g => (
                <label
                  key={g}
                  className={`flex items-center gap-1 px-3 py-1 rounded-full border cursor-pointer transition-all select-none text-xs md:text-sm
                    ${form.goals.includes(g)
                      ? 'bg-primary text-surface border-primary shadow scale-105'
                      : 'bg-surface border-border hover:border-primary hover:bg-primary/10'}`}
                >
                  <input
                    type="checkbox"
                    name="goals"
                    value={g}
                    checked={form.goals.includes(g)}
                    onChange={handleChange}
                    className="accent-primary w-4 h-4"
                  />
                  <span>{g}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">Condiciones médicas</label>
            <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto pr-2 rounded-lg border border-border bg-gradient-to-b from-white/90 to-gray-100/80 shadow-inner custom-scrollbar px-3 py-2">
              {CONDITION_CHOICES.map(c => (
                <label
                  key={c}
                  className={`flex items-center gap-1 px-3 py-1 rounded-full border cursor-pointer transition-all select-none text-xs md:text-sm
                    ${form.conditions.includes(c)
                      ? 'bg-primary text-surface border-primary shadow scale-105'
                      : 'bg-surface border-border hover:border-primary hover:bg-primary/10'}`}
                >
                  <input
                    type="checkbox"
                    name="conditions"
                    value={c}
                    checked={form.conditions.includes(c)}
                    onChange={handleChange}
                    className="accent-primary w-4 h-4"
                  />
                  <span>{c}</span>
                </label>
              ))}
            </div>
          </div>
          <style jsx>{`
            .custom-scrollbar::-webkit-scrollbar {
              width: 8px;
              background: transparent;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb {
              background: #e0e7ef;
              border-radius: 6px;
            }
            .custom-scrollbar {
              scrollbar-width: thin;
              scrollbar-color: #e0e7ef #f8fafc;
            }
          `}</style>
        </>
      )}
      {step === 3 && (
        <>
          {/* Entorno y equipamiento (multi) */}
          <div className="mb-2">
            <label className="block font-semibold mb-1">Entorno</label>
            <div className="flex flex-wrap gap-2">
              {ENVIRONMENT_CHOICES.map(e => (
                <label
                  key={e}
                  className={`flex items-center gap-1 px-3 py-1 rounded-full border cursor-pointer transition-all select-none
                    ${form.environment.includes(e)
                      ? 'bg-primary text-surface border-primary shadow-sm scale-105'
                      : 'bg-surface border-border hover:border-primary hover:bg-primary/10'}`}
                >
                  <input
                    type="checkbox"
                    name="environment"
                    value={e}
                    checked={form.environment.includes(e)}
                    onChange={handleChange}
                    className="accent-primary w-4 h-4"
                  />
                  <span className="text-sm">{e}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="mb-2">
            <label className="block font-semibold mb-1">Equipamiento disponible</label>
            <div className="flex flex-wrap gap-2">
              {EQUIPMENT_CHOICES.map(eq => (
                <label
                  key={eq}
                  className={`flex items-center gap-1 px-3 py-1 rounded-full border cursor-pointer transition-all select-none
                    ${form.equipment.includes(eq)
                      ? 'bg-primary text-surface border-primary shadow-sm scale-105'
                      : 'bg-surface border-border hover:border-primary hover:bg-primary/10'}`}
                >
                  <input
                    type="checkbox"
                    name="equipment"
                    value={eq}
                    checked={form.equipment.includes(eq)}
                    onChange={handleChange}
                    className="accent-primary w-4 h-4"
                  />
                  <span className="text-sm">{eq}</span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}
      {step === 4 && (
        <>
          {/* Niveles de actividad */}
          <div className="mb-2 flex items-center">
            <label className="block font-semibold mb-1 flex-1">Nivel NEAT (actividad diaria)</label>
            {autoFilled.neat_level && <AutoIcon />}
          </div>
          <select
            name="neat_level"
            value={form.neat_level}
            onChange={handleNumberChange}
            className="w-full p-2 rounded border border-border"
          >
            {ACTIVITY_LEVEL_CHOICES.map(l => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
          <div className="mb-2 flex items-center">
            <label className="block font-semibold mb-1 flex-1">Nivel Cardio Moderado</label>
            {autoFilled.cardio_mod_level && <AutoIcon />}
          </div>
          <select
            name="cardio_mod_level"
            value={form.cardio_mod_level}
            onChange={handleNumberChange}
            className="w-full p-2 rounded border border-border"
          >
            {ACTIVITY_LEVEL_CHOICES.map(l => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
          <div className="mb-2 flex items-center">
            <label className="block font-semibold mb-1 flex-1">Nivel Cardio Vigoroso</label>
            {autoFilled.cardio_vig_level && <AutoIcon />}
          </div>
          <select
            name="cardio_vig_level"
            value={form.cardio_vig_level}
            onChange={handleNumberChange}
            className="w-full p-2 rounded border border-border"
          >
            {ACTIVITY_LEVEL_CHOICES.map(l => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
          <div className="mb-2 flex items-center">
            <label className="block font-semibold mb-1 flex-1">Nivel Fuerza</label>
            {autoFilled.strength_level && <AutoIcon />}
          </div>
          <select
            name="strength_level"
            value={form.strength_level}
            onChange={handleNumberChange}
            className="w-full p-2 rounded border border-border"
          >
            {ACTIVITY_LEVEL_CHOICES.map(l => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
        </>
      )}
      <div className="space-y-4 flex flex-col">
        <div className="flex justify-between">
          {step > 0 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="text-secondary hover:underline"
            >
              ← Atrás
            </button>
          )}
          <div className="flex-1" />
          {step < 4 ? (
            <button
              type="submit"
              disabled={!validStep[step] || loading}
              className="bg-primary text-surface py-2 px-6 rounded-lg font-semibold transition disabled:opacity-50"
            >
              Siguiente →
            </button>
          ) : (
            <button
              type="submit"
              disabled={loading}
              className="bg-primary text-surface py-2 px-6 rounded-lg font-semibold transition"
            >
              {loading ? 'Registrando...' : 'Registrar'}
            </button>
          )}
        </div>
        {error && <div className="text-secondary text-xs text-center">{error}</div>}
        {onBack && step === 0 && (
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
