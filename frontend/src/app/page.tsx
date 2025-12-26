import Link from "next/link";
import { ArrowRight, FileText, MessageSquare, Database, Cpu, Layout, User } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-[#09090b] text-zinc-900 dark:text-zinc-100 transition-colors duration-300">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-6 text-center overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(59,130,246,0.1),transparent)]" />
        <div className="relative max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-zinc-900 to-zinc-500 dark:from-white dark:to-zinc-500">
            PDF RAG Assistant
          </h1>
          <p className="text-lg md:text-xl text-zinc-600 dark:text-zinc-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            An advanced Agentic RAG pipeline designed to bridge the gap between static documents and intelligent conversation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/upload"
              className="flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-full transition-all hover:scale-105 shadow-lg shadow-blue-500/25"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/chat"
              className="flex items-center justify-center gap-2 px-8 py-4 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 font-semibold rounded-full transition-all"
            >
              Live Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Bento Grid Features Section */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 auto-rows-[200px]">
          {/* Main Core Skill */}
          {/* Increased width and height using col-span and row-span */}
          <div className="md:col-span-2 md:row-span-2 rounded-3xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 p-8 transition-all hover:border-blue-500/50 bento-hover flex flex-col justify-between">
            <div>
              <div className="mb-6 w-14 h-14 rounded-2xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600">
                <Cpu className="w-8 h-8" />
              </div>
              
              <h3 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">
                Agentic Orchestration
              </h3>
              
              <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed mb-6">
                Leveraging 5.5 years of backend expertise  to move beyond simple chains. 
                I implement <strong>cyclic cognitive architectures</strong> using LangGraph for 
                self-correcting RAG loops and stateful multi-agent coordination.
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-white/50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700">
                  <span className="block text-xs font-bold uppercase tracking-wider text-indigo-500 mb-1">Logic</span>
                  <span className="text-xs text-zinc-600 dark:text-zinc-300">Self-Correcting Loops</span>
                </div>
                <div className="p-4 rounded-2xl bg-white/50 dark:bg-zinc-800/50 border border-zinc-100 dark:border-zinc-700">
                  <span className="block text-xs font-bold uppercase tracking-wider text-indigo-500 mb-1">Routing</span>
                  <span className="text-xs text-zinc-600 dark:text-zinc-300">Intent-Driven Paths</span>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">Powered by LangGraph & FastAPI</span>
              <div className="flex -space-x-2">
                {/* Visual indicator of "Agentic" complexity */}
                <div className="w-6 h-6 rounded-full bg-blue-500 border-2 border-white dark:border-zinc-900" />
                <div className="w-6 h-6 rounded-full bg-indigo-500 border-2 border-white dark:border-zinc-900" />
                <div className="w-6 h-6 rounded-full bg-purple-500 border-2 border-white dark:border-zinc-900" />
              </div>
            </div>
          </div>

          {/* About Me */}
          <div className="md:row-span-2 rounded-3xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 p-8 transition-all hover:border-blue-500/50">
            <div className="mb-4 w-12 h-12 rounded-2xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
              <User className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">Shotitouch T.</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
              <strong>ML Graduate Student at Stevens (GPA 4.0)</strong> and former <strong>Full-Stack Co-founder</strong> with 5.5+ years of experience[cite: 4, 5, 32]. 
              I specialize in architecting <strong>agentic GenAI systems</strong> and <strong>adversarial ML</strong>, 
              bridging the gap between scalable enterprise backends and state-of-the-art AI research.
            </p>
          </div>

          {/* Database */}
          <div className="rounded-3xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 p-6 flex flex-col justify-center transition-all hover:border-blue-500/50">
            <div className="flex items-center gap-3 mb-2 font-bold">
              <Database className="w-5 h-5 text-blue-500" /> ChromaDB
            </div>
            <p className="text-xs text-zinc-500">Vector storage for high-performance semantic retrieval.</p>
          </div>

          {/* FastAPI */}
          <div className="rounded-3xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 p-6 flex flex-col justify-center transition-all hover:border-blue-500/50">
            <div className="flex items-center gap-3 mb-2 font-bold">
              <FileText className="w-5 h-5 text-emerald-500" /> Next.js + FastAPI
            </div>
            <p className="text-xs text-zinc-500">A seamless bridge between high-speed AI logic and reactive UI.</p>
          </div>
        </div>
      </section>

      {/* Footer / Tech Stack */}
      <footer className="py-12 border-t border-zinc-200 dark:border-zinc-800 text-center">
        <p className="text-zinc-500 dark:text-zinc-500 text-sm font-medium uppercase tracking-widest">
          Engineered with precision
        </p>
        <div className="mt-4 flex flex-wrap justify-center gap-6 opacity-60 grayscale hover:grayscale-0 transition-all">
          <span>LangChain</span>
          <span>FastAPI</span>
          <span>Next.js</span>
          <span>TailwindCSS</span>
        </div>
      </footer>
    </div>
  );
}