import { useState } from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Eye, TrendingUp, ExternalLink } from "lucide-react";
import type { Content, Dataset } from "./types";
import { api } from "./api";
import { dayOffset, fmt, shortDate } from "./analytics";
import { safeUrl, Stat } from "./components";
export default function ContentDetail({
  content: c,
  data,
  workspace,
  notify,
}: {
  content: Content;
  data: Dataset;
  workspace: string;
  notify: (s: string) => void;
}) {
  const [rows, setRows] = useState<
      { position: number; retention: number }[] | null
    >(null),
    [busy, setBusy] = useState(false);
  const r = data.resources.find((item) => item.id === c.resource_id);
  const end =
    r?.coverage?.end || dayOffset(new Date().toISOString().slice(0, 10), -3);
  const start = dayOffset(end, -27);
  async function load() {
    setBusy(true);
    try {
      if (data.demo) {
        setRows(
          Array.from({ length: 21 }, (_, i) => ({
            position: i * 5,
            retention: Math.round(96 - i * 2.4 - Math.sin(i / 3) * 8),
          })),
        );
        return;
      }
      const res = await api<{
        rows: { position: number; retention: number }[];
      }>(
        "/resources/" +
          c.resource_id +
          "/retention/" +
          c.id +
          "?start=" +
          start +
          "&end=" +
          end,
        {},
        workspace,
      );
      setRows(res.rows);
      if (!res.rows.length)
        notify("Não há dados de retenção disponíveis neste período.");
    } catch (e) {
      notify(
        e instanceof Error
          ? e.message
          : "Não foi possível consultar a retenção.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="form">
      <div className="mini-stats">
        <Stat
          label="Visualizações"
          value={fmt(c.views)}
          icon={Eye}
          detail="Total acumulado"
        />
        <Stat
          label="Curtidas"
          value={fmt(c.likes)}
          icon={TrendingUp}
          detail="Total acumulado"
        />
      </div>
      <p className="muted">
        Publicado em {new Date(c.published).toLocaleDateString("pt-BR")} ·{" "}
        {c.source}
      </p>
      {c.url && (
        <a
          className="text-btn"
          href={safeUrl(c.url)}
          target="_blank"
          rel="noreferrer"
        >
          Abrir na plataforma <ExternalLink size={14} />
        </a>
      )}
      {r?.provider === "youtube" && (
        <>
          <div className="between">
            <h3>Retenção ao longo do vídeo</h3>
            <button className="btn" disabled={busy} onClick={load}>
              {busy ? "Consultando…" : "Consultar"}
            </button>
          </div>
          <p className="muted">
            {shortDate(start)} a {shortDate(end)}
            {data.demo ? " · Curva fictícia" : ""}
          </p>
          {rows && (
            <div className="retention-chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={rows}>
                  <XAxis dataKey="position" unit="%" tick={{ fontSize: 11 }} />
                  <YAxis unit="%" tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Area
                    isAnimationActive={false}
                    dataKey="retention"
                    name="Retenção (%)"
                    stroke="#ed633a"
                    fill="#fff0e9"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
}
