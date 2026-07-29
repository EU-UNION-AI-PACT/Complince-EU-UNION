import React from "react";
import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Languages,
  Shield,
  FileText,
  FlaskConical,
  Gauge,
  GitBranch,
  Globe,
  Github,
  LogIn,
  LogOut,
  ShieldAlert,
} from "lucide-react";
import { useAuth } from "../lib/auth";

const items = [
  { to: "/", labelKey: "landing", icon: Shield, testId: "nav-landing" },
  { to: "/paper", labelKey: "paper", icon: FileText, testId: "nav-paper" },
  { to: "/sandbox", labelKey: "sandbox", icon: FlaskConical, testId: "nav-sandbox" },
  { to: "/compliance", labelKey: "compliance", icon: Gauge, testId: "nav-compliance" },
  { to: "/trust", labelKey: "trust", icon: GitBranch, testId: "nav-trust" },
  { to: "/federation", labelKey: "federation", icon: Globe, testId: "nav-federation" },
  { to: "/hub", labelKey: "hub", icon: Github, testId: "nav-hub" },
];

const adminItem = { to: "/admin", labelKey: "admin", icon: ShieldAlert, testId: "nav-admin" };

export function Header() {
  const { t, i18n } = useTranslation();
  const { user, loading, loginWithGoogle, logout } = useAuth();
  const navItems = user?.role === "admin" ? [...items, adminItem] : items;
  const toggleLang = () => {
    const next = i18n.language === "de" ? "en" : "de";
    i18n.changeLanguage(next);
    window.localStorage.setItem("eudi_lang", next);
  };
  return (
    <header
      className="sticky top-0 z-30 backdrop-blur-xl border-b border-white/10 bg-[#090d16]/85"
      data-testid="app-header"
    >
      <div className="mx-auto max-w-[1500px] px-6 lg:px-10 py-3 flex items-center gap-8">
        <NavLink to="/" className="flex items-center gap-3 group" data-testid="brand-link">
          <div className="relative w-8 h-8 flex items-center justify-center rounded-sm border border-amber-500/50 bg-amber-500/10 glow-amber">
            <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse-amber" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="font-serif text-[1.05rem] font-medium tracking-tight text-white">
              {t("brand")}
            </span>
            <span className="text-[9px] font-mono uppercase tracking-[0.24em] text-amber-500/90">
              {t("brand_tag")}
            </span>
          </div>
        </NavLink>
        <nav className="hidden lg:flex items-center gap-1 flex-1">
          {navItems.map(({ to, labelKey, icon: Icon, testId }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              data-testid={testId}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 text-[13px] font-medium rounded-sm transition-colors ` +
                (isActive
                  ? labelKey === "admin"
                    ? "text-red-400 bg-red-500/10 border-b-2 border-red-500"
                    : "text-amber-400 bg-amber-500/10 border-b-2 border-amber-500"
                  : "text-slate-400 hover:text-white hover:bg-white/5")
              }
            >
              <Icon size={14} strokeWidth={1.6} />
              <span>{labelKey === "admin" ? "Admin" : t(`nav.${labelKey}`)}</span>
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          {!loading && user ? (
            <div className="flex items-center gap-2" data-testid="auth-user-block">
              {user.picture ? (
                <img
                  src={user.picture}
                  alt=""
                  className="w-7 h-7 rounded-full border border-amber-500/50"
                />
              ) : (
                <div className="w-7 h-7 rounded-full border border-amber-500/50 bg-amber-500/10 flex items-center justify-center text-[10px] font-mono text-amber-500">
                  {user.name?.[0] || "?"}
                </div>
              )}
              <span className="hidden md:inline text-[11px] font-mono text-slate-300 max-w-[130px] truncate" data-testid="auth-user-email">
                {user.email}
              </span>
              <button
                onClick={logout}
                data-testid="logout-btn"
                className="p-2 rounded-sm border border-white/10 hover:border-red-500/50 text-slate-400 hover:text-red-400 transition-colors"
                title="Logout"
              >
                <LogOut size={12} strokeWidth={1.6} />
              </button>
            </div>
          ) : !loading ? (
            <button
              onClick={loginWithGoogle}
              data-testid="login-btn"
              className="flex items-center gap-2 px-3 py-2 rounded-sm border border-amber-500/50 hover:bg-amber-500 hover:text-black text-amber-400 transition-colors text-xs font-mono uppercase tracking-wider"
            >
              <LogIn size={12} strokeWidth={1.7} />
              Sign in
            </button>
          ) : null}
          <button
            onClick={toggleLang}
            data-testid="lang-toggle"
            className="flex items-center gap-2 px-3 py-2 rounded-sm border border-white/10 text-slate-300 hover:text-white hover:border-amber-500/50 transition-colors text-xs font-mono uppercase tracking-wider"
          >
            <Languages size={14} strokeWidth={1.6} />
            {i18n.language === "de" ? "DE" : "EN"}
          </button>
        </div>
      </div>
      {/* mobile nav */}
      <nav className="lg:hidden flex items-center gap-1 overflow-x-auto px-6 pb-2 border-t border-white/5">
        {navItems.map(({ to, labelKey, icon: Icon, testId }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            data-testid={`m-${testId}`}
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 text-[11px] rounded-sm transition-colors whitespace-nowrap ` +
              (isActive
                ? labelKey === "admin"
                  ? "text-red-400 bg-red-500/10"
                  : "text-amber-400 bg-amber-500/10"
                : "text-slate-400 hover:text-white")
            }
          >
            <Icon size={12} strokeWidth={1.6} />
            {labelKey === "admin" ? "Admin" : t(`nav.${labelKey}`)}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
