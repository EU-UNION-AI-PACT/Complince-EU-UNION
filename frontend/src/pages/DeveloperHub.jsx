import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Github, ExternalLink } from "lucide-react";
import { listRepos } from "../lib/api";

const CAT_COLOR = {
  ARF: "amber",
  "SD-JWT VC": "blue",
  JMAP: "amber",
  "SPID/CIE": "blue",
  Swiyu: "amber",
  DIDComm: "blue",
  "Status List": "emerald",
  Wallet: "amber",
};

export default function DeveloperHub() {
  const { t } = useTranslation();
  const [repos, setRepos] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    listRepos().then(setRepos).catch(() => setRepos([]));
  }, []);

  const cats = ["all", ...Array.from(new Set(repos.map((r) => r.category)))];
  const visible = filter === "all" ? repos : repos.filter((r) => r.category === filter);

  return (
    <div className="mx-auto max-w-[1500px] px-6 lg:px-10 py-12">
      <div className="text-[10px] font-mono uppercase tracking-[0.22em] text-amber-500 mb-3">
        DEVELOPER HUB · OSS REGISTRY
      </div>
      <h1 className="font-serif font-light text-4xl lg:text-5xl text-white leading-tight mb-3">
        {t("hub.title")}
      </h1>
      <p className="text-slate-400 max-w-2xl mb-10">{t("hub.subtitle")}</p>

      <div className="flex flex-wrap gap-2 mb-8">
        {cats.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            data-testid={`hub-filter-${c}`}
            data-active={filter === c}
            className={`text-[11px] font-mono uppercase tracking-wider px-3 py-1.5 rounded-sm border transition-colors ${
              filter === c
                ? "border-amber-500 bg-amber-500/10 text-amber-500"
                : "border-white/10 text-slate-400 hover:text-white hover:border-white/25"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((r) => {
          const tint = CAT_COLOR[r.category] || "blue";
          return (
            <a
              key={r.slug}
              href={r.url}
              target="_blank"
              rel="noreferrer"
              data-testid={`hub-repo-${r.slug.replace(/[\/]/g, "-")}`}
              className={`trace-beam group border border-white/10 bg-[#0a0f19] p-5 rounded-sm hover:border-${tint}-500/60 transition-colors flex flex-col`}
            >
              <div className="flex items-start justify-between gap-2 mb-3">
                <div
                  className={`text-[9px] font-mono uppercase tracking-widest px-2 py-0.5 rounded-sm border ${
                    tint === "amber"
                      ? "border-amber-500/40 bg-amber-500/[0.06] text-amber-500"
                      : tint === "emerald"
                      ? "border-emerald-500/40 bg-emerald-500/[0.06] text-emerald-400"
                      : "border-blue-500/40 bg-blue-500/[0.06] text-blue-400"
                  }`}
                >
                  {r.category}
                </div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">
                  {r.role}
                </span>
              </div>
              <div className="flex items-center gap-2 mb-2">
                <Github size={13} strokeWidth={1.7} className="text-slate-500" />
                <div className="font-mono text-[13px] text-white group-hover:text-amber-400 transition-colors truncate">
                  {r.slug}
                </div>
              </div>
              <p className="text-[12px] text-slate-400 leading-relaxed flex-1">{r.description}</p>
              <div className="mt-4 flex items-center gap-1 text-[11px] text-blue-400 group-hover:text-blue-300">
                {t("hub.open")}
                <ExternalLink size={11} strokeWidth={1.7} />
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
