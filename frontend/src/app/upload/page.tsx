"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ingestPDF } from "@/lib/api";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileText,
  Info,
  Loader2,
  MessageSquare,
  Upload,
} from "lucide-react";

function getProgressMessage(mode: "fast" | "full", progress: number) {
  if (mode === "fast") {
    if (progress < 20) return "Uploading filing and preparing text extraction...";
    if (progress < 45) return "Extracting filing text and cover-page metadata...";
    if (progress < 75) return "Chunking narrative sections for retrieval...";
    return "Indexing filing chunks for grounded analysis...";
  }

  if (progress < 15) return "Uploading filing and preparing multimodal parsing...";
  if (progress < 35) return "Parsing document layout, tables, and narrative blocks...";
  if (progress < 65) return "Extracting financial tables and chart context...";
  if (progress < 85) return "Summarizing multimodal elements for retrieval...";
  return "Indexing filing content for grounded analysis...";
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<"fast" | "full">("fast");
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [progress, setProgress] = useState(0);

  const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB Limit for 512MB RAM stability

  useEffect(() => {
    if (status !== "uploading") {
      return;
    }

    const ceiling = mode === "fast" ? 92 : 88;
    const interval = window.setInterval(() => {
      setProgress((current) => {
        if (current >= ceiling) {
          return current;
        }

        const increment =
          current < 20 ? 8 :
          current < 45 ? 6 :
          current < 70 ? 4 :
          current < 82 ? 2 :
          1;

        return Math.min(current + increment, ceiling);
      });
    }, mode === "fast" ? 700 : 1100);

    return () => window.clearInterval(interval);
  }, [mode, status]);

  async function handleUpload() {
    if (!file) return;

    // CLIENT-SIDE GUARD: Prevent OOM on the server
    if (file.size > MAX_FILE_SIZE) {
      setStatus("error");
      setMessage("File is too large for the preview server. Please upload a PDF under 2MB.");
      return;
    }

    setStatus("uploading");
    setProgress(6);
    setMessage("");

    try {
      const result = await ingestPDF(file, mode);
      setProgress(100);
      setStatus("success");
      setMessage(
        `Document successfully indexed${result?.ticker && result.ticker !== "UNKNOWN" ? ` for ${result.ticker}` : ""}. You can now chat with it.`
      );
    } catch (err) {
      setProgress(0);
      setStatus("error");
      console.error(err);
      setMessage(
        err instanceof Error ? err.message : "Document ingestion failed."
      );
    }
  }

  const displayMessage =
    status === "uploading"
      ? getProgressMessage(mode, progress)
      : message;

  return (
    <div className="min-h-screen max-w-4xl mx-auto px-4 py-12 flex flex-col">
      <header className="mb-10 flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <Link href="/" className="flex items-center gap-2 text-zinc-500 hover:text-blue-500 transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" /> <span>Back to Dashboard</span>
          </Link>
          <h1 className="text-4xl font-extrabold text-gradient">Filing Ingestion</h1>
          <p className="text-zinc-500 mt-2">Upload a 10-Q or related financial filing to prepare it for grounded analysis.</p>
        </div>
        <Link href="/chat" className="flex items-center gap-2 px-5 py-2.5 bg-zinc-100 dark:bg-zinc-800 rounded-xl text-sm font-semibold hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-all border border-zinc-200 dark:border-zinc-700">
          <MessageSquare className="w-4 h-4 text-blue-500" /> Open Analysis
        </Link>
      </header>

      <div className="mb-8 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex gap-3 items-center text-amber-700 dark:text-amber-500 text-sm">
        <Info className="w-5 h-5 flex-shrink-0" />
        <p>
          <strong>Processing Note:</strong> Financial filing ingestion can be resource-intensive. For local testing, use a manageable PDF size while parsing, indexing, and multimodal extraction are being tuned.
        </p>
      </div>

      <div className={`glass-card rounded-3xl p-10 flex flex-col items-center border-2 border-dashed transition-all ${
        file ? "border-blue-500/50 bg-blue-500/5" : "border-zinc-200 dark:border-zinc-800"
      }`}>
        <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center text-blue-600 mb-6">
          <Upload className="w-8 h-8" />
        </div>

        <label className="cursor-pointer text-center">
          <span className="block text-lg font-semibold">
            {file ? file.name : "Select a filing PDF"}
          </span>
          <span className="text-sm text-zinc-500 block mt-1">
            Max 2MB &bull; Text-based PDF only
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
              setProgress(0);
            }}
          />
        </label>

        <div className="mt-8 grid w-full max-w-2xl grid-cols-1 gap-4 md:grid-cols-2">
          <button
            type="button"
            onClick={() => setMode("fast")}
            className={`rounded-2xl border p-5 text-left transition-all ${
              mode === "fast"
                ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                : "border-zinc-200 bg-white/40 hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900/40 dark:hover:border-zinc-700"
            }`}
          >
            <div className="text-sm font-bold uppercase tracking-wider text-blue-500">Fast Analysis</div>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">
              Best for quick indexing and grounded Q&amp;A. Ingests filing text and metadata with lower processing time.
            </p>
          </button>
          <button
            type="button"
            onClick={() => setMode("full")}
            className={`rounded-2xl border p-5 text-left transition-all ${
              mode === "full"
                ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                : "border-zinc-200 bg-white/40 hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900/40 dark:hover:border-zinc-700"
            }`}
          >
            <div className="text-sm font-bold uppercase tracking-wider text-blue-500">Full Analysis</div>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">
              Adds deeper table and chart extraction for richer multimodal retrieval, with longer processing time and higher compute cost.
            </p>
          </button>
        </div>

        {file && status === "idle" && (
          <button
            onClick={handleUpload}
            className="mt-8 px-10 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/25"
          >
            Start Filing Ingestion
          </button>
        )}
      </div>

      {status !== "idle" && (
        <div className={`mt-8 p-6 rounded-2xl flex gap-4 items-start animate-in fade-in slide-in-from-top-4 ${
          status === "uploading" ? "bg-zinc-100 dark:bg-zinc-900" :
            status === "success" ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" :
            "bg-red-500/10 text-red-600 border border-red-500/20"
        }`}>
          {status === "uploading" && <Loader2 className="w-5 h-5 animate-spin mt-0.5" />}
          {status === "success" && <CheckCircle2 className="w-5 h-5 mt-0.5" />}
          {status === "error" && <AlertCircle className="w-5 h-5 mt-0.5" />}

          <div className="w-full">
            <h3 className="font-bold text-sm uppercase tracking-wider">
              {status === "uploading" ? "System Processing" : status === "success" ? "Upload Complete" : "Error"}
            </h3>
            <p className="text-sm opacity-80 mt-1">{displayMessage}</p>
            {status === "uploading" && (
              <div className="mt-4 w-full max-w-xl">
                <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500 dark:text-zinc-400">
                  <span>{mode === "fast" ? "Fast Mode" : "Full Mode"}</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-blue-600 transition-[width] duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {status === "success" && (
        <Link href="/chat" className="mt-6 flex items-center justify-center gap-2 p-4 bg-zinc-900 dark:bg-white dark:text-black text-white rounded-2xl font-bold hover:scale-[1.01] transition-transform shadow-xl">
          <FileText className="w-4 h-4" /> Open Filing Analysis
        </Link>
      )}
    </div>
  );
}
