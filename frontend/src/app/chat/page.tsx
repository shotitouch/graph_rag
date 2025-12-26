"use client";

import Link from 'next/link';
import { useState, useEffect, useRef } from "react";
import { askQuestion } from "@/lib/api";
import { ArrowLeft, Send, Bot, User, Sparkles, Upload } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [sessionId] = useState("session_" + Math.random().toString(36).substring(7));
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await askQuestion(sessionId, input);
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: res.answer,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat Error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto px-4 py-6">
      {/* Header with Circular Navigation */}
      <header className="flex items-center justify-between mb-6">
        <div className="flex gap-4 items-center">
          <Link
            href="/"
            className="flex items-center gap-2 text-zinc-500 hover:text-blue-500 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> <span className="hidden sm:inline">Dashboard</span>
          </Link>
          
          <Link
            href="/upload"
            className="flex items-center gap-2 text-xs font-medium text-zinc-400 hover:text-blue-500 border border-zinc-200 dark:border-zinc-800 px-3 py-1.5 rounded-full transition-all hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <Upload className="w-3 h-3" /> New Document
          </Link>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 text-blue-500 rounded-full text-xs font-medium border border-blue-500/20">
          <Sparkles className="w-3 h-3" /> Agentic RAG Active
        </div>
      </header>

      {/* Chat Area */}
      <div 
        ref={scrollRef}
        className="flex-1 glass-card rounded-3xl overflow-y-auto p-6 space-y-6 mb-4"
      >
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
            <Bot className="w-16 h-16 mb-4 text-blue-500" />
            <h2 className="text-xl font-bold">Document Brain Active</h2>
            <p className="max-w-xs mx-auto mt-2 text-sm">
              I am ready to answer questions based on your uploaded context. What would you like to know?
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <div 
            key={i} 
            className={`flex gap-4 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm
              ${m.role === "user" ? "bg-zinc-800 text-white" : "bg-blue-600 text-white"}`}
            >
              {m.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
            </div>

            <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm
              ${m.role === "user" 
                ? "bg-blue-600 text-white rounded-tr-none" 
                : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-tl-none"}`}
            >
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-4 animate-pulse">
            <div className="w-9 h-9 rounded-xl bg-zinc-200 dark:bg-zinc-800" />
            <div className="h-12 w-32 bg-zinc-100 dark:bg-zinc-800 rounded-2xl rounded-tl-none" />
          </div>
        )}
      </div>

      {/* Input Section */}
      <div className="relative group">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 
                     p-5 pr-16 rounded-2xl shadow-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/40 
                     transition-all text-sm group-hover:border-zinc-300 dark:group-hover:border-zinc-700"
          placeholder="Ask a question about the document..."
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-2.5 bg-blue-600 text-white rounded-xl 
                     disabled:opacity-40 hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}