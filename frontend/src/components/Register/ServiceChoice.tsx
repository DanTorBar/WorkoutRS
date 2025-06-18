'use client';

import React, { useState } from 'react';
import { SiGooglefit } from 'react-icons/si';
// Importar tus SVG de hover como componentes React
import Fitbit from '@/../public/icons/fitbit.svg';
import GoogleFitHover from '@/../public/icons/googlefit-hover.svg';
import AppleHealth from '@/../public/icons/applehealth.svg';
import AppleHealthHover from '@/../public/icons/applehealth-hover.svg';
import FitbitHover from '@/../public/icons/fitbit-hover.svg';
import Garmin from '@/../public/icons/garmin.svg';
import GarminHover from '@/../public/icons/garmin-hover.svg';

export default function ServiceChoice({
  onSelect,
  onBack,
}: {
  onSelect: (service: 'googlefit' | 'apple' | 'fitbit' | 'garmin') => void;
  onBack: () => void;
}) {
  const [hovered, setHovered] = useState<string | null>(null);

  const services = [
    {
      id: 'googlefit',
      label: 'Google Fit',
      Icon: SiGooglefit,
      HoverIcon: GoogleFitHover,
    },
    {
      id: 'apple',
      label: 'Apple Health',
      Icon: AppleHealth,
      HoverIcon: AppleHealthHover,
    },
    {
      id: 'fitbit',
      label: 'Fitbit',
      Icon: Fitbit,
      HoverIcon: FitbitHover,
    },
    {
      id: 'garmin',
      label: 'Garmin',
      Icon: Garmin,
      HoverIcon: GarminHover
    },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-primary text-center">
        ¿De dónde quieres importar tus datos?
      </h2>
      <div className="grid grid-cols-2 gap-4">
        {services.map(({ id, label, Icon, HoverIcon }) => {
          const isHover = hovered === id;
          const WrapperIcon = isHover ? HoverIcon : Icon;
          const isDisabled = id === 'garmin';
          return (
            <div
              key={id}
              onClick={() => !isDisabled && onSelect(id as any)}
              onMouseEnter={() => setHovered(id)}
              onMouseLeave={() => setHovered(null)}
              className={`cursor-pointer border border-border rounded-lg p-6 flex flex-col items-center justify-center transition \
                ${isHover ? 'bg-primary text-surface' : 'bg-surface text-text'} \
                ${isDisabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`}
            >
              <WrapperIcon className={`w-8 h-8 mb-2 ${id === 'garmin' ? 'w-16 !important' : ''}`} />
              <span className="text-center font-medium">
                {label}
              </span>
            </div>
          );
        })}
      </div>
      <button onClick={onBack} className="text-secondary hover:underline">
        ← Volver
      </button>
    </div>
  );
}
