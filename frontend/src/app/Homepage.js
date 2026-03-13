"use client";

import { useState } from "react";
import { useRef } from "react";
// import Sidebar from "@/components/Sidebar";

const featureCards = [
  {
    icon: "lightbulb",
    title: "Smart Synthesis",
    description:
      "Automatically connect dots between your uploaded PDFs and meeting notes.",
  },
  {
    icon: "security",
    title: "Private by Design",
    description:
      "Your data is encrypted and never used for training foundation models.",
  },
];

// const filterTabs = ["Photos", "PDFs", "URLs"];



export default function Homepage() {
  const [activeFilter, setActiveFilter] = useState("PDFs");
  const [inputText, setInputText] = useState("");

  // handle images and links upload
  const imageInputRef = useRef(null);

  function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    console.log("Selected image:", file);
    // You can upload or process the file here
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* <Sidebar /> */}

      <main className="flex-1 flex flex-col overflow-y-auto relative">

        {/* Header */}
        <header className="flex items-center justify-between px-8 py-4 sticky top-0 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md z-10 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-4">
            <button className="lg:hidden p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800">
              <span className="material-symbols-outlined">menu</span>
            </button>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-search" viewBox="0 0 16 16">
                  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
                </svg>
              </span>
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 bg-slate-200/50 dark:bg-slate-800/50 border-none rounded-lg text-sm focus:ring-1 focus:ring-primary w-64 md:w-96"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="bg-[#8a5cf6db] hover:bg-[#8a5cf6] text-white px-5 py-2 rounded-lg text-sm font-bold transition-shadow shadow-lg shadow-primary/20">
              Account
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="max-w-4xl mx-auto w-full px-6 py-12 flex flex-col flex-1">

          {/* Hero */}
          <div className="mb-12 text-center lg:text-left">
            <h1 className="text-4xl lg:text-5xl font-black mb-4 tracking-tight">
              Dump Here, Sort Later
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
              A clean, minimalist space to store and chat with your knowledge.
              Upload docs, links, and images to build your private intelligence base.
            </p>
          </div>

          {/* Input Card */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl shadow-slate-200/50 dark:shadow-none overflow-hidden transition-all">
            <div className="flex flex-col min-h-[180px]">
              <div className="flex items-start p-4 gap-4">
                {/* <div className="size-10 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-slate-400">account_circle</span>
                </div> */}
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Drop resources here or type a question..."
                  className="w-full bg-transparent border-none focus:outline-none text-lg resize-none placeholder:text-slate-400 dark:placeholder:text-slate-600 pt-2 min-h-[120px]"
                />
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-1">

                  <input
                    type="file"
                    accept="image/*"
                    ref={imageInputRef}   // use useRef to access programmatically
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                  {[
                    { 
                      icon: "image", 
                      title: "Add image",
                      onClick: () => imageInputRef.current?.click(),
                      customIcon: (
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-image-fill" viewBox="0 0 16 16">
                          <path d="M.002 3a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-12a2 2 0 0 1-2-2zm1 9v1a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062zm5-6.5a1.5 1.5 0 1 0-3 0 1.5 1.5 0 0 0 3 0"/>
                        </svg>
                      )
                    }
                  ].map(({ icon, title, customIcon, onClick  }) => (
                    <button
                      key={icon}
                      title={title}
                      className="p-2 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors text-slate-500"
                      onClick={onClick}
                    >
                      {customIcon ?? <span className="material-symbols-outlined">{icon}</span>}
                    </button>
                  ))}
                  <div className="w-px h-6 bg-slate-300 dark:bg-slate-700 mx-2" />
                  {/* <button
                    title="Audio"
                    className="p-2 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors text-slate-500"
                  >
                    <span className="material-symbols-outlined">mic</span>
                  </button> */}
                </div>
                <button className="bg-primary text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-primary/90 transition-all">
                  <span>Create</span>
                  <span className="material-symbols-outlined text-sm">send</span>
                </button>
              </div>
            </div>
          </div>

          {/* Filter Tabs */}
          {/* <div className="mt-8 flex justify-center">
            <div className="flex h-12 w-full max-w-sm items-center justify-center rounded-xl bg-slate-200 dark:bg-slate-800/80 p-1.5 shadow-inner">
              {filterTabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveFilter(tab)}
                  className={`flex h-full grow items-center justify-center overflow-hidden rounded-lg px-2 text-sm font-semibold leading-normal transition-all
                    ${
                      activeFilter === tab
                        ? "bg-white dark:bg-slate-900 shadow-sm text-primary"
                        : "text-slate-500"
                    }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div> */}

          {/* Feature Cards */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-6">
            {featureCards.map(({ icon, title, description }) => (
              <div
                key={title}
                className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800"
              >
                <div className="size-10 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-4">
                  <span className="material-symbols-outlined">{icon}</span>
                </div>
                <h3 className="font-bold text-lg mb-2">{title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                  {description}
                </p>
              </div>
            ))}
          </div>

          <div className="py-12 text-center text-slate-400 text-xs">
            Inspired by modern productivity tools. Built for thinkers.
          </div>

        </div>
      </main>
    </div>
  );
}
