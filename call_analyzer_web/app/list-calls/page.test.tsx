import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import ListCallsPage from "./page";
import { ApiError, listCalls, type Call } from "@/lib/api";

jest.mock("@/lib/useRequireAuth", () => ({
  useRequireAuth: () => true,
}));

jest.mock("@/lib/api", () => ({
  ...jest.requireActual("@/lib/api"),
  listCalls: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({
    href,
    children,
  }: {
    href: string;
    children: ReactNode;
  }) {
    return <a href={href}>{children}</a>;
  };
});

function makeCall(overrides: Partial<Call> = {}): Call {
  return {
    call_id: "call-1",
    status: "completed",
    uploaded_audio_files: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

describe("ListCallsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the page heading", async () => {
    (listCalls as jest.Mock).mockResolvedValue([]);
    render(<ListCallsPage />);

    expect(screen.getByRole("heading", { name: "Calls" })).toBeInTheDocument();
    await screen.findByText("No calls uploaded yet.");
  });

  it("lists calls returned by the API as links to their details page", async () => {
    (listCalls as jest.Mock).mockResolvedValue([
      makeCall({ call_id: "call-1", status: "completed" }),
      makeCall({ call_id: "call-2", status: "pending" }),
    ]);

    render(<ListCallsPage />);

    const link1 = await screen.findByRole("link", { name: "call-1 — completed" });
    expect(link1).toHaveAttribute("href", "/call-details/call-1");

    const link2 = screen.getByRole("link", { name: "call-2 — pending" });
    expect(link2).toHaveAttribute("href", "/call-details/call-2");
  });

  it("shows an empty state when there are no calls", async () => {
    (listCalls as jest.Mock).mockResolvedValue([]);

    render(<ListCallsPage />);

    expect(await screen.findByText("No calls uploaded yet.")).toBeInTheDocument();
  });

  it("shows an error message when the API call fails", async () => {
    (listCalls as jest.Mock).mockRejectedValue(new ApiError(500, "Server error"));

    render(<ListCallsPage />);

    expect(
      await screen.findByText(/Server error — this endpoint may not be implemented/)
    ).toBeInTheDocument();
  });
});
