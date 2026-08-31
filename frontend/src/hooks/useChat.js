import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/chat";

export function useChat(sessionId, userId = "demo-user") {
  const socketRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [agentStatus, setAgentStatus] = useState("");
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState("");

  useEffect(() => {
    const socket = new WebSocket(`${WS_URL}/${sessionId}`);
    socketRef.current = socket;

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);
    socket.onerror = () => {
      setIsConnected(false);
      setAgentStatus("Connection unavailable");
    };
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === "status" || payload.type === "tool") {
        setAgentStatus(payload.data);
      } else if (payload.type === "token") {
        setCurrentStreamingMessage((current) => current + payload.data);
      } else if (payload.type === "complete") {
        setMessages((current) => [
          ...current,
          { role: "assistant", content: payload.data },
        ]);
        setCurrentStreamingMessage("");
        setAgentStatus("");
      } else if (payload.type === "error") {
        setAgentStatus(payload.data);
      }
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    (content) => {
      const query = content.trim();
      if (!query || socketRef.current?.readyState !== WebSocket.OPEN) return false;

      setMessages((current) => [...current, { role: "user", content: query }]);
      setCurrentStreamingMessage("");
      setAgentStatus("Planning steps...");
      socketRef.current.send(JSON.stringify({ user_id: userId, query }));
      return true;
    },
    [userId],
  );

  return {
    messages,
    isConnected,
    agentStatus,
    currentStreamingMessage,
    sendMessage,
  };
}
