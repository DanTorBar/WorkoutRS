"use client";

import { use, useEffect, useState, useRef } from "react";
import LikeButton from "@/components/LikeButton";
import Link from "next/link";
import CommentBox from "@/components/CommentBox";

interface Muscle {
  name: string;
}

interface Exercise {
  id: number;
  exerciseName: string;
  exerciseCategory: string;
  priMuscles: Muscle[];
  secMuscles: Muscle[];
  video?: string;
  instructions?: string;
  equipment?: string;
  likes_count: number;
  is_favourite?: boolean;
}

export default function EjercicioDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);
  const [isAuth, setIsAuth] = useState(true);
  const [iframeError, setIframeError] = useState(false);
  const iframeLoaded = useRef(false);

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
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}exercises/${id}/`,
          {
            cache: "no-store",
            headers: token ? { Authorization: `Token ${token}` } : {},
          }
        );
        if (!res.ok) throw new Error("Error al cargar ejercicio");
        const data = await res.json();
        setExercise(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [id, isAuth]);

  // Detectar si el iframe de YouTube no carga en 3 segundos
  useEffect(() => {
    if (
      exercise?.video &&
      (exercise.video.includes("youtube.com") ||
        exercise.video.includes("youtu.be"))
    ) {
      setIframeError(false);
      iframeLoaded.current = false;
      const timeout = setTimeout(() => {
        if (!iframeLoaded.current) setIframeError(true);
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [exercise?.video]);

  if (!hasCheckedAuth) return null;
  if (!isAuth)
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg text-secondary">
        Acceso denegado
      </div>
    );

  if (loading) {
    return (
      <main className="relative min-h-screen bg-gradient-to-br from-bg to-surface flex items-start justify-center p-6 overflow-auto">
        <div className="relative w-full max-w-3xl bg-surface rounded-2xl shadow-2xl p-8 animate-pulse">
          <div className="h-8 w-32 bg-primary/20 rounded mb-4" />
          <div className="h-6 w-1/2 bg-primary/10 rounded mb-8" />
          <div className="flex gap-2 mb-8">
            <div className="h-6 w-24 bg-accent/20 rounded-full" />
            <div className="h-6 w-20 bg-primary/20 rounded-full" />
          </div>
          <div className="h-32 w-full bg-primary/10 rounded mb-6" />
          <div className="h-24 w-full bg-secondary/10 rounded" />
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
  if (!exercise) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg text-text">
        No hay datos del ejercicio.
      </div>
    );
  }

  return (
    <main className="relative min-h-screen bg-gradient-to-br from-bg to-surface flex items-start justify-center p-6 overflow-auto">
      <div className="relative w-full max-w-3xl bg-surface rounded-2xl shadow-2xl p-8">
        <div className="flex justify-between items-center mb-6">
          <Link
            href="/ejercicios"
            className="inline-flex items-center text-secondary hover:text-primary transition"
          >
            <span className="mr-1">←</span> Volver
          </Link>
          <LikeButton
            initialCount={exercise.likes_count}
            initialLiked={!!exercise.is_favourite}
            type="exercise"
            itemId={exercise.id}
          />
        </div>
        <div className="space-y-1 mb-6">
          <h1 className="text-3xl font-bold text-primary mb-1">
            {exercise.exerciseName}
          </h1>
          {exercise.instructions && exercise.instructions !== "N/A" && (
            <div className="space-y-1">
              {exercise.instructions
                .split(/\n\s*\n+/)
                .map((parrafo, idx) => parrafo.trim())
                .filter(Boolean)
                .map((parrafo, idx) => (
                  <p key={idx} className="text-text leading-relaxed m-0">
                    {parrafo}
                  </p>
                ))}
            </div>
          )}
        </div>
        <div className="flex flex-wrap gap-2 mb-6 w-full">
          <Tag label={exercise.exerciseCategory} color="primary" />
          {exercise.priMuscles && exercise.priMuscles.length > 0 && (
            <Tag
              label={exercise.priMuscles.map((m) => m.name).join(", ")}
              color="accent"
            />
          )}
          {exercise.secMuscles && exercise.secMuscles.length > 0 && (
            <Tag
              label={exercise.secMuscles.map((m) => m.name).join(", ")}
              color="secondary"
            />
          )}
          {exercise.equipment && exercise.equipment !== "N/A" && (
            <Tag label={exercise.equipment} color="equipment" />
          )}
        </div>
        {exercise.video && (
          <div className="mb-6">
            {exercise.video.includes("youtube.com") ||
            exercise.video.includes("youtu.be") ? (
              // Si la URL contiene consent.youtube.com, mostrar el fallback directamente
              iframeError || exercise.video.includes("consent.youtube.com") ? (
                <div className="flex flex-col items-center justify-center bg-red-50 border border-red-200 rounded-lg p-4">
                  <span className="text-red-700 mb-2 font-semibold">
                    No se puede mostrar el vídeo embebido aquí.
                  </span>
                  <a
                    href={exercise.video}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-700 underline font-medium"
                  >
                    Ver en YouTube
                  </a>
                </div>
              ) : (
                <div className="aspect-w-16 aspect-h-9 w-full">
                  <iframe
                    src={getYoutubeEmbedUrl(exercise.video)}
                    title="Video de ejercicio"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="w-full h-64 rounded-lg shadow border-none"
                    onLoad={() => {
                      iframeLoaded.current = true;
                    }}
                  />
                </div>
              )
            ) : (
              <video
                src={exercise.video}
                controls
                className="w-full rounded-lg shadow"
              />
            )}
          </div>
        )}
        {/* Comentarios */}
        <CommentBox
          workoutId={exercise.id}
          token={
            typeof window !== "undefined"
              ? localStorage.getItem("authToken")
              : null
          }
        />
      </div>
    </main>
  );
}

function Tag({
  label,
  color,
}: {
  label: string | JSX.Element;
  color: "primary" | "secondary" | "accent" | "equipment";
}): JSX.Element {
  let icon = null;
  if (color === "primary") {
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          width="16"
          height="16"
          className="inline"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M7.0498 7.0498H7.0598M10.5118 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V10.5118C3 11.2455 3 11.6124 3.08289 11.9577C3.15638 12.2638 3.27759 12.5564 3.44208 12.8249C3.6276 13.1276 3.88703 13.387 4.40589 13.9059L9.10589 18.6059C10.2939 19.7939 10.888 20.388 11.5729 20.6105C12.1755 20.8063 12.8245 20.8063 13.4271 20.6105C14.112 20.388 14.7061 19.7939 15.8941 18.6059L18.6059 15.8941C19.7939 14.7061 20.388 14.112 20.6105 13.4271C20.8063 12.8245 20.8063 12.1755 20.6105 11.5729C20.388 10.888 19.7939 10.2939 18.6059 9.10589L13.9059 4.40589C13.387 3.88703 13.1276 3.6276 12.8249 3.44208C12.5564 3.27759 12.2638 3.15638 11.9577 3.08289C11.6124 3 11.2455 3 10.5118 3ZM7.5498 7.0498C7.5498 7.32595 7.32595 7.5498 7.0498 7.5498C6.77366 7.5498 6.5498 7.32595 6.5498 7.0498C6.5498 6.77366 6.77366 6.5498 7.0498 6.5498C7.32595 6.5498 7.5498 6.77366 7.5498 7.0498Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></path>
        </svg>
      </span>
    );
  } else if (color === "accent") {
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg
          viewBox="0 0 24 24"
          width="14"
          height="14"
          className="mr-1"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
        >
          <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            <defs>
              <style>{`.cls-1{fill:none;stroke:currentColor;stroke-miterlimit:10;stroke-width:1.91px;}`}</style>
            </defs>
            <path
              className="cls-1"
              d="M9.14,16.77S8,13.17,10.09,11A14.12,14.12,0,0,1,13,9.13a4.78,4.78,0,1,1,5.61,4.7c-1.83,2.77-5.83,7.71-11.33,7.71C4.36,21.54,1.5,13,1.5,9.13V4.48A2.26,2.26,0,0,1,3.64,2.23c1.73-.09,4,0,4.54,1.17C9,5.11,7.23,8.18,5.32,8.18c0,1.5,1.83,4.76,3.49,6.56"
            ></path>
          </g>
        </svg>
      </span>
    );
  } else if (color === "secondary") {
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg
          viewBox="0 0 24 24"
          width="14"
          height="14"
          className="mr-1"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
        >
          <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            <defs>
              <style>{`.cls-1{fill:none;stroke:currentColor;stroke-miterlimit:10;stroke-width:1.91px;}`}</style>
            </defs>
            <path
              className="cls-1"
              d="M9.14,16.77S8,13.17,10.09,11A14.12,14.12,0,0,1,13,9.13a4.78,4.78,0,1,1,5.61,4.7c-1.83,2.77-5.83,7.71-11.33,7.71C4.36,21.54,1.5,13,1.5,9.13V4.48A2.26,2.26,0,0,1,3.64,2.23c1.73-.09,4,0,4.54,1.17C9,5.11,7.23,8.18,5.32,8.18c0,1.5,1.83,4.76,3.49,6.56"
            ></path>
          </g>
        </svg>
      </span>
    );
  } else if (color === "equipment") {
    icon = (
      <span className="mr-1 align-middle inline-block">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          width="16"
          height="16"
          className="inline"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g id="SVGRepo_iconCarrier">
            <path
              d="M3.92443 18.6073L4.45475 18.077L3.92443 18.6073ZM5.39271 20.0756L4.86238 20.6059L5.39271 20.0756ZM9.06343 20.0756L8.5331 20.6059H8.5331L9.06343 20.0756ZM9.79757 20.8097L10.3279 20.2794L10.3279 20.2794L9.79757 20.8097ZM14.6055 19.3774L13.8811 19.1833L13.8811 19.1833L14.6055 19.3774ZM14.6055 18.5713L13.8811 18.7654L14.6055 18.5713ZM12.036 21.9469L11.8419 21.2225H11.8419L12.036 21.9469ZM11.2299 21.9469L11.424 21.2225L11.2299 21.9469ZM2.05306 11.964L2.77751 12.1581V12.1581L2.05306 11.964ZM3.19028 14.2024L2.65995 14.7328L3.19028 14.2024ZM2.05306 12.7701L1.32862 12.9643L2.05306 12.7701ZM4.62257 9.3945L4.81668 10.1189H4.81668L4.62257 9.3945ZM5.42871 9.3945L5.62283 8.67005V8.67005L5.42871 9.3945ZM20.0756 9.06343L19.5452 9.59376L20.0756 9.06343ZM20.8097 9.79757L21.34 9.26724L20.8097 9.79757ZM19.3774 14.6055L19.1833 13.8811H19.1833L19.3774 14.6055ZM18.5713 14.6055L18.7654 13.8811L18.7654 13.8811L18.5713 14.6055ZM21.9469 12.036L21.2225 11.8419L21.2225 11.8419L21.9469 12.036ZM21.9469 11.2299L21.2225 11.424L21.2225 11.424L21.9469 11.2299ZM11.964 2.05307L11.7699 1.32862V1.32862L11.964 2.05307ZM14.2024 3.19028L13.6721 3.72061L14.2024 3.19028ZM12.7701 2.05307L12.576 2.77751V2.77751L12.7701 2.05307ZM9.3945 4.62257L8.67005 4.42845V4.42845L9.3945 4.62257ZM9.3945 5.42871L10.1189 5.2346V5.2346L9.3945 5.42871ZM7.02426 16.9757C7.31715 17.2686 7.31715 17.7435 7.02426 18.0364C6.73136 18.3293 6.25649 18.3293 5.9636 18.0364L7.02426 16.9757ZM18.0364 5.9636C18.3293 6.25649 18.3293 6.73136 18.0364 7.02426C17.7435 7.31715 17.2686 7.31715 16.9757 7.02426L18.0364 5.9636ZM11.6329 7.96221L12.1633 7.43188L11.6329 7.96221ZM4.45475 18.077L5.92304 19.5452L4.86238 20.6059L3.39409 19.1376L4.45475 18.077ZM19.5452 5.92304L18.077 4.45475L19.1376 3.39409L20.6059 4.86238L19.5452 5.92304ZM19.5452 7.79895C19.9063 7.43788 20.1226 7.2193 20.258 7.04192C20.3203 6.96028 20.346 6.9114 20.3567 6.88584C20.3649 6.86626 20.3638 6.86179 20.3638 6.861L21.8638 6.861C21.8638 7.30594 21.6745 7.65828 21.4505 7.95179C21.2398 8.22799 20.937 8.52853 20.6059 8.85961L19.5452 7.79895ZM20.6059 4.86238C20.937 5.19347 21.2398 5.49401 21.4505 5.77021C21.6745 6.06372 21.8638 6.41605 21.8638 6.861L20.3638 6.861C20.3638 6.8602 20.3649 6.85573 20.3567 6.83615C20.346 6.8106 20.3203 6.76171 20.258 6.68008C20.1226 6.50269 19.9063 6.28411 19.5452 5.92304L20.6059 4.86238ZM5.92304 19.5452C6.28411 19.9063 6.50269 20.1226 6.68008 20.258C6.76171 20.3203 6.8106 20.346 6.83615 20.3567C6.85573 20.3649 6.8602 20.3638 6.861 20.3638L6.861 21.8638C6.41605 21.8638 6.06372 21.6745 5.77021 21.4505C5.49401 21.2398 5.19347 20.937 4.86238 20.6059L5.92304 19.5452ZM8.85961 20.6059C8.52853 20.937 8.22799 21.2398 7.95179 21.4505C7.65828 21.6745 7.30594 21.8638 6.861 21.8638L6.861 20.3638C6.86179 20.3638 6.86626 20.3649 6.88584 20.3567C6.9114 20.346 6.96028 20.3203 7.04191 20.258C7.2193 20.1226 7.43788 19.9063 7.79895 19.5452L8.85961 20.6059ZM4.45475 16.201C4.09368 16.5621 3.87736 16.7807 3.74201 16.9581C3.67973 17.0397 3.65396 17.0886 3.6433 17.1142C3.63513 17.1337 3.63619 17.1382 3.63619 17.139L2.13619 17.139C2.13619 16.6941 2.32554 16.3417 2.54948 16.0482C2.76022 15.772 3.06301 15.4715 3.39409 15.1404L4.45475 16.201ZM3.39409 19.1376C3.06301 18.8065 2.76022 18.506 2.54948 18.2298C2.32554 17.9363 2.13619 17.5839 2.13619 17.139L3.63619 17.139C3.63619 17.1398 3.63513 17.1443 3.6433 17.1638C3.65396 17.1894 3.67973 17.2383 3.74201 17.3199C3.87736 17.4973 4.09368 17.7159 4.45475 18.077L3.39409 19.1376ZM15.1404 3.39409C15.4715 3.06301 15.772 2.76022 16.0482 2.54948C16.3417 2.32554 16.6941 2.13619 17.139 2.13619L17.139 3.63619C17.1382 3.63619 17.1337 3.63513 17.1142 3.6433C17.0886 3.65396 17.0397 3.67973 16.9581 3.74201C16.7807 3.87736 16.5621 4.09368 16.201 4.45475L15.1404 3.39409ZM18.077 4.45475C17.7159 4.09368 17.4973 3.87736 17.3199 3.74201C17.2383 3.67973 17.1894 3.65396 17.1638 3.6433C17.1443 3.63513 17.1398 3.63619 17.139 3.63619L17.139 2.13619C17.5839 2.13619 17.9363 2.32554 18.2298 2.54948C18.506 2.76022 18.8065 3.06301 19.1376 3.39409L18.077 4.45475ZM9.59376 19.5452L10.3279 20.2794L9.26724 21.34L8.5331 20.6059L9.59376 19.5452ZM12.938 20.2794C13.2908 19.9266 13.5194 19.6969 13.6777 19.5071C13.8292 19.3253 13.8669 19.2363 13.8811 19.1833L15.3299 19.5715C15.2361 19.9216 15.0482 20.2057 14.8297 20.4677C14.6179 20.7218 14.3319 21.0067 13.9986 21.34L12.938 20.2794ZM13.9986 16.6087C14.3319 16.942 14.6179 17.2269 14.8297 17.481C15.0482 17.743 15.2361 18.0271 15.3299 18.3772L13.8811 18.7654C13.8669 18.7124 13.8292 18.6234 13.6777 18.4416C13.5194 18.2518 13.2908 18.0222 12.938 17.6693L13.9986 16.6087ZM13.8811 19.1833C13.9177 19.0464 13.9177 18.9023 13.8811 18.7654L15.3299 18.3772C15.4348 18.7684 15.4348 19.1803 15.3299 19.5715L13.8811 19.1833ZM13.9986 21.34C13.6653 21.6734 13.3804 21.9593 13.1263 22.1712C12.8643 22.3896 12.5802 22.5776 12.2301 22.6714L11.8419 21.2225C11.8949 21.2083 11.9839 21.1707 12.1657 21.0191C12.3555 20.8609 12.5851 20.6322 12.938 20.2794L13.9986 21.34ZM10.3279 20.2794C10.6807 20.6322 10.9104 20.8609 11.1002 21.0191C11.282 21.1707 11.371 21.2083 11.424 21.2225L11.0357 22.6714C10.6857 22.5776 10.4016 22.3896 10.1396 22.1712C9.88548 21.9593 9.60055 21.6734 9.26724 21.34L10.3279 20.2794ZM12.2301 22.6714C11.8389 22.7762 11.427 22.7762 11.0357 22.6714L11.424 21.2225C11.5609 21.2592 11.705 21.2592 11.8419 21.2225L12.2301 22.6714ZM3.72061 11.062C3.36778 11.4149 3.13912 11.6445 2.98091 11.8343C2.82932 12.0161 2.79171 12.1051 2.77751 12.1581L1.32862 11.7699C1.42242 11.4198 1.61035 11.1357 1.82884 10.8737C2.04069 10.6196 2.32664 10.3347 2.65995 10.0014L3.72061 11.062ZM2.65995 14.2024L2.13619 14.7328L2.65995 14.2024ZM2.77751 12.1581C2.74083 12.295 2.74083 12.4391 2.77751 12.576L1.32862 12.9643C1.22379 12.573 1.22379 12.1611 1.32862 11.7699L2.77751 12.1581ZM2.65995 10.0014C2.99326 9.66807 3.27819 9.38212 3.53228 9.17027C3.79432 8.95178 4.07838 8.76385 4.42845 8.67005L4.81668 10.1189C4.76368 10.1331 4.67467 10.1708 4.49287 10.3223C4.30312 10.4806 4.07344 10.7092 3.72061 11.062L2.65995 10.0014ZM6.33067 11.062C5.97784 10.7092 5.74816 10.4806 5.55841 10.3223C5.37661 10.1708 5.2876 10.1331 5.2346 10.1189L5.62283 8.67005C5.9729 8.76385 6.25696 8.95178 6.519 9.17027C6.77308 9.38212 7.05802 9.66807 7.39133 10.0014L6.33067 11.062ZM4.42845 8.67005C4.81968 8.56522 5.2316 8.56523 5.62283 8.67005L5.2346 10.1189C5.09771 10.0823 4.95357 10.0823 4.81668 10.1189L4.42845 8.67005ZM20.6059 8.5331L21.34 9.26724L20.2794 10.3279L19.5452 9.59376L20.6059 8.5331ZM21.34 13.9986C21.0067 14.3319 20.7218 14.6179 20.4677 14.8297C20.2057 15.0482 19.9216 15.2361 19.5715 15.3299L19.1833 13.8811C19.2363 13.8669 19.3253 13.8292 19.5071 13.6777C19.6969 13.5194 19.9266 13.2908 20.2794 12.938L21.34 13.9986ZM17.6693 12.938C18.0222 13.2908 18.2518 13.5194 18.4416 13.6777C18.6234 13.8292 18.7124 13.8669 18.7654 13.8811L18.3772 15.3299C18.0271 15.2361 17.743 15.0482 17.481 14.8297C17.2269 14.6179 16.942 14.3319 16.6087 13.9986L17.6693 12.938ZM19.5715 15.3299C19.1803 15.4348 18.7684 15.4348 18.3772 15.3299L18.7654 13.8811C18.9023 13.9177 19.0464 13.9177 19.1833 13.8811L19.5715 15.3299ZM20.2794 12.938C20.6322 12.5851 20.8609 12.3555 21.0191 12.1657C21.1707 11.9839 21.2083 11.8949 21.2225 11.8419L22.6714 12.2301C22.5776 12.5802 22.3896 12.8643 22.1712 13.1263C21.9593 13.3804 21.6734 13.6653 21.34 13.9986L20.2794 12.938ZM21.34 9.26724C21.6734 9.60055 21.9593 9.88548 22.1712 10.1396C22.3896 10.4016 22.5776 10.6857 22.6714 11.0357L21.2225 11.424C21.2083 11.371 21.1707 11.282 21.0191 11.1002C20.8609 10.9104 20.6322 10.6807 20.2794 10.3279L21.34 9.26724ZM21.2225 11.8419C21.2592 11.705 21.2592 11.5609 21.2225 11.424L22.6714 11.0357C22.7762 11.427 22.7762 11.8389 22.6714 12.2301L21.2225 11.8419ZM10.0014 2.65995C10.3347 2.32664 10.6196 2.04069 10.8737 1.82884C11.1357 1.61035 11.4198 1.42242 11.7699 1.32862L12.1581 2.77751C12.1051 2.79171 12.0161 2.82932 11.8343 2.98091C11.6445 3.13912 11.4149 3.36778 11.062 3.72061L10.0014 2.65995ZM13.6721 3.72061C13.3193 3.36778 13.0896 3.13912 12.8998 2.98091C12.718 2.82932 12.629 2.79171 12.576 2.77751L12.9643 1.32862C13.3143 1.42242 13.5984 1.61035 13.8604 1.82884C14.1145 2.04069 14.3994 2.32664 14.7328 2.65995L13.6721 3.72061ZM11.7699 1.32862C12.1611 1.22379 12.573 1.22379 12.9643 1.32862L12.576 2.77751C12.4391 2.74083 12.295 2.74083 12.1581 2.77751L11.7699 1.32862ZM11.062 3.72061C10.7092 4.07344 10.4806 4.30312 10.3223 4.49287C10.1708 4.67467 10.1331 4.76368 10.1189 4.81668L8.67005 4.42845C8.76385 4.07838 8.95178 3.79432 9.17027 3.53228C9.38212 3.27819 9.66807 2.99326 10.0014 2.65995L11.062 3.72061ZM10.0014 7.39133C9.66807 7.05802 9.38212 6.77308 9.17027 6.519C8.95178 6.25696 8.76386 5.9729 8.67005 5.62283L10.1189 5.2346C10.1331 5.2876 10.1708 5.37661 10.3223 5.55841C10.4806 5.74816 10.7092 5.97784 11.062 6.33067L10.0014 7.39133ZM10.1189 4.81668C10.0823 4.95357 10.0823 5.0977 10.1189 5.2346L8.67005 5.62283C8.56523 5.2316 8.56522 4.81968 8.67005 4.42845L10.1189 4.81668ZM3.72061 13.6721L7.02426 16.9757L5.9636 18.0364L2.65995 14.7328L3.72061 13.6721ZM14.7328 2.65995L18.0364 5.9636L16.9757 7.02426L13.6721 3.72061L14.7328 2.65995ZM12.938 17.6693L11.8367 16.5681L12.8974 15.5075L13.9986 16.6087L12.938 17.6693ZM11.8367 15.5075L15.5075 11.8367L16.5681 12.8974L12.8974 16.5681L11.8367 15.5075ZM16.6087 13.9986L15.5075 12.8974L16.5681 11.8367L17.6693 12.938L16.6087 13.9986ZM11.8367 16.5681L7.43188 12.1633L8.49254 11.1026L12.8974 15.5075L11.8367 16.5681ZM7.43188 12.1633L6.33067 11.062L7.39133 10.0014L8.49254 11.1026L7.43188 12.1633ZM12.1633 8.49254L8.49254 12.1633L7.43188 11.1026L11.1026 7.43188L12.1633 8.49254ZM15.5075 12.8974L11.1026 8.49254L12.1633 7.43188L16.5681 11.8367L15.5075 12.8974ZM11.1026 8.49254L10.0014 7.39133L11.062 6.33067L12.1633 7.43188L11.1026 8.49254ZM19.5452 9.59376C19.0496 9.09814 19.0496 8.29458 19.5452 7.79895L20.6059 8.85961C20.6961 8.76945 20.6961 8.62326 20.6059 8.5331L19.5452 9.59376ZM8.5331 20.6059C8.62326 20.6961 8.76945 20.6961 8.85961 20.6059L7.79895 19.5452C8.29457 19.0496 9.09814 19.0496 9.59376 19.5452L8.5331 20.6059Z"
              fill="#1C274C"
            ></path>
          </g>
        </svg>
      </span>
    );
  }
  // Definir clases de fondo y texto explícitamente para evitar errores de variables no definidas
  let bg = "";
  let text = "";
  switch (color) {
    case "primary":
      bg = "bg-primary/10";
      text = "text-primary";
      break;
    case "secondary":
      bg = "bg-blue-100";
      text = "text-blue-800";
      break;
    case "accent":
      bg = "bg-blue-200";
      text = "text-blue-900";
      break;
    case "equipment":
      bg = "bg-green-100";
      text = "text-green-800";
      break;
    default:
      bg = "bg-gray-100";
      text = "text-gray-800";
  }
  return (
    <span
      className={`${bg} ${text} px-2 py-1 rounded-full text-xs font-medium inline-flex items-center`}
    >
      {icon}
      {label}
    </span>
  );
}

// Helper para obtener la URL de embed de YouTube
function getYoutubeEmbedUrl(url: string): string {
  // Si ya es embed, devolver tal cual
  if (url.includes("/embed/")) return url;
  // Si es consent.youtube.com, devolver tal cual (se mostrará fallback)
  if (url.includes("consent.youtube.com")) return url;
  // Extraer ID del vídeo de todos los formatos posibles
  let videoId = "";
  // Soporta: /watch?v=, /embed/, /v/, youtu.be/
  const ytMatch = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([\w-]{11})/
  );
  if (ytMatch && ytMatch[1]) {
    videoId = ytMatch[1];
  } else {
    // Fallback: intentar extraer v=...
    const vParam = url.match(/[?&]v=([\w-]{11})/);
    if (vParam && vParam[1]) videoId = vParam[1];
  }
  return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
}
