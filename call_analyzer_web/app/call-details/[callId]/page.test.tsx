import { render, screen } from "@testing-library/react";
import CallDetailsPage from "./page";
import { ApiError, getCall, type Call } from "@/lib/api";

jest.mock("@/lib/useRequireAuth", () => ({
  useRequireAuth: () => true,
}));

jest.mock("next/navigation", () => ({
  useParams: () => ({ callId: "call-1" }),
}));

jest.mock("@/lib/api", () => ({
  ...jest.requireActual("@/lib/api"),
  getCall: jest.fn(),
}));

function makeCall(overrides: Partial<Call> = {}): Call {
  return {
    call_id: "call-1",
    status: "completed",
    uploaded_audio_files: [
      { id: 1, audio: "/media/call-1.mp3", size: 100, type: "audio/mpeg", path: "call-1.mp3", metadata: {}, created_at: "2026-01-01T00:00:00Z" },
    ],
    summary: "Customer asked about billing.",
    transcript: "Hello, I have a question about my bill.",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

describe("CallDetailsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the call id in the heading", async () => {
    (getCall as jest.Mock).mockResolvedValue(makeCall());

    render(<CallDetailsPage />);

    expect(screen.getByRole("heading", { name: "Call call-1" })).toBeInTheDocument();
    expect(getCall).toHaveBeenCalledWith("call-1");
    await screen.findByText("completed");
  });

  it("displays the call's status, summary, transcript, and audio files", async () => {
    (getCall as jest.Mock).mockResolvedValue(makeCall());

    render(<CallDetailsPage />);

    expect(await screen.findByText("completed")).toBeInTheDocument();
    expect(screen.getByText("Customer asked about billing.")).toBeInTheDocument();
    expect(screen.getByText("Hello, I have a question about my bill.")).toBeInTheDocument();

    const downloadLink = screen.getByRole("link", { name: "call-1.mp3" });
    expect(downloadLink).toHaveAttribute("href", "/media/call-1.mp3");
  });

  it("shows an error message when the call fails to load", async () => {
    (getCall as jest.Mock).mockRejectedValue(new ApiError(404, "Not found"));

    render(<CallDetailsPage />);

    expect(
      await screen.findByText(/Not found — this endpoint may not be implemented/)
    ).toBeInTheDocument();
  });
});
