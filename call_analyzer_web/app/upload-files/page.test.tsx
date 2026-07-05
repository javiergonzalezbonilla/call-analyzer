import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import UploadFilesPage from "./page";
import { ApiError, uploadAudioFile, type Call } from "@/lib/api";

jest.mock("@/lib/useRequireAuth", () => ({
  useRequireAuth: () => true,
}));

jest.mock("@/lib/api", () => ({
  ...jest.requireActual("@/lib/api"),
  uploadAudioFile: jest.fn(),
}));

function makeCall(): Call {
  return {
    call_id: "call-1",
    status: "pending",
    uploaded_audio_files: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  };
}

describe("UploadFilesPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the upload dropzone", () => {
    render(<UploadFilesPage />);

    expect(
      screen.getByRole("heading", { name: "Upload call recordings" })
    ).toBeInTheDocument();
    expect(
      screen.getByText("Drag and drop audio files here, or click to browse")
    ).toBeInTheDocument();
  });

  it("uploads a selected file and shows success status", async () => {
    const user = userEvent.setup();
    (uploadAudioFile as jest.Mock).mockResolvedValue(makeCall());

    render(<UploadFilesPage />);

    const file = new File(["audio-bytes"], "call.mp3", { type: "audio/mpeg" });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, file);

    expect(await screen.findByText("call.mp3")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("Uploaded")).toBeInTheDocument());
    expect(uploadAudioFile).toHaveBeenCalledWith(file);
  });

  it("shows an error status when the upload fails", async () => {
    const user = userEvent.setup();
    (uploadAudioFile as jest.Mock).mockRejectedValue(new ApiError(400, "Bad file"));

    render(<UploadFilesPage />);

    const file = new File(["audio-bytes"], "call.mp3", { type: "audio/mpeg" });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, file);

    expect(await screen.findByText("Bad file")).toBeInTheDocument();
  });
});
