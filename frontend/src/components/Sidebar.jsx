"use client";

import Image from 'next/image';
import logo from "../app/assets/logo.png";


const workspaces = [
  {
    id: "personal",
    label: "Personal",
    icon: "person",
    iconColor: "text-blue-500",
    folders: ["Tokyo trip", "Basketball team uniform idea"],
  },
  {
    id: "work",
    label: "Work",
    icon: "work",
    iconColor: "text-amber-500",
    folders: ["prompt notes", "interview tips", "industry trends"],
  },
];

export default function Sidebar() {
  return (
    <aside className="w-72 border-r border-slate-200 dark:border-slate-800 bg-background-light dark:bg-background-dark hidden lg:flex flex-col">
      <div className="p-6 flex flex-col h-full overflow-y-auto">

        {/* Logo */}
        <div className="flex items-center gap-3 mb-10 shrink-0">
          <div className="size-8 bg-primary rounded flex items-center justify-center text-white">
            <Image src={logo} alt="My Logo" width={64} height={64} />
          </div>
          <h2 className="font-bold text-xl">Clipra</h2>
        </div>

        <div className="flex flex-col gap-6 flex-1">

          {/* Nav Items */}
          <div className="flex flex-col gap-1">
            {/* <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary cursor-pointer hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined text-[20px]">schedule</span>
              <p className="text-sm font-medium">Recent History</p>
            </div> */}
            <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#8a5cf624] dark:hover:bg-slate-800 transition-colors cursor-pointer text-slate-600 dark:text-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-trash" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
              </svg>
              <p className="text-md font-medium">Trash</p>
            </div>
          </div>

          {/* Notebooks */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Notebooks
            </p>
            <div className="flex flex-col gap-4">
              {workspaces.map((ws) => (
                <div key={ws.id}>
                  <div className="flex items-center gap-2 px-3 py-1.5 text-slate-900 dark:text-slate-100">
                    {/* arrow down (collapse) */}
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-caret-down" viewBox="0 0 16 16">
                      <path d="M3.204 5h9.592L8 10.481zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659"/>
                    </svg>

                    {/* logo for the folder title */}
                    <span className={`material-symbols-outlined text-[18px] ${ws.iconColor}`}>
                      {ws.icon}
                    </span>
                    <p className="text-sm font-semibold">{ws.label}</p>
                  </div>
                  <div className="flex flex-col gap-0.5 ml-8 mt-1 border-l border-slate-200 dark:border-slate-800">
                    {ws.folders.map((folder) => (
                      <div
                        key={folder}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-r-lg hover:bg-[#8a5cf624] dark:hover:bg-slate-800 cursor-pointer text-slate-500 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[16px]">
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-journals" viewBox="0 0 16 16">
                            <path d="M5 0h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2 2 2 0 0 1-2 2H3a2 2 0 0 1-2-2h1a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1H1a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v9a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1H3a2 2 0 0 1 2-2"/>
                            <path d="M1 6v-.5a.5.5 0 0 1 1 0V6h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 3v-.5a.5.5 0 0 1 1 0V9h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm0 2.5v.5H.5a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1H2v-.5a.5.5 0 0 0-1 0"/>
                          </svg>
                        </span>
                        <p className="text-xs font-medium truncate">{folder}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* User Footer */}
        <div className="mt-auto flex items-center gap-3 pt-4 border-t border-slate-200 dark:border-slate-800 shrink-0">
          <div
            className="size-8 rounded-full bg-slate-300 dark:bg-slate-700 bg-cover shrink-0"
            style={{
              backgroundImage:
                "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDaPjB3Nw3iW78FTeeE0zr9My8CKka-P0_X35ThjaLTPmOjNa1VuUvqykJdOH-8IPysUqrRd581Z0edOiZSyKHT_UImtSsuIga0XzDbR92oqqzq7hB2pvEpL1BjgndmtmexWTfd1Oo-P9otiCiUTUFFco_1zk7TAZgxbSHZxwzsUq1NsooiXfhLuFg-1p-nyDeQa8B84WZgy2_36w2akHtAqZyhULYuOtQtnCOPnAeJjvb5DrWe5MJXO8TNkuZ_4QGas5Rqh8Xem4k')",
            }}
          />
          <div className="flex flex-col overflow-hidden">
            <p className="text-xs font-bold truncate">Alex Johnson</p>
            <p className="text-[10px] text-slate-500">Free Plan</p>
          </div>
          <span className="material-symbols-outlined ml-auto text-slate-400 cursor-pointer hover:text-slate-600 dark:hover:text-slate-200">
            settings
          </span>
        </div>

      </div>
    </aside>
  );
}
