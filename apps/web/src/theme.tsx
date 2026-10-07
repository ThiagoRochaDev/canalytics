import { useEffect, useState } from "react";
import { Monitor, Moon, Sun } from "lucide-react";
export type ThemePreference = "light" | "dark" | "system";
const KEY = "canalytics.theme";
export function readPreference(): ThemePreference {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved === "light" || saved === "dark" || saved === "system")
      return saved;
  } catch {}
  return "system";
}
export function useTheme() {
  const [preference, setPreference] = useState<ThemePreference>(readPreference);
  const [systemDark, setSystemDark] = useState(
    () => matchMedia("(prefers-color-scheme: dark)").matches,
  );
  const resolved =
    preference === "system" ? (systemDark ? "dark" : "light") : preference;
  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const update = () => setSystemDark(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = resolved;
    document.documentElement.style.colorScheme = resolved;
    try {
      localStorage.setItem(KEY, preference);
    } catch {}
  }, [resolved, preference]);
  return { preference, resolved, setPreference };
}
export function ThemeButton({
  resolved,
  onChange,
}: {
  resolved: string;
  onChange: (p: ThemePreference) => void;
}) {
  return (
    <button
      className="icon-btn theme-button"
      aria-label={
        resolved === "dark" ? "Ativar tema claro" : "Ativar tema escuro"
      }
      title={resolved === "dark" ? "Tema claro" : "Tema escuro"}
      onClick={() => onChange(resolved === "dark" ? "light" : "dark")}
    >
      {resolved === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
export function ThemeSelect({
  value,
  onChange,
}: {
  value: ThemePreference;
  onChange: (p: ThemePreference) => void;
}) {
  return (
    <div className="appearance-panel">
      <div>
        <Monitor size={18} />
        <span>
          <strong>Aparência</strong>
          <small>Preferência salva neste navegador.</small>
        </span>
      </div>
      <select
        aria-label="Tema da interface"
        value={value}
        onChange={(e) => onChange(e.target.value as ThemePreference)}
      >
        <option value="system">Seguir o sistema</option>
        <option value="light">Claro</option>
        <option value="dark">Escuro</option>
      </select>
    </div>
  );
}
