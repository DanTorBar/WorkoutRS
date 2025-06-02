"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { Loader2, ChevronLeft } from "lucide-react";
import LikeButton from "@/components/LikeButton";
import React from "react";
import AccessDeniedPage from "@/components/AccessDeniedPage";
import CommentBox from "@/components/CommentBox";

interface Workout {
  id: number;
  creationDate: string;
  workoutName: string;
  workoutCategory: string;
  level: string;
  gender: string;
  bodyPart: string;
  description: string;
  likes_count: number;
  liked: boolean;
  creator: {
    id: number;
    username: string;
  };
}

interface Day {
  day: number;
  exercises: string[];
}

export default function RutinaDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [days, setDays] = useState<Day[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);
  const [isAuth, setIsAuth] = useState(true);

  useEffect(() => {
    const token =
      typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
    setIsAuth(!!token);
    setHasCheckedAuth(true);
  }, []);

  useEffect(() => {
    if (!isAuth) return;
    (async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("authToken");
        if (!token) throw new Error("Token no encontrado");

        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}workouts/${id}/`,
          {
            cache: "no-store",
            headers: { Authorization: `Token ${token}` },
          }
        );
        if (!res.ok) {
          if (res.status === 401) throw new Error("No autorizado");
          throw new Error("Error al cargar rutina");
        }
        const data = await res.json();
        setWorkout(data.workout);
        // Aseguramos 7 días, rellenando vacíos si no vienen
        const completos: Day[] = [];
        for (let d = 1; d <= 7; d++) {
          const existe = data.days.find((x: Day) => x.day === d);
          completos.push(existe || { day: d, exercises: [] });
        }
        setDays(completos);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [id, isAuth]);

  if (!hasCheckedAuth) return null;
  if (!isAuth) return <AccessDeniedPage />;

  if (loading) {
    return (
      <main
        className="relative min-h-screen bg-gradient-to-br from-bg to-surface flex items-start justify-center p-6 overflow-auto"
      >
        <div className="relative w-full max-w-6xl bg-surface rounded-2xl shadow-2xl p-8 animate-pulse">
          {/* Header skeleton */}
          <div className="flex justify-between items-center mb-6">
            <div className="h-8 w-32 bg-primary/20 rounded" />
            <div className="h-8 w-20 bg-primary/20 rounded" />
          </div>
          {/* Title skeleton */}
          <div className="h-10 w-2/3 bg-primary/20 rounded mb-4" />
          <div className="h-6 w-1/2 bg-primary/10 rounded mb-8" />
          {/* Tags skeleton */}
          <div className="flex gap-2 mb-8">
            <div className="h-6 w-24 bg-accent/20 rounded-full" />
            <div className="h-6 w-20 bg-primary/20 rounded-full" />
            <div className="h-6 w-16 bg-secondary/20 rounded-full" />
          </div>
          {/* Days skeleton */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {Array.from({ length: 7 }).map((_, i) => (
              <div
                key={i}
                className="bg-bg border border-border rounded-lg p-6 flex flex-col gap-4"
              >
                <div className="h-6 w-24 bg-primary/20 rounded mb-2" />
                <div className="space-y-2">
                  <div className="h-4 w-3/4 bg-primary/10 rounded" />
                  <div className="h-4 w-2/3 bg-primary/10 rounded" />
                  <div className="h-4 w-1/2 bg-primary/10 rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg text-secondary">
        Error: {error}
      </div>
    );
  }
  if (!workout) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg text-text">
        No hay datos de la rutina.
      </div>
    );
  }

  return (
    <main
      className="
        relative 
        min-h-screen
        bg-gradient-to-br from-bg to-surface
        flex items-start justify-center p-6 overflow-auto
      "
    >
      {/* Tarjeta central */}
      <div className="relative w-full max-w-6xl bg-surface rounded-2xl shadow-2xl p-8">
        {/* Volver + Likes */}
        <div className="flex justify-between items-center mb-6">
          <Link
            href="/rutinas"
            className="inline-flex items-center text-secondary hover:text-primary transition"
          >
            <ChevronLeft className="mr-1" /> Volver
          </Link>
                    <div className="flex flex-col items-center gap-1 flex-1">
            <span className="text-xs text-secondary">
              Creado el{" "}
              {new Date(workout.creationDate).toLocaleDateString()} por{" "}
              <Link
                href={`/perfil/${workout.creator.id}`}
                className="text-primary hover:underline"
              >
                {workout.creator.username}
              </Link>
            </span>
          </div>
          <LikeButton
            initialCount={workout.likes_count}
            initialLiked={workout.liked}
            type="workout"
            itemId={workout.id}
          />
        </div>

        {/* Cabecera Rutina */}
        <div className="space-y-2 mb-8">
          <h1 className="text-4xl font-bold text-primary">
            {workout.workoutName}
          </h1>
          {workout.description === "N/A" ? (
            <p className="text-text italic">Sin descripción</p>
          ) : (
            <p className="text-text">{workout.description}</p>
          )}
        </div>

        {/* Detalles */}
        <div className="flex flex-wrap gap-2 mb-8 w-full">
          <div className="flex-1 min-w-[180px] flex flex-wrap gap-2 items-start">
            <Tag label={workout.level} color="accent" />
            <Tag label={workout.workoutCategory} color="primary" />
            <Tag label={workout.gender} color="secondary" />
          </div>
          <div className="flex-1 min-w-[180px] flex flex-wrap gap-2 items-start justify-end">
            {workout.bodyPart &&
              workout.bodyPart
                .split(",")
                .map((bp) => (
                  <Tag key={bp.trim()} label={bp.trim()} color="bodypart" />
                ))}
          </div>
        </div>

        {/* Días */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {days.map((d) => (
            <div
              key={d.day}
              className="bg-bg border border-border rounded-lg p-6 hover:shadow transition"
            >
              <h2 className="text-2xl font-semibold text-primary mb-4">
                Día {d.day}
              </h2>
              {d.exercises.length ? (
                <ul className="list-disc list-inside space-y-2 text-text">
                  {d.exercises.map((ex, i) => (
                    <li key={i}>{ex}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-text italic">Descanso</p>
              )}
            </div>
          ))}
        </section>
        {/* Comentarios */}
        <CommentBox workoutId={workout.id} token={typeof window !== "undefined" ? localStorage.getItem("authToken") : null} />
      </div>
    </main>
  );
}

// Componente reutilizable para etiquetas
function Tag({
  label,
  color,
}: {
  label: string | JSX.Element;
  color: "primary" | "secondary" | "accent" | "bodypart";
}): JSX.Element {
  // Iconos según el color (igual que en la lista de rutinas)
  let icon = null;
  if (color === "primary") {
    // Categoría
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16" className="inline" xmlns="http://www.w3.org/2000/svg"><path d="M7.0498 7.0498H7.0598M10.5118 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V10.5118C3 11.2455 3 11.6124 3.08289 11.9577C3.15638 12.2638 3.27759 12.5564 3.44208 12.8249C3.6276 13.1276 3.88703 13.387 4.40589 13.9059L9.10589 18.6059C10.2939 19.7939 10.888 20.388 11.5729 20.6105C12.1755 20.8063 12.8245 20.8063 13.4271 20.6105C14.112 20.388 14.7061 19.7939 15.8941 18.6059L18.6059 15.8941C19.7939 14.7061 20.388 14.112 20.6105 13.4271C20.8063 12.8245 20.8063 12.1755 20.6105 11.5729C20.388 10.888 19.7939 10.2939 18.6059 9.10589L13.9059 4.40589C13.387 3.88703 13.1276 3.6276 12.8249 3.44208C12.5564 3.27759 12.2638 3.15638 11.9577 3.08289C11.6124 3 11.2455 3 10.5118 3ZM7.5498 7.0498C7.5498 7.32595 7.32595 7.5498 7.0498 7.5498C6.77366 7.5498 6.5498 7.32595 6.5498 7.0498C6.5498 6.77366 6.77366 6.5498 7.0498 6.5498C7.32595 6.5498 7.5498 6.77366 7.5498 7.0498Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path></svg>
      </span>
    );
  } else if (color === "accent") {
    // Nivel
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg fill="none" viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="1.2" className="inline"><rect x="16" y="4" width="2" height="16"/><rect x="11" y="10" width="2" height="10"/><rect x="6" y="14" width="2" height="6"/></svg>
      </span>
    );
  } else if (color === "secondary") {
    // Género
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg viewBox="0 0 16 16" width="16" height="16" xmlns="http://www.w3.org/2000/svg" className="inline"><path d="m 8 1 c -1.65625 0 -3 1.34375 -3 3 s 1.34375 3 3 3 s 3 -1.34375 3 -3 s -1.34375 -3 -3 -3 z m -1.5 7 c -2.492188 0 -4.5 2.007812 -4.5 4.5 v 0.5 c 0 1.109375 0.890625 2 2 2 h 8 c 1.109375 0 2 -0.890625 2 -2 v -0.5 c 0 -2.492188 -2.007812 -4.5 -4.5 -4.5 z m 0 0" fill="currentColor"></path></svg>
      </span>
    );
  }
  const bg =
    color === "primary"
      ? "bg-primary/10"
      : color === "secondary"
      ? "bg-secondary"
      : color === "accent"
      ? "bg-accent"
      : "bg-blue-200"; // bodypart: azul claro
  const text =
    color === "primary"
      ? "text-primary"
      : color === "secondary"
      ? "text-surface"
      : color === "accent"
      ? "text-surface"
      : "text-blue-900"; // bodypart: azul oscuro
  return (
    <span
      className={`${bg} ${text} px-3 py-1 rounded-full text-sm font-medium inline-flex items-center`}
    >
      {icon}
      {label}
    </span>
  );
}
