import type { ReactNode } from "react";
import { Dialog } from "radix-ui";
import {
  ArrowUpRight,
  BarChart3,
  ChevronRight,
  Eye,
  Play,
  ShieldCheck,
  X,
} from "lucide-react";
import type { Content, Dataset, Resource } from "./types";
import { fmt, labelProvider, shortDate } from "./analytics";
export function Brand() {
  return (
    <div className="brand">
      <span className="brand-mark">
        <Play size={19} fill="currentColor" />
      </span>
      canalytics<span className="brand-dot">.</span>
    </div>
  );
}
export function Avatar({
  r,
  small = false,
}: {
  r: Pick<Resource, "color" | "initials">;
  small?: boolean;
}) {
  return (
    <span
      className={"avatar " + (small ? "small" : "")}
      style={{ background: r.color + "15", color: r.color }}
    >
      {r.initials}
    </span>
  );
}
export function Empty({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <BarChart3 size={28} />
      </span>
      <h3>{title}</h3>
      <p>{children}</p>
      {action}
    </div>
  );
}
export function Badge({
  children,
  tone = "",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
export function Stat({
  label,
  value,
  delta,
  icon: Icon,
  detail,
}: {
  label: string;
  value: string;
  delta?: number | null;
  icon: typeof Eye;
  detail?: string;
}) {
  return (
    <article className="stat">
      <div className="stat-label">
        {label}
        <Icon size={17} />
      </div>
      <strong>{value}</strong>
      <div className="stat-footer">
        {delta != null ? (
          <>
            <span className={delta >= 0 ? "positive" : "negative"}>
              {delta >= 0 ? "+" : ""}
              {delta.toFixed(1).replace(".", ",")}%
            </span>
            <span>vs. período anterior</span>
          </>
        ) : (
          <span>{detail || "Comparação indisponível"}</span>
        )}
      </div>
    </article>
  );
}
export function Source({ r, demo }: { r: Resource; demo: boolean }) {
  return (
    <div className="source">
      <ShieldCheck size={14} />
      <span>
        {demo ? "Demonstração · dados fictícios" : r.source}
        {r.last_sync ? " · Coleta em " + shortDate(r.last_sync) : ""}
      </span>
    </div>
  );
}
export function Modal({
  open,
  onClose,
  title,
  description,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={(v) => !v && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="overlay" />
        <Dialog.Content className="modal">
          <Dialog.Title>{title}</Dialog.Title>
          <Dialog.Description>{description}</Dialog.Description>
          <Dialog.Close className="icon-btn modal-close" aria-label="Fechar">
            <X size={20} />
          </Dialog.Close>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
export function ContentTable({
  items,
  data,
  onOpen,
}: {
  items: Content[];
  data: Dataset;
  onOpen: (c: Content) => void;
}) {
  return items.length ? (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Conteúdo</th>
            <th>Visualizações</th>
            <th>Curtidas</th>
            <th>Comentários</th>
            <th>Publicado</th>
            <th>
              <span className="sr-only">Detalhes</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((c) => (
            <tr key={c.resource_id + c.id}>
              <td>
                <button className="content-title" onClick={() => onOpen(c)}>
                  <span className="video-art">
                    <Play size={17} />
                  </span>
                  <span>
                    {c.title}
                    <small>
                      {labelProvider(
                        data.resources.find((r) => r.id === c.resource_id)
                          ?.provider || "",
                      )}{" "}
                      · Total acumulado
                    </small>
                  </span>
                </button>
              </td>
              <td>{fmt(c.views)}</td>
              <td>{fmt(c.likes)}</td>
              <td>{fmt(c.comments)}</td>
              <td className="muted">{shortDate(c.published)}</td>
              <td>
                <button
                  className="icon-btn"
                  aria-label={"Abrir " + c.title}
                  onClick={() => onOpen(c)}
                >
                  <ChevronRight size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ) : (
    <Empty title="Nenhum conteúdo por aqui">
      Os conteúdos disponíveis aparecerão após a sincronização.
    </Empty>
  );
}
export function ChannelCards({
  items,
  demo,
  onOpen,
}: {
  items: Resource[];
  demo: boolean;
  onOpen: (id: string) => void;
}) {
  return (
    <div className="channel-grid">
      {items.map((r) => (
        <article className="card channel-card" key={r.id}>
          <div className="between">
            <Avatar r={r} />
            <Badge>{labelProvider(r.provider)}</Badge>
          </div>
          <h3>{r.name}</h3>
          <p>
            {r.kind === "community"
              ? "Comunidade"
              : r.kind === "stream"
                ? "Canal de transmissão"
                : "Canal de conteúdo"}
          </p>
          <div className="channel-numbers">
            <div>
              <strong>{fmt(r.followers)}</strong>
              <span>{r.followers_label || "Seguidores / inscritos"}</span>
            </div>
            <div>
              <strong>{fmt(r.content_count)}</strong>
              <span>
                {r.kind === "community" ? "Canais" : "Itens retornados"}
              </span>
            </div>
          </div>
          <Source r={r} demo={demo} />
          <button className="btn full" onClick={() => onOpen(r.id)}>
            Explorar métricas <ArrowUpRight size={15} />
          </button>
        </article>
      ))}
    </div>
  );
}
export function safeUrl(url: string) {
  try {
    return new URL(url).protocol === "https:" ? url : undefined;
  } catch {
    return undefined;
  }
}
