"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import LikeButton from "@/components/LikeButton";
import { Loader2 } from "lucide-react";

interface Workout {
  id: number;
  workoutName: string;
  workoutCategory: string;
  level: string;
  gender: string;
  likes_count: number;
  creationDate: string;
  bodyPart: string;
  description?: string;
}

interface Exercise {
  id: number;
  exerciseName: string;
  exerciseCategory: string;
  video: string;
  instructions: string;
  equipment: string;
  likes_count: number;
  priMuscles: number[];
  secMuscles: number[];
}

export default function RecomendacionesPage() {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [workoutError, setWorkoutError] = useState<string | null>(null);
  const [exerciseError, setExerciseError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      setWorkoutError(null);
      setExerciseError(null);
      let workoutsData: Workout[] = [];
      let exercisesData: Exercise[] = [];
      const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
      if (!token) {
        setWorkoutError("No autenticado");
        setExerciseError("No autenticado");
        setLoading(false);
        return;
      }
      // Rutinas
      try {
        const wRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}core/recommend/workouts/`, {
          headers: { Authorization: `Token ${token}` },
        });
        if (wRes.ok) {
          workoutsData = await wRes.json();
        } else {
          setWorkoutError("No se han podido obtener recomendaciones de rutinas.");
        }
      } catch {
        setWorkoutError("No se han podido obtener recomendaciones de rutinas.");
      }
      // Ejercicios
      try {
        const eRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}core/recommend/exercises/`, {
          headers: { Authorization: `Token ${token}` },
        });
        if (eRes.ok) {
          exercisesData = await eRes.json();
        } else {
          setExerciseError("No se han podido obtener recomendaciones de ejercicios.");
        }
      } catch {
        setExerciseError("No se han podido obtener recomendaciones de ejercicios.");
      }
      setWorkouts(workoutsData);
      setExercises(exercisesData);
      setError(null);
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-bg">
        <Loader2 className="animate-spin w-12 h-12 text-primary mb-4" />
        <span className="text-secondary">Cargando recomendaciones...</span>
      </main>
    );
  }
  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-bg text-secondary">
        Error: {error}
      </main>
    );
  }

  return (
    <main className="relative h-[calc(100vh-5rem-2px)] bg-gradient-to-br from-bg to-surface p-6 flex flex-col gap-12">
      {/* Rutinas recomendadas */}
      <section>
        <h2 className="text-3xl font-bold text-primary mb-6 text-center">Rutinas recomendadas para ti</h2>
        {workoutError ? (
          <div className="text-center text-red-500 mb-4">{workoutError}</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 justify-center">
            {workouts.length === 0 ? (
              <div className="col-span-full text-center text-secondary">No hay recomendaciones de rutinas.</div>
            ) : (
              workouts.map((rutina) => (
                <Link
                  key={rutina.id}
                  href={`/rutinas/${rutina.id}`}
                  className="bg-surface border border-border rounded-lg p-6 shadow flex flex-col gap-2 hover:shadow-lg transition-all duration-300 min-h-[260px]"
                >
                  <h3 className="text-lg font-bold text-primary mb-1 text-center break-words leading-tight w-full" style={{ wordBreak: 'break-word', maxHeight: '3.5em', overflow: 'hidden' }} title={rutina.workoutName}>{rutina.workoutName}</h3>
                  <div className="flex flex-wrap gap-2 mb-2 justify-center">
                    {/* Categoría */}
                    {rutina.workoutCategory && (
                      <span className="inline-flex items-center bg-primary/10 text-primary px-2 py-1 rounded-full text-xs font-medium">
                        <svg viewBox="0 0 24 24" fill="none" width="14" height="14" className="mr-1"><path d="M7.0498 7.0498H7.0598M10.5118 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V10.5118C3 11.2455 3 11.6124 3.08289 11.9577C3.15638 12.2638 3.27759 12.5564 3.44208 12.8249C3.6276 13.1276 3.88703 13.387 4.40589 13.9059L9.10589 18.6059C10.2939 19.7939 10.888 20.388 11.5729 20.6105C12.1755 20.8063 12.8245 20.8063 13.4271 20.6105C14.112 20.388 14.7061 19.7939 15.8941 18.6059L18.6059 15.8941C19.7939 14.7061 20.388 14.112 20.6105 13.4271C20.8063 12.8245 20.8063 12.1755 20.6105 11.5729C20.388 10.888 19.7939 10.2939 18.6059 9.10589L13.9059 4.40589C13.387 3.88703 13.1276 3.6276 12.8249 3.44208C12.5564 3.27759 12.2638 3.15638 11.9577 3.08289C11.6124 3 11.2455 3 10.5118 3ZM7.5498 7.0498C7.5498 7.32595 7.32595 7.5498 7.0498 7.5498C6.77366 7.5498 6.5498 7.32595 6.5498 7.0498C6.5498 6.77366 6.77366 6.5498 7.0498 6.5498C7.32595 6.5498 7.5498 6.77366 7.5498 7.0498Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path></svg>
                        {rutina.workoutCategory}
                      </span>
                    )}
                    {/* Nivel */}
                    <span className="inline-flex items-center bg-accent text-surface px-2 py-1 rounded-full text-xs font-medium">
                      <svg fill="none" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="1.2" className="mr-1"><rect x="16" y="4" width="2" height="16" /><rect x="11" y="10" width="2" height="10" /><rect x="6" y="14" width="2" height="6" /></svg>
                      {rutina.level}
                    </span>
                    {/* Género */}
                    <span className="inline-flex items-center bg-secondary text-surface px-2 py-1 rounded-full text-xs font-medium">
                      <svg viewBox="0 0 16 16" width="14" height="14" className="mr-1"><path d="m 8 1 c -1.65625 0 -3 1.34375 -3 3 s 1.34375 3 3 3 s 3 -1.34375 3 -3 s -1.34375 -3 -3 -3 z m -1.5 7 c -2.492188 0 -4.5 2.007812 -4.5 4.5 v 0.5 c 0 1.109375 0.890625 2 2 2 h 8 c 1.109375 0 2 -0.890625 2 -2 v -0.5 c 0 -2.492188 -2.007812 -4.5 -4.5 -4.5 z m 0 0" fill="currentColor"></path></svg>
                      {rutina.gender}
                    </span>
                    {/* Partes del cuerpo */}
                    {rutina.bodyPart && (
                      <span className="inline-flex items-center bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs font-medium">
                        <svg viewBox="0 0 24 24" width="14" height="14" className="mr-1" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="M9.14,16.77S8,13.17,10.09,11A14.12,14.12,0,0,1,13,9.13a4.78,4.78,0,1,1,5.61,4.7c-1.83,2.77-5.83,7.71-11.33,7.71C4.36,21.54,1.5,13,1.5,9.13V4.48A2.26,2.26,0,0,1,3.64,2.23c1.73-.09,4,0,4.54,1.17C9,5.11,7.23,8.18,5.32,8.18c0,1.5,1.83,4.76,3.49,6.56" fill="none" stroke="currentColor" strokeMiterlimit="10" strokeWidth="1.91"/></svg>
                        {rutina.bodyPart.replace(/,/g, ", ")}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-center mt-auto gap-2">
                    <LikeButton
                      initialCount={rutina.likes_count || 0}
                      initialLiked={false}
                      type="workout"
                      itemId={rutina.id}
                    />
                  </div>
                </Link>
              ))
            )}
          </div>
        )}
      </section>
      {/* Ejercicios recomendados */}
      <section>
        <h2 className="text-3xl font-bold text-primary mb-6 text-center">Ejercicios recomendados para ti</h2>
        {exerciseError ? (
          <div className="text-center text-red-500 mb-4">{exerciseError}</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 justify-center">
            {exercises.length === 0 ? (
              <div className="col-span-full text-center text-secondary">No hay recomendaciones de ejercicios.</div>
            ) : (
              exercises.map((ex) => {
                // Ambientes y equipamiento
                const ambientes = ["Casa", "Gimnasio", "Aire Libre", "AireLibre"];
                const eqArr = ex.equipment ? ex.equipment.split(",").map((e) => e.trim().replace(/AireLibre/, "Aire Libre")) : [];
                const ambientesPresentes = ["Casa", "Gimnasio", "Aire Libre"].filter((amb) => eqArr.includes(amb));
                const equipamientoReal = eqArr.filter((e) => !["Casa", "Gimnasio", "Aire Libre"].includes(e) && e !== "Ninguno");
                return (
                  <Link
                    key={ex.id}
                    href={`/ejercicios/${ex.id}`}
                    className="bg-surface border border-border rounded-lg p-6 shadow flex flex-col gap-2 hover:shadow-lg transition-all duration-300 min-h-[260px]"
                  >
                    <h3 className="text-lg font-bold text-primary mb-1 text-center break-words leading-tight w-full" style={{ wordBreak: 'break-word', maxHeight: '3.5em', overflow: 'hidden' }} title={ex.exerciseName}>{ex.exerciseName}</h3>
                    <div className="flex flex-wrap gap-2 mb-2 justify-center">
                      {/* Categoría */}
                      {ex.exerciseCategory && (
                        <span className="inline-flex items-center bg-primary/10 text-primary px-2 py-1 rounded-full text-xs font-medium">
                          <svg viewBox="0 0 24 24" fill="none" width="14" height="14" className="mr-1"><path d="M7.0498 7.0498H7.0598M10.5118 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V10.5118C3 11.2455 3 11.6124 3.08289 11.9577C3.15638 12.2638 3.27759 12.5564 3.44208 12.8249C3.6276 13.1276 3.88703 13.387 4.40589 13.9059L9.10589 18.6059C10.2939 19.7939 10.888 20.388 11.5729 20.6105C12.1755 20.8063 12.8245 20.8063 13.4271 20.6105C14.112 20.388 14.7061 19.7939 15.8941 18.6059L18.6059 15.8941C19.7939 14.7061 20.388 14.112 20.6105 13.4271C20.8063 12.8245 20.8063 12.1755 20.6105 11.5729C20.388 10.888 19.7939 10.2939 18.6059 9.10589L13.9059 4.40589C13.387 3.88703 13.1276 3.6276 12.8249 3.44208C12.5564 3.27759 12.2638 3.15638 11.9577 3.08289C11.6124 3 11.2455 3 10.5118 3ZM7.5498 7.0498C7.5498 7.32595 7.32595 7.5498 7.0498 7.5498C6.77366 7.5498 6.5498 7.32595 6.5498 7.0498C6.5498 6.77366 6.77366 6.5498 7.0498 6.5498C7.32595 6.5498 7.5498 6.77366 7.5498 7.0498Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path></svg>
                          {ex.exerciseCategory.replace(/,/g, ", ")}
                        </span>
                      )}
                      {/* Ambientes */}
                      {ambientesPresentes.map((amb) => (
                        <span key={amb} className="inline-flex items-center bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">
                          <svg viewBox="0 0 24 24" fill="none" width="14" height="14" className="mr-1" xmlns="http://www.w3.org/2000/svg"><path d="M19 9.77806V16.2C19 17.8801 19 18.7202 18.673 19.3619C18.3854 19.9264 17.9265 20.3854 17.362 20.673C16.7202 21 15.8802 21 14.2 21H9.8C8.11984 21 7.27976 21 6.63803 20.673C6.07354 20.3854 5.6146 19.9264 5.32698 19.3619C5 18.7202 5 17.8801 5 16.2V9.7774M21 12L15.5668 5.96393C14.3311 4.59116 13.7133 3.90478 12.9856 3.65138C12.3466 3.42882 11.651 3.42887 11.0119 3.65153C10.2843 3.90503 9.66661 4.59151 8.43114 5.96446L3 12M14 12C14 13.1045 13.1046 14 12 14C10.8954 14 10 13.1045 10 12C10 10.8954 10.8954 9.99996 12 9.99996C13.1046 9.99996 14 10.8954 14 12Z" stroke="#000000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path></svg>
                          {amb}
                        </span>
                      ))}
                      {/* Equipamiento */}
                      {equipamientoReal.map((eq) => (
                        <span key={eq} className="inline-flex items-center bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                          {eq}
                        </span>
                      ))}
                    </div>
                    {/* Músculos principales/secundarios si existen */}
                    {Array.isArray(ex.priMuscles) && ex.priMuscles.length > 0 &&
                      typeof ex.priMuscles[0] === "object" &&
                      (ex.priMuscles[0] as any).name && (ex.priMuscles[0] as any).name !== "N/A" && (
                      <div className="flex flex-wrap gap-2 mb-2 justify-center">
                        <span className="inline-flex items-center bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs font-medium">
                          <svg viewBox="0 0 24 24" width="14" height="14" className="mr-1"><path className="cls-1" d="M9.14,16.77S8,13.17,10.09,11A14.12,14.12,0,0,1,13,9.13a4.78,4.78,0,1,1,5.61,4.7c-1.83,2.77-5.83,7.71-11.33,7.71C4.36,21.54,1.5,13,1.5,9.13V4.48A2.26,2.26,0,0,1,3.64,2.23c1.73-.09,4,0,4.54,1.17C9,5.11,7.23,8.18,5.32,8.18c0,1.5,1.83,4.76,3.49,6.56" fill="none" stroke="currentColor" strokeMiterlimit="10" strokeWidth="1.91"/></svg>
                          {ex.priMuscles.map((m: any) => m.name).join(", ")}
                        </span>
                      </div>
                    )}
                    {Array.isArray(ex.secMuscles) && ex.secMuscles.length > 0 &&
                      typeof ex.secMuscles[0] === "object" &&
                      (ex.secMuscles[0] as any).name && (ex.secMuscles[0] as any).name !== "N/A" && (
                      <div className="flex flex-wrap gap-2 mb-2 justify-center">
                        <span className="inline-flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                          <svg viewBox="0 0 24 24" width="14" height="14" className="mr-1"><path className="cls-1" d="M9.14,16.77S8,13.17,10.09,11A14.12,14.12,0,0,1,13,9.13a4.78,4.78,0,1,1,5.61,4.7c-1.83,2.77-5.83,7.71-11.33,7.71C4.36,21.54,1.5,13,1.5,9.13V4.48A2.26,2.26,0,0,1,3.64,2.23c1.73-.09,4,0,4.54,1.17C9,5.11,7.23,8.18,5.32,8.18c0,1.5,1.83,4.76,3.49,6.56" fill="none" stroke="currentColor" strokeMiterlimit="10" strokeWidth="1.91"/></svg>
                          {ex.secMuscles.map((m: any) => m.name).join(", ")}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-center mt-auto gap-2">
                      <LikeButton
                        initialCount={ex.likes_count}
                        initialLiked={false}
                        type="exercise"
                        itemId={ex.id}
                      />
                    </div>
                  </Link>
                );
              })
            )}
          </div>
        )}
      </section>
    </main>
  );
}
