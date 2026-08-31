import { render, screen } from "@testing-library/react";
import { ChatMessage } from "../components/ChatMessage";
import App from "../App";
import { useChat } from "../hooks/useChat";

jest.mock("react-markdown", () => ({
  __esModule: true,
  default: ({ children, components }) => components.p({ children }),
}));

jest.mock("../hooks/useChat", () => ({
  useChat: jest.fn(),
}));

describe("CogniFlow chat UI", () => {
  beforeEach(() => {
    useChat.mockReturnValue({
      messages: [],
      isConnected: true,
      agentStatus: "Executing Jira Search",
      currentStreamingMessage: "",
      sendMessage: jest.fn(),
    });
  });

  it("shows the live execution trace when an agent status arrives", () => {
    render(<App />);

    expect(screen.getByText("Execution trace")).toBeVisible();
    expect(screen.getByText("Executing Jira Search")).toBeVisible();
    expect(screen.getByText("Live")).toBeVisible();
  });

  it("renders citations as interactive badges in assistant markdown", () => {
    render(
      <ChatMessage
        message={{ role: "assistant", content: "The blocker is tracked in [Jira-402]." }}
      />,
    );

    const citation = screen.getByRole("button", { name: "Jira-402" });
    expect(citation).toBeVisible();
    expect(citation).toHaveAttribute("title", "Open source [Jira-402]");
  });
});
