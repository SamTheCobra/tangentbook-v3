"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const stored = localStorage.getItem("tangentbook_theme");
    if (stored === "light") {
      setTheme("light");
    }
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("tangentbook_theme", next);
    if (next === "light") {
      document.documentElement.setAttribute("data-theme", "light");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  };

  return (
    <button
      onClick={toggle}
      className="text-xs uppercase hover:underline"
      style={{
        color: "var(--text-muted)",
        letterSpacing: "0.08em",
        background: "none",
        border: "none",
        cursor: "pointer",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {theme === "dark" ? "LIGHT MODE" : "DARK MODE"}
    </button>
  );
}
