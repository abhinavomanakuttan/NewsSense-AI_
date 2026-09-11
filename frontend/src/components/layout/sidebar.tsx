"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bookmark,
  Calendar,
  Globe,
  History,
  Home,
  LayoutDashboard,
  MapPin,
  Newspaper,
  Search,
  Settings,
  Sparkles,
  Zap,
} from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
}

const baseNavItems = [
  { href: "/feed", label: "Feed", icon: Home },
  { href: "/search", label: "Search", icon: Search },
  { href: "/events", label: "Events", icon: Calendar },
  { href: "/bookmarks", label: "Bookmarks", icon: Bookmark },
  { href: "/chatbot", label: "AI Chat", icon: Sparkles },
  { href: "/history", label: "History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

// Regional intelligence navigation
const regionalNavItems = [
  {
    href: "/breaking",
    label: "Breaking",
    icon: Zap,
    accent: "text-red-500",
    activeBg: "bg-red-500 text-white",
  },
  {
    href: "/kerala",
    label: "Kerala",
    icon: MapPin,
    accent: "text-emerald-600",
    activeBg: "bg-emerald-600 text-white",
  },
  {
    href: "/india",
    label: "India",
    icon: Newspaper,
    accent: "text-orange-600",
    activeBg: "bg-orange-600 text-white",
  },
  {
    href: "/global",
    label: "Global",
    icon: Globe,
    accent: "text-blue-600",
    activeBg: "bg-blue-600 text-white",
  },
];

export function Sidebar({ isOpen }: SidebarProps) {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);

  const navItems =
    user?.role === "admin"
      ? [
          ...baseNavItems.slice(0, 2),
          { href: "/admin", label: "Admin", icon: LayoutDashboard },
          ...baseNavItems.slice(2),
        ]
      : baseNavItems;

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r bg-card transition-transform lg:static lg:translate-x-0",
        isOpen ? "translate-x-0" : "-translate-x-full",
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/feed" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Newspaper className="h-5 w-5 text-primary-foreground" />
          </span>
          <span className="text-lg font-bold">NewsSense AI</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {/* ── Regional Intelligence Section ── */}
        <div className="mb-1 mt-1">
          <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            Regional Intelligence
          </p>
          {regionalNavItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? item.activeBg
                    : `hover:bg-accent hover:text-accent-foreground ${item.accent}`,
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
                {item.href === "/breaking" && (
                  <span className="ml-auto flex h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                )}
              </Link>
            );
          })}
        </div>

        <div className="my-2 border-t" />

        {/* ── Main Navigation ── */}
        <div>
          <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            Navigation
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/feed" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </aside>
  );
}
