"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, AlertCircle } from "lucide-react";
import { Message, ChatResponse } from "@/app/types";
import PlayerCard from "./PlayerCard";

const API_BASE = "";

export default function Chat() {
  const [messages, setMessages]   = useState<Message[]>([]);
  const [input, setInput]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [apiCalls, setApiCalls]   = useState<number | null>(null);
  const bottomRef                 = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage() {
    const playerName = input.trim();
    if (!playerName || loading) return;

    setInput("");
    setError(null);

    // Add user message
    const userMsg: Message = { role: "user", content: playerName };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    // Build history for multi-turn (text only — no playerData)
    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_name: playerName,
          conversation_history: history,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? "Something went wrong.");
      }

      const data: ChatResponse = await res.json();
      setApiCalls(data.api_calls_today);

      const assistantMsg: Message = {
        role: "assistant",
        content: data.reply,
        playerData: data.player_data,
      };
      setMessages((prev) => [...prev, assistantMsg]);

    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error.";
      setError(msg);
      // Remove the user message if request failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="flex flex-col h-full">

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 gap-3">
            <div className="text-5xl">⚽</div>
            <p className="text-lg font-medium text-gray-600">PL Stats AI</p>
            <p className="text-sm max-w-xs">
              Type a Premier League player's name to get their stats and an AI analysis.
            </p>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {["Bruno Fernandes", "Erling Haaland", "Bukayo Saka", "Virgil van Dijk"].map((name) => (
                <button
                  key={name}
                  onClick={() => { setInput(name); }}
                  className="px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 text-sm rounded-full border border-purple-200 transition-colors"
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "user" ? (
              <div className="bg-purple-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-xs text-sm">
                {msg.content}
              </div>
            ) : (
              <div className="flex flex-col gap-3 max-w-xl w-full">
                {/* Player card */}
                {msg.playerData && <PlayerCard player={msg.playerData} />}
                {/* AI analysis bubble */}
                <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-2xl rounded-tl-sm text-sm leading-relaxed">
                    {msg.content.split('\n').map((line, i) => {
                        const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                        return (
                            <p
                                key={i}
                                className={line.startsWith('#') ? 'font-bold text-base mb-1' : 'mb-1'}
                                dangerouslySetInnerHTML={{ __html: formatted.replace(/^#+\s/, '') }}
                            />
                        );
                    })}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-2 text-gray-500 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Looking up player stats...
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-xl flex items-center gap-2 text-sm max-w-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-200 px-4 py-3 bg-white">
        {apiCalls !== null && (
          <p className="text-xs text-gray-400 mb-2 text-right">
            API calls today: {apiCalls}/90
          </p>
        )}
        <div className="flex gap-2 items-end">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a player name, e.g. Bruno Fernandes..."
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50"          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed text-white p-2.5 rounded-xl transition-colors"
          >
            {loading
              ? <Loader2 className="w-5 h-5 animate-spin" />
              : <Send className="w-5 h-5" />
            }
          </button>
        </div>
      </div>

    </div>
  );
}