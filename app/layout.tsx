import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Toaster } from "sonner";
import { AuroraBackground } from "@/components/ui/aurora-background";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EasyLLM - Autonomous Neural Decision & Training Engine",
  description: "Autonomous end-to-end platform for RAG knowledge retrieval, QLoRA fine-tuning, and hybrid AI systems.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-[#fbfbfc] text-slate-900 antialiased selection:bg-blue-500/20 selection:text-blue-700`}>
        <AuroraBackground className="min-h-screen">
          <Navbar />
          <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {children}
          </main>
        </AuroraBackground>
        <Toaster position="bottom-right" richColors />
      </body>
    </html>
  );
}
