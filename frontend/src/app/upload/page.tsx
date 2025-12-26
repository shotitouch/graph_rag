"use client";

import Link from 'next/link';
import { useState } from "react";
import { ingestPDF } from "@/lib/api";
import { ArrowLeft, Upload, FileText, CheckCircle2, AlertCircle, Loader2, MessageSquare } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleUpload() {
    if (!file) return;

    setStatus("uploading");
    setMessage("Processing document chunks and generating embeddings...");

    try {
      const res = await ingestPDF(file);
      setStatus("success");
      setMessage("Document successfully indexed in ChromaDB.");
    } catch (err) {
      setStatus("error");
      setMessage("Failed to process PDF. Please check the backend connection.");
    }
  }

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-4 py-12 flex flex-col">
      {/* Header with Circular Navigation */}
      <header className="mb-10 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <Link
            href="/"
            className="flex items-center gap-2 text-zinc-500 hover:text-blue-500 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" /> <span>Back to Dashboard</span>
          </Link>
          <h1 className="text-4xl font-extrabold text-gradient">Knowledge Ingestion</h1>
          <p className="text-zinc-500 mt-2">Upload your PDF to expand the assistant's context.</p>
        </div>

        <Link
          href="/chat"
          className="flex items-center gap-2 px-5 py-2.5 bg-zinc-100 dark:bg-zinc-800 rounded-xl text-sm font-semibold hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-all border border-zinc-200 dark:border-zinc-700"
        >
          <MessageSquare className="w-4 h-4 text-blue-500" /> Resume Chat
        </Link>
      </header>

      {/* Upload Zone */}
      <div className={`glass-card rounded-3xl p-10 flex flex-col items-center border-2 border-dashed transition-all
        ${file ? "border-blue-500/50 bg-blue-500/5" : "border-zinc-200 dark:border-zinc-800"}`}>
        
        <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-600 mb-6">
          <Upload className="w-8 h-8" />
        </div>

        <label className="cursor-pointer text-center">
          <span className="block text-lg font-semibold">
            {file ? file.name : "Select a PDF document"}
          </span>
          <span className="text-sm text-zinc-500 block mt-1">
            Accepts PDF up to 10MB
          </span>
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setStatus("idle");
                setMessage("");
            }}
          />
        </label>

        {file && status === "idle" && (
          <button
            onClick={handleUpload}
            className="mt-8 px-10 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/25"
          >
            Start Ingestion
          </button>
        )}
      </div>

      {/* Feedback & Navigation Call to Action */}
      {status !== "idle" && (
        <div className={`mt-8 p-6 rounded-2xl flex gap-4 items-start animate-in fade-in slide-in-from-top-4 
          ${status === "uploading" ? "bg-zinc-100 dark:bg-zinc-900" : 
            status === "success" ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" : 
            "bg-red-500/10 text-red-600 border border-red-500/20"}`}
        >
          {status === "uploading" && <Loader2 className="w-5 h-5 animate-spin mt-0.5" />}
          {status === "success" && <CheckCircle2 className="w-5 h-5 mt-0.5" />}
          {status === "error" && <AlertCircle className="w-5 h-5 mt-0.5" />}
          
          <div>
            <h3 className="font-bold text-sm uppercase tracking-wider">
              {status === "uploading" ? "System Processing" : status === "success" ? "Upload Complete" : "Error"}
            </h3>
            <p className="text-sm opacity-80 mt-1">{message}</p>
          </div>
        </div>
      )}

      {status === "success" && (
        <Link
          href="/chat"
          className="mt-6 flex items-center justify-center gap-2 p-4 bg-zinc-900 dark:bg-white dark:text-black text-white rounded-2xl font-bold hover:scale-[1.01] transition-transform shadow-xl"
        >
          <FileText className="w-4 h-4" /> Start Chatting with PDF
        </Link>
      )}
    </div>
  );
}