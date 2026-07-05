"use client";

import { useCallback, useRef, useState } from "react";
import { useRequireAuth } from "@/lib/useRequireAuth";
import { ApiError, uploadAudioFile, type Call } from "@/lib/api";

type UploadItem = {
  id: string;
  fileName: string;
  status: "pending" | "success" | "error";
  error?: string;
  call?: Call;
};

export default function UploadFilesPage() {
  const ready = useRequireAuth();
  const [items, setItems] = useState<UploadItem[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadFiles = useCallback((files: FileList | File[]) => {
    Array.from(files).forEach((file) => {
      const id = `${file.name}-${Date.now()}-${Math.random()}`;
      setItems((prev) => [{ id, fileName: file.name, status: "pending" }, ...prev]);

      uploadAudioFile(file)
        .then((call) => {
          setItems((prev) =>
            prev.map((item) => (item.id === id ? { ...item, status: "success", call } : item))
          );
        })
        .catch((err) => {
          setItems((prev) =>
            prev.map((item) =>
              item.id === id
                ? {
                    ...item,
                    status: "error",
                    error: err instanceof ApiError ? err.message : "Upload failed",
                  }
                : item
            )
          );
        });
    });
  }, []);

  if (!ready) return null;

  return (
    <div className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900 dark:text-zinc-50">
        Upload call recordings
      </h1>

      <div
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragActive(false);
          if (event.dataTransfer.files.length) uploadFiles(event.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-16 text-center transition-colors ${
          dragActive
            ? "border-zinc-900 bg-zinc-100 dark:border-zinc-100 dark:bg-zinc-900"
            : "border-black/15 dark:border-white/15"
        }`}
      >
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Drag and drop audio files here, or click to browse
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="audio/*"
          multiple
          className="hidden"
          onChange={(event) => {
            if (event.target.files?.length) uploadFiles(event.target.files);
            event.target.value = "";
          }}
        />
      </div>

      {items.length > 0 && (
        <ul className="mt-8 divide-y divide-black/10 dark:divide-white/10">
          {items.map((item) => (
            <li key={item.id} className="flex items-center justify-between py-3 text-sm">
              <span className="truncate pr-4 text-zinc-800 dark:text-zinc-200">
                {item.fileName}
              </span>
              {item.status === "pending" && <span className="text-zinc-500">Uploading…</span>}
              {item.status === "success" && (
                <span className="text-green-600 dark:text-green-400">Uploaded</span>
              )}
              {item.status === "error" && (
                <span className="text-red-600 dark:text-red-400">{item.error}</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
