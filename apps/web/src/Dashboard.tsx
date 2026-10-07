import { useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  ArrowDownToLine,
  CalendarDays,
  ChevronRight,
  Clock3,
  Eye,
  Info,
  MessageSquare,
  Sparkles,
  Trash2,
  TrendingUp,
  Users,
} from "lucide-react";
import type { Content, Daily, Dataset, Resource } from "./types";
import {
  dayCount,
  dayOffset,
  fmt,
  period,
  shortDate,
  sum,
  labelProvider,
} from "./analytics";
import { api, post, saveBlob } from "./api";
import { Avatar, Badge, ContentTable, Source, Stat } from "./components";

interface Props {
  data: Dataset;
  r: Resource;
  workspace: string;
  onSelect: (id: string) => void;
  onContent: (c: Content) => void;
  onLibrary: () => void;
  notify: (s: string) => void;
  refresh: () => void;
}
export default function Dashboard({
  data,
  r,
  workspace,
  onSelect,
  onContent,
  onLibrary,
  notify,
  refresh,
}: Props) {
  const [days, setDays] = useState(28),
    [customStart, setCustomStart] = useState(""),
    [customEnd, setCustomEnd] = useState("");
  const [metric, setMetric] = useState<keyof Daily>("views"),
    [compare, setCompare] = useState(true),
    [note, setNote] = useState(""),
    [busy, setBusy] = useState(false);
  const lastSnapshot = data.snapshots
    .filter((s) => s.resource_id === r.id)
    .at(-1);
  const end =
    customEnd ||
    r.coverage?.end ||
    lastSnapshot?.observed_at.slice(0, 10) ||
    dayOffset(new Date().toISOString().slice(0, 10), -3);
  const start = customStart || dayOffset(end, -days + 1);
  const valid = start <= end && dayCount(start, end) <= 366;
  const stats = period(
    data.daily.filter((row) => row.resource_id === r.id),
    valid ? start : end,
    end,
  );
  const chart = Array.from({ length: stats.length }, (_, i) => {
    const day = dayOffset(valid ? start : end, i);
    return {
      day,
      value: stats.current.find((row) => row.day === day)?.[metric] ?? null,
      previous:
        stats.previous.find(
          (row) => row.day === dayOffset(day, -stats.length),
        )?.[metric] ?? null,
    };
  });
  const snapshots = data.snapshots.filter(
    (s) =>
      s.resource_id === r.id &&
      s.observed_at.slice(0, 10) >= start &&
      s.observed_at.slice(0, 10) <= end,
  );
  const latest = snapshots.at(-1);
  const contents = data.contents
    .filter((c) => c.resource_id === r.id)
    .sort((a, b) => (b.views ?? -1) - (a.views ?? -1));
  const gained = sum(stats.current, "gained"),
    lost = sum(stats.current, "lost"),
    minutes = sum(stats.current, "minutes"),
    change = stats.delta("views"),
    revenue = sum(stats.current, "revenue");
  async function run(fn: () => Promise<void>) {
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      notify(e instanceof Error ? e.message : "Ocorreu um erro.");
    } finally {
      setBusy(false);
    }
  }
  async function exportData() {
    if (data.demo) {
      const rows = (r.mode === "daily" ? data.daily : data.snapshots).filter(
        (row) => row.resource_id === r.id,
      );
      if (!rows.length) {
        notify("Ainda não há dados para exportar.");
        return;
      }
      const fields = Object.keys(rows[0]);
      const text =
        fields.join(",") +
        "\n" +
        rows
          .map((row) =>
            fields
              .map((k) =>
                JSON.stringify(
                  (row as unknown as Record<string, unknown>)[k] ?? "",
                ),
              )
              .join(","),
          )
          .join("\n");
      saveBlob(
        new Blob(["\ufeff" + text], { type: "text/csv" }),
        "canalytics-DEMONSTRACAO.csv",
      );
      return;
    }
    const res = await fetch("/api/resources/" + r.id + "/export", {
      headers: { "X-Workspace-ID": workspace },
    });
    if (!res.ok) throw new Error("Não foi possível exportar.");
    saveBlob(await res.blob(), "canalytics-" + r.provider + ".csv");
  }
  return (
    <>
      <div className="filterbar">
        <div className="channel-select">
          <Avatar r={r} small />
          <select
            aria-label="Canal analisado"
            value={r.id}
            onChange={(e) => onSelect(e.target.value)}
          >
            {data.resources.map((item) => (
              <option value={item.id} key={item.id}>
                {item.name} · {labelProvider(item.provider)}
              </option>
            ))}
          </select>
        </div>
        <div className="date-controls">
          <CalendarDays size={16} />
          <select
            aria-label="Período"
            value={customStart || customEnd ? "custom" : days}
            onChange={(e) => {
              if (e.target.value === "custom") {
                setCustomStart(start);
                setCustomEnd(end);
              } else {
                setDays(Number(e.target.value));
                setCustomStart("");
                setCustomEnd("");
              }
            }}
          >
            <option value={7}>Últimos 7 dias disponíveis</option>
            <option value={28}>Últimos 28 dias disponíveis</option>
            <option value={90}>Últimos 90 dias disponíveis</option>
            <option value="custom">Período personalizado</option>
          </select>
          <button
            className="btn"
            disabled={busy}
            onClick={() => run(exportData)}
          >
            <ArrowDownToLine size={16} />
            Exportar
          </button>
        </div>
      </div>
      {(customStart || customEnd) && (
        <div className="custom-dates">
          <label>
            De
            <input
              type="date"
              value={customStart}
              onInput={(e) => setCustomStart(e.currentTarget.value)}
              onChange={(e) => setCustomStart(e.target.value)}
            />
          </label>
          <label>
            Até
            <input
              type="date"
              value={customEnd}
              onInput={(e) => setCustomEnd(e.currentTarget.value)}
              onChange={(e) => setCustomEnd(e.target.value)}
            />
          </label>
          {!valid && (
            <span className="negative">
              Use um intervalo válido de até 366 dias.
            </span>
          )}
        </div>
      )}
      {r.sync_error && (
        <div className="alert">
          <Info size={18} />
          {r.sync_error}
        </div>
      )}
      <div className="period-label">
        {shortDate(start)} — {shortDate(end)}
        <span>
          {r.mode === "daily"
            ? "Relatório diário · " +
              stats.current.length +
              "/" +
              stats.length +
              " dias retornados" +
              (!stats.full ? " · Cobertura parcial" : "")
            : "Snapshots · histórico construído a partir das coletas"}
        </span>
      </div>
      {r.mode === "daily" ? (
        <>
          <div className="stats-grid">
            <Stat
              label="Visualizações"
              value={fmt(sum(stats.current, "views"))}
              delta={change}
              icon={Eye}
            />
            <Stat
              label="Tempo assistido"
              value={minutes == null ? "—" : fmt(minutes / 60) + " h"}
              delta={stats.delta("minutes")}
              icon={Clock3}
            />
            <Stat
              label="Inscritos (saldo)"
              value={
                gained == null || lost == null
                  ? "—"
                  : (gained - lost >= 0 ? "+" : "") + fmt(gained - lost)
              }
              icon={Users}
              detail={fmt(gained) + " ganhos · " + fmt(lost) + " perdidos"}
            />
            <Stat
              label="Curtidas"
              value={fmt(sum(stats.current, "likes"))}
              delta={stats.delta("likes")}
              icon={TrendingUp}
            />
          </div>
          <section className="card chart-card">
            <div className="card-heading">
              <div>
                <h2>Evolução do canal</h2>
                <p>Cada publicação faz parte de uma trajetória.</p>
              </div>
              <div className="chart-controls">
                <select
                  aria-label="Métrica do gráfico"
                  value={metric}
                  onChange={(e) => setMetric(e.target.value as keyof Daily)}
                >
                  <option value="views">Visualizações</option>
                  <option value="minutes">Minutos assistidos</option>
                  <option value="gained">Inscritos ganhos</option>
                  <option value="likes">Curtidas</option>
                  <option value="comments">Comentários</option>
                  <option value="shares">Compartilhamentos</option>
                </select>
                <label className="check-label">
                  <input
                    type="checkbox"
                    checked={compare}
                    onChange={(e) => setCompare(e.target.checked)}
                  />
                  Comparar
                </label>
              </div>
            </div>
            <div className="chart-legend">
              <span>
                <i className="orange" />
                Período selecionado
              </span>
              {compare && (
                <span>
                  <i className="gray" />
                  Período anterior
                </span>
              )}
            </div>
            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={chart}
                  margin={{ top: 12, right: 12, left: -12, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor="#ee653d"
                        stopOpacity={0.18}
                      />
                      <stop
                        offset="100%"
                        stopColor="#ee653d"
                        stopOpacity={0.01}
                      />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    vertical={false}
                    stroke="var(--chart-grid)"
                    strokeDasharray="4 4"
                  />
                  <XAxis
                    dataKey="day"
                    tickFormatter={shortDate}
                    axisLine={false}
                    tickLine={false}
                    minTickGap={55}
                    tick={{ fill: "var(--axis)", fontSize: 11 }}
                    dy={8}
                  />
                  <YAxis
                    tickFormatter={(v) => fmt(v, true)}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "var(--axis)", fontSize: 11 }}
                  />
                  <Tooltip
                    labelFormatter={(v) => shortDate(String(v))}
                    formatter={(v, name) => [
                      fmt(Number(v)),
                      name === "value"
                        ? "Período selecionado"
                        : "Período anterior",
                    ]}
                    contentStyle={{
                      borderRadius: 10,
                      borderColor: "#e8e8eb",
                      fontSize: 12,
                    }}
                  />
                  {compare && (
                    <Line
                      isAnimationActive={false}
                      type="monotone"
                      dataKey="previous"
                      stroke="#b9c1ca"
                      strokeDasharray="5 5"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                  )}
                  <Area
                    isAnimationActive={false}
                    type="monotone"
                    dataKey="value"
                    stroke="#ee653d"
                    fill="url(#fill)"
                    strokeWidth={2.5}
                    connectNulls={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <Source r={r} demo={data.demo} />
          </section>
          <div className="insight-card">
            <span className="insight-icon">
              <Sparkles size={20} />
            </span>
            <div>
              <strong>
                {change != null
                  ? change >= 0
                    ? "Seu canal ganhou ritmo."
                    : "Um período para observar mais de perto."
                  : "Seu histórico está ganhando contexto."}
              </strong>
              <p>
                {change != null
                  ? "As visualizações " +
                    (change >= 0 ? "cresceram " : "caíram ") +
                    Math.abs(change).toFixed(1).replace(".", ",") +
                    "% em relação aos " +
                    stats.length +
                    " dias anteriores. Explore os conteúdos para investigar a mudança."
                  : "Comparações precisam de dois períodos completos. Dias não retornados não são tratados como zero."}
              </p>
            </div>
            <Badge>Leitura do período</Badge>
          </div>
          <div className="two-col">
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Como seu público chega</h2>
                  <p>Fontes de tráfego retornadas pela plataforma</p>
                </div>
              </div>
              <Breakdown kind="traffic" data={data} r={r} />
            </section>
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Onde estão assistindo</h2>
                  <p>Dispositivos usados pelo seu público</p>
                </div>
                <Users size={18} />
              </div>
              <Breakdown kind="device" data={data} r={r} />
            </section>
          </div>
          <section className="card">
            <div className="card-heading">
              <div>
                <h2>Conteúdos em destaque</h2>
                <p>Visualizações acumuladas desde a publicação</p>
              </div>
              <button className="text-btn" onClick={onLibrary}>
                Ver todos
                <ChevronRight size={16} />
              </button>
            </div>
            <ContentTable
              items={contents.slice(0, 5)}
              data={data}
              onOpen={onContent}
            />
          </section>
          <div className="two-col">
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Geografia do público</h2>
                  <p>Países retornados pela plataforma</p>
                </div>
              </div>
              <Breakdown kind="country" data={data} r={r} />
            </section>
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Mais detalhes do período</h2>
                  <p>Disponibilidade varia conforme a permissão</p>
                </div>
              </div>
              <div className="detail-list">
                <div>
                  <span>Comentários</span>
                  <strong>{fmt(sum(stats.current, "comments"))}</strong>
                </div>
                <div>
                  <span>Compartilhamentos</span>
                  <strong>{fmt(sum(stats.current, "shares"))}</strong>
                </div>
                <div>
                  <span>Receita estimada (USD)</span>
                  <strong>
                    {revenue == null
                      ? "Não disponível"
                      : new Intl.NumberFormat("pt-BR", {
                          style: "currency",
                          currency: "USD",
                        }).format(revenue)}
                  </strong>
                </div>
                <div>
                  <span>Retenção por vídeo</span>
                  <span>Abra um conteúdo</span>
                </div>
              </div>
            </section>
          </div>
        </>
      ) : (
        <>
          <div className="stats-grid">
            <Stat
              label={r.followers_label || "Seguidores"}
              value={fmt(r.followers)}
              icon={Users}
              detail="Última coleta do perfil"
            />
            <Stat
              label={
                r.kind === "community"
                  ? "Membros online (aprox.)"
                  : "Espectadores ao vivo"
              }
              value={fmt(
                r.kind === "community" ? latest?.online : latest?.live_viewers,
              )}
              icon={Eye}
              detail="Último snapshot no período"
            />
            <Stat
              label="Itens retornados"
              value={fmt(r.content_count)}
              icon={TrendingUp}
              detail={
                r.kind === "community"
                  ? "Canais do servidor"
                  : "Conteúdos do catálogo"
              }
            />
            <Stat
              label="Coletas no período"
              value={fmt(snapshots.length)}
              icon={Clock3}
              detail="Sem reconstrução retroativa"
            />
          </div>
          <section className="card chart-card">
            <div className="card-heading">
              <div>
                <h2>
                  {r.kind === "community"
                    ? "Evolução de membros"
                    : "Evolução de seguidores"}
                </h2>
                <p>Contagem em cada coleta; não representa ganho diário.</p>
              </div>
              <Badge>Snapshots</Badge>
            </div>
            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={snapshots}>
                  <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
                  <XAxis
                    dataKey="observed_at"
                    tickFormatter={shortDate}
                    minTickGap={55}
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={(v) => fmt(v, true)}
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip labelFormatter={(v) => shortDate(String(v))} />
                  <Area
                    isAnimationActive={false}
                    dataKey={r.kind === "community" ? "members" : "followers"}
                    name={r.kind === "community" ? "Membros" : "Seguidores"}
                    stroke={r.color}
                    fill={r.color + "18"}
                    strokeWidth={2}
                    connectNulls={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <Source r={r} demo={data.demo} />
          </section>
          <div className="info-box">
            <Info size={18} />
            <p>
              {r.live ? "Ao vivo na última coleta: " + r.live_title + ". " : ""}
              O histórico deste conector começa quando a coleta é ativada.
              Intervalos sem coleta e métricas não disponibilizadas ficam sem
              valor.
            </p>
          </div>
          <ContentTable
            items={contents.slice(0, 10)}
            data={data}
            onOpen={onContent}
          />
        </>
      )}
      <section className="card">
        <div className="card-heading">
          <div>
            <h2>Diário do canal</h2>
            <p>Registre publicações, mudanças de estratégia e aprendizados.</p>
          </div>
          <MessageSquare size={18} />
        </div>
        <form
          className="note-form"
          onSubmit={(e) => {
            e.preventDefault();
            if (data.demo) {
              notify(
                "As anotações ficam disponíveis ao conectar seu próprio canal.",
              );
              return;
            }
            run(async () => {
              await api(
                "/resources/" + r.id + "/notes",
                post({ body: note }),
                workspace,
              );
              setNote("");
              refresh();
            });
          }}
        >
          <input
            aria-label="Anotação do canal"
            placeholder="O que mudou no seu canal?"
            value={note}
            maxLength={2000}
            onChange={(e) => setNote(e.target.value)}
            required
          />
          <button className="btn" disabled={busy}>
            Adicionar
          </button>
        </form>
        {data.notes
          .filter((n) => n.resource_id === r.id)
          .map((n) => (
            <div className="note" key={n.id}>
              <div>
                <p>{n.body}</p>
                <small>{shortDate(n.created)}</small>
              </div>
              <button
                className="icon-btn"
                aria-label="Remover anotação"
                onClick={() =>
                  run(async () => {
                    await api(
                      "/notes/" + n.id,
                      { method: "DELETE" },
                      workspace,
                    );
                    refresh();
                  })
                }
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
      </section>
    </>
  );
}
const labels: Record<string, string> = {
  RELATED_VIDEO: "Vídeos relacionados",
  YT_SEARCH: "Pesquisa do YouTube",
  SUBSCRIBER: "Inscrições",
  EXT_URL: "Fontes externas",
  MOBILE: "Celular",
  DESKTOP: "Computador",
  TV: "TV",
  TABLET: "Tablet",
  BR: "Brasil",
  PT: "Portugal",
  US: "Estados Unidos",
};
function Breakdown({
  kind,
  data,
  r,
}: {
  kind: string;
  data: Dataset;
  r: Resource;
}) {
  const rows =
    data.breakdowns.find((b) => b.resource_id === r.id && b.kind === kind)
      ?.rows || [];
  const max = Math.max(1, ...rows.map((row) => row.value));
  return rows.length ? (
    <div className="breakdown">
      {rows.slice(0, 5).map((row, i) => (
        <div key={row.label}>
          <div>
            <span>
              <i
                style={{
                  background: [
                    "#ed633a",
                    "#ef9674",
                    "#f5bd9c",
                    "#cad1d8",
                    "#9ca9b7",
                  ][i],
                }}
              />
              {labels[row.label] || row.label}
            </span>
            <strong>{fmt(row.value, true)}</strong>
          </div>
          <div className="bar-track">
            <span
              style={{
                width: (row.value / max) * 100 + "%",
                background: i === 0 ? "#ed633a" : "#e8c3b6",
              }}
            />
          </div>
        </div>
      ))}
      <p className="breakdown-note">
        Visualizações · {shortDate(rows[0].start)} a {shortDate(rows[0].end)} ·
        intervalo da coleta
      </p>
    </div>
  ) : (
    <div className="no-breakdown">
      A plataforma ainda não retornou este detalhamento.
    </div>
  );
}
