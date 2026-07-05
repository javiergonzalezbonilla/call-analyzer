import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginPage from "./page";
import { ApiError, login } from "@/lib/api";
import { setToken } from "@/lib/auth";

const pushMock = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

jest.mock("@/lib/api", () => ({
  ...jest.requireActual("@/lib/api"),
  login: jest.fn(),
}));

jest.mock("@/lib/auth", () => ({
  setToken: jest.fn(),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the login form", () => {
    render(<LoginPage />);

    expect(screen.getByRole("heading", { name: "Log in" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log in" })).toBeInTheDocument();
  });

  it("logs in and redirects to /upload-files on success", async () => {
    const user = userEvent.setup();
    (login as jest.Mock).mockResolvedValue({
      token: "abc123",
      user: { id: 1, email: "a@b.com", role: "user", is_active: true },
    });

    render(<LoginPage />);

    await user.type(screen.getByLabelText("Email"), "a@b.com");
    await user.type(screen.getByLabelText("Password"), "password");
    await user.click(screen.getByRole("button", { name: "Log in" }));

    await waitFor(() => expect(login).toHaveBeenCalledWith("a@b.com", "password"));
    expect(setToken).toHaveBeenCalledWith("abc123");
    expect(pushMock).toHaveBeenCalledWith("/upload-files");
  });

  it("shows an error message when login fails", async () => {
    const user = userEvent.setup();
    (login as jest.Mock).mockRejectedValue(new ApiError(401, "Invalid credentials"));

    render(<LoginPage />);

    await user.type(screen.getByLabelText("Email"), "a@b.com");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Log in" }));

    expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
    expect(setToken).not.toHaveBeenCalled();
    expect(pushMock).not.toHaveBeenCalled();
  });
});
