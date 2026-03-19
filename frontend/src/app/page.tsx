import AppShell from "@/components/layout/AppShell";
import HeroInput from "@/components/home/HeroInput";
import FeatureCards from "@/components/home/FeatureCards";

export default function HomePage() {
  return (
    <AppShell>
      <div className="max-w-4xl mx-auto w-full px-6 py-12 flex flex-col items-center gap-16">
        {/* Hero */}
        <div className="w-full flex flex-col items-center text-center gap-4 animate-fade-up opacity-0 [animation-fill-mode:forwards]">
          <div className="inline-flex items-center gap-2 bg-primary/8 border border-primary/15 text-primary text-xs font-semibold px-3 py-1.5 rounded-full">
            <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
            Powered by Hybrid RAG + Multi-Agent AI
          </div>
          <h1
            className="text-4xl sm:text-5xl text-slate-800 leading-tight tracking-tight max-w-2xl"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Dump Here, Sort Later
          </h1>
          <p className="text-slate-400 text-base max-w-lg leading-relaxed">
            Dumpling ingests anything from links, PDFs, images, plain text and automatically organises and connects your knowledge using AI.
          </p>
        </div>

        {/* Central input */}
        <div className="w-full animate-fade-up opacity-0 [animation-fill-mode:forwards] stagger-2">
          <HeroInput />
        </div>

        {/* Feature cards */}
        <div className="w-full pb-16">
          <FeatureCards />
        </div>
      </div>
    </AppShell>
  );
}
