"use client";

const sources = [
  { id: 1, icon: "picture_as_pdf", iconColor: "text-red-500",  name: "Flight Booking.pdf", date: "14:30, 12-Oct-2023", active: false },
  { id: 2, icon: "description",    iconColor: "text-blue-500", name: "Itinerary.docx",      date: "09:15, 14-Oct-2023", active: true  },
  { id: 3, icon: "link",           iconColor: "text-green-500",name: "Hotel Pin.url",        date: "18:45, 12-Oct-2023", active: false },
];

export default function Sidepanel() {
  return (
    <section className="w-64 border-r border-slate-200 dark:border-slate-800 flex flex-col bg-slate-50/50 dark:bg-slate-900/30 shrink-0">
      <div className="p-4 flex items-center justify-between border-b border-slate-200 dark:border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Sources</h3>
        <button className="size-6 flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-800 rounded transition-colors">
          <span className="material-symbols-outlined text-lg text-slate-500">add</span>
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        {sources.map((source) => (
          <div
            key={source.id}
            className={`flex items-start gap-3 p-2 rounded-lg bg-white dark:bg-slate-800/50 border cursor-pointer transition-colors
              ${source.active
                ? "border-primary/50"
                : "border-slate-200 dark:border-slate-800 hover:border-primary/50"
              }`}
          >
            <span className={`material-symbols-outlined text-xl mt-0.5 ${source.iconColor}`}>
              {source.icon}
            </span>
            <div className="flex-1 overflow-hidden">
              <p className="text-xs font-medium truncate">{source.name}</p>
              <p className="text-[10px] text-slate-400 mt-0.5">{source.date}</p>
            </div>
            <button className="text-slate-400 hover:text-slate-100 transition-colors">
              <span className="material-symbols-outlined text-[18px]">more_vert</span>
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}