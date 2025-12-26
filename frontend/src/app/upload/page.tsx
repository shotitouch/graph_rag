"use client";

import Link from 'next/link';
import { useState } from "react";
import { ingestPDF } from "@/lib/api";
import { ArrowLeft, Upload, FileText, CheckCircle2, AlertCircle, Loader2, MessageSquare, Info } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB Limit for 512MB RAM stability

  async function handleUpload() {
    if (!file) return;

    // CLIENT-SIDE GUARD: Prevent OOM on the server
    if (file.size > MAX_FILE_SIZE) {
      setStatus("error");
      setMessage("File is too large for the preview server. Please upload a PDF under 2MB.");
      return;
    }

    setStatus("uploading");
    setMessage("Processing document chunks and generating embeddings...");

    try {
      const res = await ingestPDF(file);
      setStatus("success");
      setMessage("Document successfully indexed. You can now chat with it.");
    } catch (err) {
      setStatus("error");
      setMessage("Server memory limit reached or connection lost. Try a smaller PDF.");
    }
  }

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-4 py-12 flex flex-col">
      <header className="mb-10 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <Link href="/" className="flex items-center gap-2 text-zinc-500 hover:text-blue-500 transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" /> <span>Back to Dashboard</span>
          </Link>
          <h1 className="text-4xl font-extrabold text-gradient">Knowledge Ingestion</h1>
          <p className="text-zinc-500 mt-2">Upload your PDF to expand the assistant's context.</p>
        </div>
        <Link href="/chat" className="flex items-center gap-2 px-5 py-2.5 bg-zinc-100 dark:bg-zinc-800 rounded-xl text-sm font-semibold hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-all border border-zinc-200 dark:border-zinc-700">
          <MessageSquare className="w-4 h-4 text-blue-500" /> Resume Chat
        </Link>
      </header>

      {/* Recruiter Notice / Memory Guard */}
      <div className="mb-8 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex gap-3 items-center text-amber-700 dark:text-amber-500 text-sm">
        <Info className="w-5 h-5 flex-shrink-0" />
        <p>
          <strong>Server Note:</strong> To maintain stability on free-tier RAM (512MB), uploads are restricted to <strong>text-based PDFs under 2MB</strong> (approx. 15-20 pages).
        </p>
      </div>

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
            Max 2MB • Text-based PDF only
          </span>
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => {
                const selectedFile = e.target.files?.[0] || null;
                setFile(selectedFile);
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
        <Link href="/chat" className="mt-6 flex items-center justify-center gap-2 p-4 bg-zinc-900 dark:bg-white dark:text-black text-white rounded-2xl font-bold hover:scale-[1.01] transition-transform shadow-xl">
          <FileText className="w-4 h-4" /> Start Chatting with PDF
        </Link>
      )}
    </div>
  );
}