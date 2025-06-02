// File: src/components/LikeButton.tsx
"use client";

import React, { useState } from "react";
import { FaHeart, FaRegHeart } from "react-icons/fa";

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

  const toggleLike = async () => {
    if (loading) return;
    setLoading(true);

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        console.error("Token not found");
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
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}social/favourites/`, {
          method: "POST",
          headers,
          body,
        });
        setLiked(true);
        setCount(count + 1);
      } else {
        // Quitar like
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}social/favourites/delete-by-type/`, {
          method: "DELETE",
          headers,
          body,
        });
        setLiked(false);
        setCount(count - 1);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={toggleLike}
      disabled={loading}
      className="inline-flex items-center space-x-2 text-text hover:text-red-600 transition px-3 py-1 rounded-full font-medium bg-red-200"
    >
      <span>{count}</span>
      {liked ? (
        <FaHeart className="h-5 w-5 text-red-600" />
      ) : (
        <FaRegHeart className="h-5 w-5" />
      )}
    </button>
  );
}
