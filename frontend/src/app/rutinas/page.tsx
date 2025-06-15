"use client";

import LikeButton from "@/components/LikeButton";
import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";

export default function RutinasPage() {
  const [rutinas, setRutinas] = useState<any[]>([]);
  const [favs, setFavs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [level, setLevel] = useState("");
  const [gender, setGender] = useState("");
  const [order, setOrder] = useState("name");
  const PAGE_SIZE = 12;
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const [categoryOptions, setCategoryOptions] = useState([
    { value: "", label: "Todas las categorías" },
  ]);
  const [levelOptions, setLevelOptions] = useState([
    { value: "", label: "Todos los niveles" },
  ]);
  const [genderOptions, setGenderOptions] = useState([
    { value: "", label: "Todos los géneros" },
  ]);

  const fetchMoreRutinas = async () => {
    try {
      const params = new URLSearchParams({
        page: String(page + 1),
        page_size: String(PAGE_SIZE),
        ...(search && { term: search }),
        ...(category && { cat: category }),
        ...(level && { level: level }),
        ...(gender && { gender: gender }),
        ...(order && { order }),
      });
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}workouts/?${params.toString()}`
      );
      if (!res.ok) {
        setHasMore(false);
        return;
      }
      const newRutinasData = await res.json();
      if (newRutinasData.results.length < PAGE_SIZE) setHasMore(false);
      setRutinas((prev: any[]) => [...prev, ...newRutinasData.results]);
      setPage((prev) => prev + 1);
    } catch {}
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setPage(1);
        setHasMore(true);
        const token = localStorage.getItem("authToken");
        const params = new URLSearchParams({
          page: "1",
          page_size: String(PAGE_SIZE),
          ...(search && { term: search }),
          ...(category && { cat: category }),
          ...(level && { level: level }),
          ...(gender && { gender: gender }),
          ...(order && { order }),
        });
        const rutRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}workouts/?${params.toString()}`,
          { cache: "no-store" }
        );
        if (!rutRes.ok) throw new Error("Error al cargar rutinas");
        const rutinasData = await rutRes.json();
        let favsData: any[] = [];
        if (token) {
          const favRes = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}social/favourites/`,
            {
              headers: { Authorization: `Token ${token}` },
            }
          );
          if (favRes.ok) {
            favsData = await favRes.json();
          }
        }
        setRutinas(rutinasData.results);
        setFavs(favsData);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [search, order, category, level, gender]);

  // Elimina el efecto de debounce automático
  useEffect(() => {
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    debounceTimeout.current = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
      setHasMore(true);
    }, 200); // 0.4 segundos de margen
    return () => {
      if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    };
  }, [searchInput]);

  // if (loading) {
  //   return <div className="min-h-screen flex items-center justify-center bg-bg">Cargando...</div>;
  // }
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg text-red-500">
        {" "}
        <p className="text-text">No hay rutinas disponibles en este momento.</p>
      </div>
    );
  }

  // Fetch dropdown options from backend
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}workouts/options/`
        );
        if (!res.ok) throw new Error("Error al cargar opciones");
        const data = await res.json();
        setCategoryOptions([
          { value: "", label: "Todas las categorías" },
          ...data.categories
            .filter((c: string) => c !== "N/A")
            .map((c: string) => ({ value: c, label: c })),
        ]);
        setLevelOptions([
          { value: "", label: "Todos los niveles" },
          ...data.levels
            .filter((l: string) => l !== "N/A")
            .map((l: string) => ({ value: l, label: l })),
        ]);
        setGenderOptions([
          { value: "", label: "Todos los géneros" },
          ...data.genders
            .filter((g: string) => g !== "N/A")
            .map((g: string) => ({ value: g, label: g })),
        ]);
      } catch (e) {
        // fallback: keep default options
      }
    };
    fetchOptions();
  }, []);

  return (
    <main className="min-h-screen bg-bg text-text p-8">
      <h1 className="text-3xl font-bold mb-6">Listado de Rutinas</h1>
      <form
        className="flex flex-col sm:flex-row gap-4 mb-6 flex-wrap px-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSearch(searchInput);
          setPage(1);
          setHasMore(true);
        }}
      >
        {/* Input con icono de búsqueda */}
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/70 pointer-events-none">
            {/* Lupa */}
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
              <circle
                cx="11"
                cy="11"
                r="7"
                stroke="currentColor"
                strokeWidth="2"
              />
              <path
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                d="M20 20l-3.5-3.5"
              />
            </svg>
          </span>
          <input
            type="text"
            placeholder="Buscar por nombre..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-surface text-text shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 placeholder:text-secondary/70 h-[42px]"
          />
        </div>
        {/* Dropdown categoría con icono */}
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/70 pointer-events-none">
            {/* Nuevo icono categoría */}
            <svg
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
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
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="pl-10 pr-4 py-2 rounded-lg border border-border bg-surface text-text shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 cursor-pointer hover:border-primary h-[42px]"
          >
            {categoryOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {/* Dropdown nivel con icono */}
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/70 pointer-events-none">
            {/* Nuevo icono nivel */}
            <svg
              fill="none"
              viewBox="0 0 24 24"
              width="18"
              height="18"
              stroke="currentColor"
              strokeWidth="1.2"
            >
              <rect x="16" y="4" width="2" height="16" />
              <rect x="11" y="10" width="2" height="10" />
              <rect x="6" y="14" width="2" height="6" />
            </svg>
          </span>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="pl-10 pr-4 py-2 rounded-lg border border-border bg-surface text-text shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 cursor-pointer hover:border-primary h-[42px]"
          >
            {levelOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {/* Dropdown género con icono */}
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/70 pointer-events-none">
            {/* Nuevo icono género */}
            <svg
              viewBox="0 0 16 16"
              width="18"
              height="18"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
              <g
                id="SVGRepo_tracerCarrier"
                strokeLinecap="round"
                strokeLinejoin="round"
              ></g>
              <g id="SVGRepo_iconCarrier">
                {" "}
                <path
                  d="m 8 1 c -1.65625 0 -3 1.34375 -3 3 s 1.34375 3 3 3 s 3 -1.34375 3 -3 s -1.34375 -3 -3 -3 z m -1.5 7 c -2.492188 0 -4.5 2.007812 -4.5 4.5 v 0.5 c 0 1.109375 0.890625 2 2 2 h 8 c 1.109375 0 2 -0.890625 2 -2 v -0.5 c 0 -2.492188 -2.007812 -4.5 -4.5 -4.5 z m 0 0"
                  fill="currentColor"
                ></path>{" "}
              </g>
            </svg>
          </span>
          <select
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="pl-10 pr-4 py-2 rounded-lg border border-border bg-surface text-text shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 cursor-pointer hover:border-primary h-[42px]"
          >
            {genderOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {/* Dropdown orden con icono */}
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary/70 pointer-events-none">
            {/* Ordenar */}
            <svg
              viewBox="0 0 24 24"
              width="18"
              height="18"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
              <g
                id="SVGRepo_tracerCarrier"
                strokeLinecap="round"
                strokeLinejoin="round"
              ></g>
              <g id="SVGRepo_iconCarrier">
                {" "}
                <g id="Edit / Sort_Ascending">
                  {" "}
                  <path
                    id="Vector"
                    d="M4 17H10M4 12H13M18 11V19M18 19L21 16M18 19L15 16M4 7H16"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  ></path>{" "}
                </g>{" "}
              </g>
            </svg>{" "}
          </span>
          <select
            value={order}
            onChange={(e) => setOrder(e.target.value)}
            className="pl-10 pr-4 py-2 rounded-lg border border-border bg-surface text-text shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all duration-200 cursor-pointer hover:border-primary h-[42px]"
          >
            <option value="name">Nombre</option>
            <option value="popularity">Popularidad</option>
            <option value="likes_count">Likes</option>
            <option value="creationDate">Recientes</option>
          </select>
        </div>
        <button
          type="submit"
          className="px-4 py-2 rounded bg-primary text-surface font-semibold hover:bg-primary/80 shadow-sm transition-all duration-200 h-[42px]"
        >
          Buscar
        </button>
      </form>
      <InfiniteScroll
        dataLength={rutinas.length}
        next={fetchMoreRutinas}
        hasMore={hasMore}
        loader={
          hasMore && !loading && rutinas.length > 0 ? (
            <div className="text-center py-4">Cargando más rutinas...</div>
          ) : null
        }
        endMessage={
          <div className="text-center py-4 text-secondary">
            No hay más rutinas.
          </div>
        }
      >
        <ul className="flex flex-col gap-4 px-2">
          {loading
            ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                <li
                  key={i}
                  className="bg-surface border border-border rounded-lg p-6 shadow flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
                >
                  <div className="flex-1">
                    <Skeleton height={28} width={180} className="mb-2" />
                    <Skeleton height={20} width={120} className="mb-2" />
                    <Skeleton height={20} width={80} />
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <Skeleton circle height={32} width={32} />
                    <Skeleton height={20} width={90} />
                  </div>
                </li>
              ))
            : rutinas.length > 0 &&
              rutinas.map((rutina: any) => {
                const liked = favs.some(
                  (fav: any) => fav.workout === rutina.id
                );
                const favCount = rutina.likes_count || 0;
                return (
                  <li
                    key={rutina.id}
                    className="bg-surface border border-border rounded-lg p-6 shadow flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 transition-all duration-400 hover:shadow-lg cursor-pointer"
                  >
                    <div className="flex-1">
                      <Link
                        href={`/rutinas/${rutina.id}`}
                        className="hover:underline"
                      >
                        <h2 className="text-xl font-semibold text-primary">
                          {rutina.workoutName}
                        </h2>
                      </Link>
                      <div className="flex flex-wrap gap-2 my-4">
                        {/* Partes del cuerpo */}
                        {rutina.bodyPart && (
                          <span className="inline-flex items-center bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs font-medium">
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
                            {rutina.bodyPart.replace(/,/g, ", ")}
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {/* Categoría */}
                        <span className="inline-flex items-center bg-primary/10 text-primary px-2 py-1 rounded-full text-xs font-medium">
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            width="14"
                            height="14"
                            className="mr-1"
                          >
                            <path
                              d="M7.0498 7.0498H7.0598M10.5118 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V10.5118C3 11.2455 3 11.6124 3.08289 11.9577C3.15638 12.2638 3.27759 12.5564 3.44208 12.8249C3.6276 13.1276 3.88703 13.387 4.40589 13.9059L9.10589 18.6059C10.2939 19.7939 10.888 20.388 11.5729 20.6105C12.1755 20.8063 12.8245 20.8063 13.4271 20.6105C14.112 20.388 14.7061 19.7939 15.8941 18.6059L18.6059 15.8941C19.7939 14.7061 20.388 14.112 20.6105 13.4271C20.8063 12.8245 20.8063 12.1755 20.6105 11.5729C20.388 10.888 19.7939 10.2939 18.6059 9.10589L13.9059 4.40589C13.387 3.88703 13.1276 3.6276 12.8249 3.44208C12.5564 3.27759 12.2638 3.15638 11.9577 3.08289C11.6124 3 11.2455 3 10.5118 3ZM7.5498 7.0498C7.5498 7.32595 7.32595 7.5498 7.0498 7.5498C6.77366 7.5498 6.5498 7.32595 6.5498 7.0498C6.5498 6.77366 6.77366 6.5498 7.0498 6.5498C7.32595 6.5498 7.5498 6.77366 7.5498 7.0498Z"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            ></path>
                          </svg>
                          {rutina.workoutCategory}
                        </span>
                        {/* Nivel */}
                        <span className="inline-flex items-center bg-accent text-surface px-2 py-1 rounded-full text-xs font-medium">
                          <svg
                            fill="none"
                            viewBox="0 0 24 24"
                            width="14"
                            height="14"
                            stroke="currentColor"
                            strokeWidth="1.2"
                            className="mr-1"
                          >
                            <rect x="16" y="4" width="2" height="16" />
                            <rect x="11" y="10" width="2" height="10" />
                            <rect x="6" y="14" width="2" height="6" />
                          </svg>
                          {rutina.level}
                        </span>
                        {/* Género */}
                        <span className="inline-flex items-center bg-secondary text-surface px-2 py-1 rounded-full text-xs font-medium">
                          <svg
                            viewBox="0 0 16 16"
                            width="14"
                            height="14"
                            className="mr-1"
                          >
                            <path
                              d="m 8 1 c -1.65625 0 -3 1.34375 -3 3 s 1.34375 3 3 3 s 3 -1.34375 3 -3 s -1.34375 -3 -3 -3 z m -1.5 7 c -2.492188 0 -4.5 2.007812 -4.5 4.5 v 0.5 c 0 1.109375 0.890625 2 2 2 h 8 c 1.109375 0 2 -0.890625 2 -2 v -0.5 c 0 -2.492188 -2.007812 -4.5 -4.5 -4.5 z m 0 0"
                              fill="currentColor"
                            ></path>
                          </svg>
                          {rutina.gender}
                        </span>
                      </div>
                      {rutina.description && rutina.description !== "N/A" && (
                        <p className="text-xs text-secondary mb-2 line-clamp-2 max-w-xl">
                          {rutina.description}
                        </p>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <LikeButton
                        initialCount={favCount}
                        initialLiked={liked}
                        type="workout"
                        itemId={rutina.id}
                      />
                      <Link
                        href={`/rutinas/${rutina.id}`}
                        className="block text-secondary hover:underline"
                      >
                        Ver detalles
                      </Link>
                    </div>
                  </li>
                );
              })}
        </ul>
      </InfiniteScroll>
      {rutinas.length === 0 && !loading && (
        <div className="text-center bg-surface border border-border rounded-lg p-6 shadow mt-8">
          <p className="text-text">
            No hay rutinas disponibles en este momento.
          </p>
        </div>
      )}
    </main>
  );
}
