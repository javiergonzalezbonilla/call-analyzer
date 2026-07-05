"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/auth";
import { useAuthToken } from "@/lib/useAuthToken";

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const token = useAuthToken();

  if (pathname === "/login" || !token) return null;

  function handleLogout() {
    clearToken();
    router.replace("/login");
  }

  return (
    <nav className="flex items-center gap-6 border-b border-black/10 px-6 py-4 dark:border-white/10">
      <Link
        href="/upload-files"
        className="text-sm font-medium text-zinc-700 hover:text-zinc-950 dark:text-zinc-300 dark:hover:text-zinc-50"
      >
        Upload
      </Link>
      <Link
        href="/list-calls"
        className="text-sm font-medium text-zinc-700 hover:text-zinc-950 dark:text-zinc-300 dark:hover:text-zinc-50"
      >
        Calls
      </Link>
      <button
        onClick={handleLogout}
        className="ml-auto text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
      >
        Log out
      </button>
    </nav>
  );
}
