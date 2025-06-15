// File: src/components/LikeButton.tsx
"use client";

import React, { useState } from "react";
import { FaHeart, FaRegHeart } from "react-icons/fa";
import AccessDeniedModal from "@/components/AccessDeniedModal";

export default function LikeButton({
  initialCount,
  initialLiked,
  type,
  itemId,
}: {
  initialCount: number;
  initialLiked: boolean;
  type: "workout" | "exercise";
  itemId: number;
}) {
  const [liked, setLiked] = useState(initialLiked);
  const [count, setCount] = useState(initialCount);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleLike = async () => {
    if (loading) return;
    setLoading(true);

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        console.warn("Token not found, mostrando modal de acceso");
        setIsModalOpen(true);
        setLoading(false);
        return;
      }

      const body = JSON.stringify({ [type]: itemId });
      const headers = {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      };

      if (!liked) {
        // Dar like
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}social/favourites/`,
          {
            method: "POST",
            headers,
            body,
          }
        );
        if (!res.ok) {
          console.error("Error al dar like:", res.statusText);
        } else {
          setLiked(true);
          setCount((c) => c + 1);
        }
      } else {
        // Quitar like
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}social/favourites/delete-by-type/`,
          {
            method: "DELETE",
            headers,
            body,
          }
        );
        if (!res.ok) {
          console.error("Error al quitar like:", res.statusText);
        } else {
          setLiked(false);
          setCount((c) => c - 1);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={toggleLike}
        disabled={loading}
        className="inline-flex items-center space-x-2 text-text hover:text-red-600 transition px-3 py-1 rounded-full font-medium bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span>{count}</span>
        {liked ? (
          <FaHeart className="h-5 w-5 text-red-600" />
        ) : (
          <FaRegHeart className="h-5 w-5" />
        )}
      </button>

      {isModalOpen && (
        <AccessDeniedModal onClose={() => setIsModalOpen(false)} />
      )}
    </>
  );
}
