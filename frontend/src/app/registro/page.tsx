'use client';

import { useState } from 'react';
import StepOneForm from '@/components/Register/StepOneForm';
import StepTwoChoice from '@/components/Register/StepTwoChoice';
import ServiceChoice from '@/components/Register/ServiceChoice';
import FileUploader from '@/components/Register/FileUploader';
import HealthProfileForm from '@/components/Register/HealthProfileForm';

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [healthOption, setHealthOption] = useState<'file' | 'manual' | null>(null);
  const [serviceType, setServiceType] = useState<'googlefit' | 'apple' | 'fitbit' | 'garmin' | null>(null);
  const [profileData, setProfileData] = useState<any>(null);
  const [userData, setUserData] = useState<any>(null);
  const [registering, setRegistering] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  // Para evitar que el usuario pierda datos manuales al importar, mergea solo campos vacíos
  function mergeProfileData(imported: any) {
    setProfileData((prev: any) => {
      if (!prev) return imported;
      const merged = { ...prev };
      Object.entries(imported).forEach(([k, v]) => {
        if (v && (!merged[k] || merged[k] === '')) {
          merged[k] = v;
        }
      });
      return merged;
    });
  }

  // Manejo de registro final
  async function handleRegister(profileForm: any) {
    setRegistering(true);
    setRegisterError(null);
    try {
      // Convierte los campos multi a array si vienen como string
      const toArray = (v: any) => (typeof v === 'string' ? v.split(',').map((s: string) => s.trim()).filter(Boolean) : v ?? []);
      const profilePayload = {
        ...profileForm,
        goals: toArray(profileForm.goals),
        conditions: toArray(profileForm.conditions),
        equipment: toArray(profileForm.equipment),
        environment: toArray(profileForm.environment),
      };
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...userData,
          health_data_consent: true,
          profile: profilePayload,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw data;
      alert('¡Cuenta creada!');
      window.location.href = '/login';
    } catch (err: any) {
      setRegisterError(err?.error || 'Error al registrar');
    } finally {
      setRegistering(false);
    }
  }

  let n = 1;
  switch (step) {
    case 1:
      n = 1;
      break;
    case 2:
      n = 2;
      break;
    case 3:
      n = healthOption === 'file' ? 2 : 3;
      break;
    case 4:
      n = 2;
      break;
    case 5:
      n = 3;
      break;
    default:
      n = 1;
      break;
  }

  return (
    <main
      className="
        relative h-[calc(100vh-5rem-2px)]
        from-bg to-surface
        flex items-center justify-center p-6
        overflow-hidden
      "
    >
      <div className="relative w-full max-w-md bg-surface rounded-2xl shadow-2xl p-8 z-10">
        {/* Stepper */}
        <div className="flex justify-between items-center mb-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className={`flex-1 h-2 mx-1 rounded ${
                n >= i ? 'bg-primary' : 'bg-border'
              }`}
            />
          ))}
        </div>

        {/* Flujo por pasos */}
        {step === 1 && (
          <StepOneForm
            onNext={(form) => {
              setUserData(form);
              setStep(2);
            }}
          />
        )}

        {step === 2 && (
          <StepTwoChoice
            onSelect={(opt) => {
              setHealthOption(opt);
              setStep(opt === 'file' ? 3 : 5);
            }}
            onBack={() => setStep(1)}
          />
        )}

        {step === 3 && healthOption === 'file' && (
          <ServiceChoice
            onSelect={(svc) => {
              setServiceType(svc);
              setStep(4);
            }}
            onBack={() => setStep(2)}
          />
        )}

        {step === 4 && healthOption === 'file' && serviceType && (
          <FileUploader
            serviceType={serviceType}
            onNext={(data) => {
              // Normaliza los datos importados para el formulario
              const normalized = {
                first_name: data.first_name ?? '',
                last_name: data.last_name ?? '',
                birth_date: data.birth_date ?? '',
                gender: data.gender ?? '',
                weight: data.weight_kg?.toString() ?? data.weight ?? '',
                height: data.height_cm?.toString() ?? data.height ?? '',
                goals: data.goals ?? '',
                environment: data.environment ?? '',
                conditions: data.conditions ?? '',
                equipment: data.equipment ?? '',
                neat_level: data.neat_level ?? 0,
                cardio_mod_level: data.cardio_mod_level ?? 0,
                cardio_vig_level: data.cardio_vig_level ?? 0,
                strength_level: data.strength_level ?? 0,
                imported_neat_min: data.imported_neat_min ?? undefined,
                imported_cardio_mod_min: data.imported_cardio_mod_min ?? undefined,
                imported_cardio_vig_min: data.imported_cardio_vig_min ?? undefined,
                imported_strength_min: data.imported_strength_min ?? undefined,
              };
              setProfileData((prev: any) => {
                if (!prev) return normalized;
                const merged = { ...normalized };
                (Object.entries(prev) as [keyof typeof normalized, any][]).forEach(([k, v]) => {
                  if (v && (!merged[k] || merged[k] === '' || merged[k] === 0)) {
                    merged[k] = v;
                  }
                });
                return merged;
              });
              setStep(5);
            }}
            onBack={() => setStep(3)}
          />
        )}

        {step === 5 && (
          <HealthProfileForm
            defaultValues={{
              first_name: profileData?.first_name ?? '',
              last_name: profileData?.last_name ?? '',
              birth_date: profileData?.birth_date ?? '',
              gender: profileData?.gender ?? '',
              weight: profileData?.weight ?? profileData?.weight_kg?.toString() ?? '',
              height: profileData?.height ?? profileData?.height_cm?.toString() ?? '',
              goals: profileData?.goals ?? '',
              environment: profileData?.environment ?? '',
              conditions: profileData?.conditions ?? '',
              equipment: profileData?.equipment ?? '',
              neat_level: profileData?.neat_level ?? 0,
              cardio_mod_level: profileData?.cardio_mod_level ?? 0,
              cardio_vig_level: profileData?.cardio_vig_level ?? 0,
              strength_level: profileData?.strength_level ?? 0,
              imported_neat_min: profileData?.imported_neat_min,
              imported_cardio_mod_min: profileData?.imported_cardio_mod_min,
              imported_cardio_vig_min: profileData?.imported_cardio_vig_min,
              imported_strength_min: profileData?.imported_strength_min,
            }}
            onBack={() => {
              if (healthOption === 'file') setStep(4);
              else setStep(2);
            }}
            onSubmit={handleRegister}
            loading={registering}
            error={registerError ?? undefined}
          />
        )}
      </div>
    </main>
  );
}
