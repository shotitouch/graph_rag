import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Shotitouch | Agentic PDF RAG",
  description: "Next-generation document intelligence powered by LangGraph & FastAPI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased 
        bg-white dark:bg-[#09090b] text-zinc-900 dark:text-zinc-100 transition-colors duration-300`}
      >
        {/* Subtle Background Pattern */}
        <div className="fixed inset-0 z-[-1] opacity-[0.03] dark:opacity-[0.05] pointer-events-none">
          <div className="absolute inset-0 bg-[grid-row-40px] [mask-image:linear-gradient(to_bottom,white,transparent)]" 
               style={{ backgroundImage: 'radial-gradient(circle, currentColor 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
        </div>

        {/* We remove the max-w-3xl from here because the Home page 
           needs to be full-width for the Hero section. 
           We will apply constraints inside individual pages instead.
        */}
        <main className="relative min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}