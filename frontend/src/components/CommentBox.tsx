import React, { useEffect, useState } from "react";

interface Comment {
  id: number;
  user: string;
  comment: string;
  date_added: string;
  reported: boolean;
}

interface CommentBoxProps {
  workoutId: number;
  token: string | null;
}

export default function CommentBox({ workoutId, token }: CommentBoxProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [posting, setPosting] = useState(false);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}social/comments/?workout=${workoutId}`,
        { headers: token ? { Authorization: `Token ${token}` } : {} }
      );
      if (!res.ok) throw new Error("Error al cargar comentarios");
      const data = await res.json();
      setComments(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
    // eslint-disable-next-line
  }, [workoutId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setPosting(true);
    setError(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}social/comments/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Token ${token}` } : {}),
          },
          body: JSON.stringify({ workout: workoutId, comment: newComment }),
        }
      );
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Error al enviar comentario");
      }
      setNewComment("");
      fetchComments();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  };

  const handleReport = async (id: number) => {
    if (!token) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}social/comments/${id}/`,
        {
          method: "PATCH",
          headers: { Authorization: `Token ${token}` },
        }
      );
      if (!res.ok) throw new Error("Error al reportar comentario");
      // Actualizar el estado local para reflejar el reporte
      setComments((prev) =>
        prev.map((c) => (c.id === id ? { ...c, reported: true } : c))
      );
    } catch {
      alert("Error al reportar comentario");
    }
  };

  return (
    <div className="mt-10">
        <hr className="border-secondary"/>
      <h2 className="text-2xl text-center font-bold mt-4 mb-6 text-primary">Comentarios</h2>
      {loading ? (
        <div className="text-secondary">Cargando comentarios...</div>
      ) : (
        <ul className="space-y-4 mb-6">
          {comments.length === 0 && (
            <li className="text-text italic">Sé el primero en comentar esta rutina.</li>
          )}
          {comments.map((c) => (
            <li
              key={c.id}
              className={`bg-bg border border-border rounded-lg p-4 ${c.reported ? 'opacity-60 bg-red-100' : ''}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-primary">{c.user}</span>
                <div className="flex items-center">
                  <span className="text-xs text-secondary">{new Date(c.date_added).toLocaleString()}</span>
                  {token && !c.reported && (
                    <button 
                      className="flex gap-1 text-xs text-red-600 ml-6"
                      onClick={() => handleReport(c.id)}
                      title="Reportar comentario"
                    >  
                      Reportar
                      <svg fill="#ff0000" width={16} height={16} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke="#ff0000"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fillRule="evenodd" d="M16,2 C16.2652165,2 16.5195704,2.10535684 16.7071068,2.29289322 L21.7071068,7.29289322 C21.8946432,7.4804296 22,7.73478351 22,8 L22,15 C22,15.2339365 21.9179838,15.4604694 21.7682213,15.6401844 L16.7682213,21.6401844 C16.5782275,21.868177 16.2967798,22 16,22 L8,22 C7.73478351,22 7.4804296,21.8946432 7.29289322,21.7071068 L2.29289322,16.7071068 C2.10535684,16.5195704 2,16.2652165 2,16 L2,8 C2,7.73478351 2.10535684,7.4804296 2.29289322,7.29289322 L7.29289322,2.29289322 C7.4804296,2.10535684 7.73478351,2 8,2 L16,2 Z M15.5857864,4 L8.41421356,4 L4,8.41421356 L4,15.5857864 L8.41421356,20 L15.5316251,20 L20,14.6379501 L20,8.41421356 L15.5857864,4 Z M12,16 C12.5522847,16 13,16.4477153 13,17 C13,17.5522847 12.5522847,18 12,18 C11.4477153,18 11,17.5522847 11,17 C11,16.4477153 11.4477153,16 12,16 Z M12,6 C12.5522847,6 13,6.44771525 13,7 L13,13 C13,13.5522847 12.5522847,14 12,14 C11.4477153,14 11,13.5522847 11,13 L11,7 C11,6.44771525 11.4477153,6 12,6 Z"></path> </g></svg>
                    </button>
                  )}
                  {c.reported && (
                    <div className="flex items-center text-secondary gap-1 ml-8">
                        <span className="text-xs">Reportado</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="text-text mb-2">{c.comment}</div>
            </li>
          ))}
        </ul>
      )}
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {token ? (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            className="flex-1 border border-border rounded px-3 py-2"
            placeholder="Escribe un comentario..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            disabled={posting}
            maxLength={500}
            required
          />
          <button
            type="submit"
            className="bg-primary text-surface px-4 py-2 rounded hover:bg-primary/80 transition"
            disabled={posting}
          >
            {posting ? "Enviando..." : "Comentar"}
          </button>
        </form>
      ) : (
        <div className="text-secondary">Inicia sesión para comentar.</div>
      )}
    </div>
  );
}
