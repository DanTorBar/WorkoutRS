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
  const [serviceType, setServiceType] = useState<'google' | 'apple' | 'fitbit' | 'garmin' | null>(null);
  const [profileData, setProfileData] = useState<any>(null);

  const next = () => setStep((s) => s + 1);
  const back = () => setStep((s) => s - 1);
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
  };

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
        {step === 1 && <StepOneForm onNext={next} />}

        {step === 2 && (
          <StepTwoChoice
            onSelect={(opt) => {
              setHealthOption(opt);
              next();
            }}
            onBack={back}
          />
        )}

        {step === 3 && healthOption === 'file' && (
          <ServiceChoice
            onSelect={(svc) => {
              setServiceType(svc);
              next();
            }}
            onBack={back}
          />
        )}

        {step === 4 && healthOption === 'file' && serviceType && (
          <FileUploader
            serviceType={serviceType}
            onNext={(data) => {
              setProfileData(data);
              next();
            }}
            onBack={back}
          />
        )}

        {((step === 3 && healthOption === 'manual') ||
          (step === 5 && healthOption === 'file')) && (
          <HealthProfileForm
            defaultValues={profileData ?? {}}
            onBack={back}
          />
        )}
      </div>
    </main>
  );
}
