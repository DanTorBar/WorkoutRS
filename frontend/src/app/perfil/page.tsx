"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import HealthProfileForm from "@/components/Register/HealthProfileForm";

// Tipado para evitar errores de acceso a propiedades
interface HealthProfile {
  date_of_birth?: string;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  age?: number;
  bmi?: number;
  goals?: string[];
  conditions?: string[];
  equipment?: string[];
  environment?: string[];
  neat_level?: number;
  cardio_mod_level?: number;
  cardio_vig_level?: number;
  strength_level?: number;
}

interface User {
  first_name?: string;
  last_name?: string;
  email?: string;
  health_profile?: HealthProfile;
}

export default function PerfilPage() {
  const [user, setUser] = useState<User | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      router.push("/login");
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_URL}users/profile/`, {
      headers: { Authorization: `Token ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setUser(data);
        setLoading(false);
      });
  }, [router]);

  const handleSave = async (form) => {
    setLoading(true);
    setError("");
    const token = localStorage.getItem("authToken");
    // Separar datos de usuario y perfil de salud
    const {
      first_name,
      last_name,
      birth_date,
      gender,
      weight,
      height,
      goals,
      conditions,
      equipment,
      environment,
      neat_level,
      cardio_mod_level,
      cardio_vig_level,
      strength_level,
    } = form;
    const userPayload = {
      first_name,
      last_name,
      health_profile: {
        date_of_birth: birth_date,
        gender,
        weight_kg: weight,
        height_cm: height,
        goals,
        conditions,
        equipment,
        environment,
        neat_level,
        cardio_mod_level,
        cardio_vig_level,
        strength_level,
      },
    };
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}users/me/`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify(userPayload),
    });
    if (res.ok) {
      setEditMode(false);
      const updated = await res.json();
      setUser(updated);
    } else {
      setError("No se pudo guardar el perfil. Revisa los datos.");
    }
    setLoading(false);
  };

  if (loading) return <div className="p-8 text-center">Cargando...</div>;
  if (!user) return <div className="p-8 text-center">No se pudo cargar el perfil.</div>;

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow mt-8">
      <h1 className="text-3xl font-bold mb-2 text-center text-primary">Perfil de Usuario</h1>
      <p className="text-center text-gray-500 mb-6">Gestiona y edita todos tus datos personales y de salud</p>
      {editMode ? (
        <HealthProfileForm
          defaultValues={{
            ...user,
            ...user.health_profile,
            birth_date: user.health_profile?.date_of_birth || "",
            weight: user.health_profile?.weight_kg || "",
            height: user.health_profile?.height_cm || "",
          }}
          onSubmit={handleSave}
          loading={loading}
          error={error}
          onBack={() => setEditMode(false)}
        />
      ) : (
        <div className="space-y-8">
          {/* Datos personales */}
          <div>
            <h2 className="text-lg font-semibold text-primary mb-2">Datos personales</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="block text-xs text-gray-500">Nombre</span>
                <span className="font-semibold text-lg">{user.first_name || user.health_profile?.first_name || '-'}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Apellidos</span>
                <span className="font-semibold text-lg">{user.last_name || user.health_profile?.last_name || '-'}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Género</span>
                <span className="font-semibold">{user.health_profile?.gender || '-'}</span>
              </div>
              <div className="sm:col-span-2">
                <span className="block text-xs text-gray-500">Email</span>
                <span className="font-semibold">{user.email}</span>
              </div>
            </div>
          </div>
          {/* Objetivos y condiciones */}
          <div>
            <h2 className="text-lg font-semibold text-primary mb-2">Objetivos y condiciones</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="block text-xs text-gray-500">Objetivos</span>
                <span className="font-semibold">{user.health_profile?.goals?.length ? user.health_profile.goals.join(", ") : "-"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Condiciones médicas</span>
                <span className="font-semibold">{user.health_profile?.conditions?.length ? user.health_profile.conditions.join(", ") : "-"}</span>
              </div>
            </div>
          </div>
          {/* Entorno y equipamiento */}
          <div>
            <h2 className="text-lg font-semibold text-primary mb-2">Entorno y equipamiento</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="block text-xs text-gray-500">Equipamiento</span>
                <span className="font-semibold">{user.health_profile?.equipment?.length ? user.health_profile.equipment.join(", ") : "-"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Entorno</span>
                <span className="font-semibold">{user.health_profile?.environment?.length ? user.health_profile.environment.join(", ") : "-"}</span>
              </div>
            </div>
          </div>
          {/* Niveles de actividad */}
          <div>
            <h2 className="text-lg font-semibold text-primary mb-2">Niveles de actividad</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="block text-xs text-gray-500">Nivel NEAT</span>
                <span className="font-semibold">{user.health_profile?.neat_level ?? "-"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Cardio Moderado</span>
                <span className="font-semibold">{user.health_profile?.cardio_mod_level ?? "-"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Cardio Vigoroso</span>
                <span className="font-semibold">{user.health_profile?.cardio_vig_level ?? "-"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500">Nivel Fuerza</span>
                <span className="font-semibold">{user.health_profile?.strength_level ?? "-"}</span>
              </div>
            </div>
          </div>
          <div className="flex justify-end mt-8">
            <button
              type="button"
              onClick={() => setEditMode(true)}
              className="px-6 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 font-semibold shadow"
            >
              Editar perfil
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
