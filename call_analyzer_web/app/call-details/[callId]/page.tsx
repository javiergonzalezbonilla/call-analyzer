"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useRequireAuth } from "@/lib/useRequireAuth";
import { ApiError, getCall, type Call } from "@/lib/api";

export default function CallDetailsPage() {
  const ready = useRequireAuth();
  const params = useParams<{ callId: string }>();
  const [call, setCall] = useState<Call | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    getCall(params.callId)
      .then(setCall)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? `${err.message} — this endpoint may not be implemented on the backend yet.`
            : "Failed to load call."
        )
      );
  }, [ready, params.callId]);

  if (!ready) return null;

  return (
    <div className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
      <h1 className="mb-6 text-xl font-semibold text-zinc-900 dark:text-zinc-50">
        Call {params.callId}
      </h1>

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
      {!error && !call && <p className="text-sm text-zinc-500">Loading…</p>}

      {call && (
        <dl className="space-y-4 text-sm">
          <div>
            <dt className="text-zinc-500">Status</dt>
            <dd className="text-zinc-900 dark:text-zinc-100">{call.status}</dd>
          </div>

          {call.summary && (
            <div>
              <dt className="text-zinc-500">Summary</dt>
              <dd className="text-zinc-900 dark:text-zinc-100">{call.summary}</dd>
            </div>
          )}

          {call.transcript && (
            <div>
              <dt className="text-zinc-500">Transcript</dt>
              <dd className="whitespace-pre-wrap text-zinc-900 dark:text-zinc-100">
                {call.transcript}
              </dd>
            </div>
          )}

          <div>
            <dt className="mb-1 text-zinc-500">Audio files</dt>
            <dd>
              <ul className="space-y-1">
                {call.uploaded_audio_files.map((file) => (
                  <li key={file.id}>
                    <a
                      href={file.audio}
                      download
                      className="text-zinc-800 hover:underline dark:text-zinc-200"
                    >
                      {file.path}
                    </a>
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        </dl>
      )}
    </div>
  );
}
