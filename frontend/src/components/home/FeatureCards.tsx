const features = [
  {
    icon: "auto_fix_high",
    title: "Ingestion Agent",
    desc: "Drop a URL, paste text, upload a file or image. Dumpling scrapes, parses, and chunks it into searchable knowledge automatically.",
    gradient: "from-violet-50 to-purple-50",
  },
  {
    icon: "image_search",
    title: "Categorisation Agent",
    desc: "Every piece of content is intelligently sorted into the right folder by an AI agent that reads meaning, not just filenames.",
    gradient: "from-amber-50 to-orange-50",
  },
  {
    icon: "shield_lock",
    title: "Critic Agent",
    desc: "A built-in critic agent checks every folder assignment and every answer for accuracy before it reaches you. So what you get is verified, not just generated.",
    gradient: "from-sky-50 to-blue-50",
  },
  {
    icon: "hub",
    title: "Semantic Search",
    desc: "Ask a question in plain English. Dumpling searches across all your folders using hybrid RAG (keyword + semantic) and returns the most relevant answer with sources cited.",
    gradient: "from-emerald-50 to-teal-50",
  }
];

export default function FeatureCards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 w-full">
      {features.map((f, i) => (
        <div
          key={f.title}
          className={`group bg-gradient-to-br ${f.gradient} border border-warm-400/50 rounded-2xl p-6 hover:border-primary/20 hover:shadow-warm-sm transition-all duration-200 animate-fade-up opacity-0 [animation-fill-mode:forwards]`}
          style={{ animationDelay: `${200 + i * 60}ms` }}
        >
          <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary mb-4 shadow-warm-sm group-hover:shadow-warm-md group-hover:scale-110 transition-all duration-200">
            <span className="material-symbols-outlined text-[20px]">{f.icon}</span>
          </div>
          <h3
            className="text-base font-normal text-slate-800 mb-1.5"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {f.title}
          </h3>
          <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
        </div>
      ))}
    </div>
  );
}
