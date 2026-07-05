"use client";

import { ApiError, listCalls, type Call } from "@/lib/api";
import { useRequireAuth } from "@/lib/useRequireAuth";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function ListCallsPage() {
  const ready = useRequireAuth();
  const [calls, setCalls] = useState<Call[] | null>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    listCalls()
      .then(setCalls)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? `${err.message} — this endpoint may not be implemented on the backend yet.`
            : "Failed to load calls."
        )
      );
  }, [ready]);

  if (!ready) return null;

  return (
    <div className="mx-auto w-full max-w-3xl flex-1 px-6 py-12">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900 dark:text-zinc-50">Calls</h1>

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
      {!error && calls === null && <p className="text-sm text-zinc-500">Loading…</p>}
      {calls !== null && calls.length === 0 && (
        <p className="text-sm text-zinc-500">No calls uploaded yet.</p>
      )}

      {calls && calls.length > 0 && (
        <ul className="divide-y divide-black/10 dark:divide-white/10">
          {calls.map((call) => (
            <li key={call.call_id} className="flex items-center justify-between py-3 text-sm">
              <Link
                href={`/call-details/${call.call_id}`}
                className="text-zinc-800 hover:underline dark:text-zinc-200"
              >
                {call.call_id} — {call.status}
              </Link>
              <div className="flex gap-3">
                {call.uploaded_audio_files.map((file) => (
                  <a
                    key={file.id}
                    href={file.audio}
                    download
                    className="text-zinc-500 hover:underline"
                  >
                    Download
                  </a>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
