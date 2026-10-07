import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  ChevronRight,
  Code2,
  ExternalLink,
  Film,
  Info,
  Layers3,
  LayoutDashboard,
  LoaderCircle,
  Menu,
  Plus,
  Plug,
  Radio,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Trash2,
  Users,
  X,
} from "lucide-react";
import type { Content, Dataset, Provider, Status } from "./types";
import { api, post } from "./api";
import { labelProvider } from "./analytics";
import {
  Badge,
  Brand,
  ChannelCards,
  ContentTable,
  Empty,
  Modal,
} from "./components";
import Dashboard from "./Dashboard";
import ConnectorDialog from "./ConnectorDialog";
import ContentDetail from "./ContentDetail";
import { useTheme, ThemeButton, ThemeSelect } from "./theme";
type Page =
  | "overview"
  | "channels"
  | "content"
  | "live"
  | "community"
  | "connections"
  | "settings";
const nav = [
  { id: "overview", label: "Visão geral", icon: LayoutDashboard },
  { id: "channels", label: "Meus canais", icon: Layers3 },
  { id: "content", label: "Conteúdos", icon: Film },
  { id: "live", label: "Ao vivo", icon: Radio },
  { id: "community", label: "Comunidades", icon: Users },
] as const;
const titles: Record<Page, [string, string]> = {
  overview: [
    "Uma visão clara do seu crescimento.",
    "Entenda os resultados. Encontre o próximo passo.",
  ],
  channels: [
    "Todos os seus canais. Um só lugar.",
    "Acompanhe cada plataforma com suas próprias métricas.",
  ],
  content: [
    "Conteúdo que conta uma história.",
    "Explore o desempenho acumulado das suas publicações.",
  ],
  live: [
    "Sua presença ao vivo.",
    "Acompanhe transmissões e a evolução das coletas.",
  ],
  community: [
    "Sua comunidade em movimento.",
    "Veja o tamanho e a presença dos seus servidores.",
  ],
  connections: [
    "Conecte seu universo.",
    "Autorize suas plataformas e mantenha os dados por perto.",
  ],
  settings: [
    "Seu espaço de criação.",
    "Gerencie sua instalação e suas áreas de trabalho.",
  ],
};
export default function App() {
  const theme = useTheme();
  const [status, setStatus] = useState<Status | null>(null),
    [data, setData] = useState<Dataset | null>(null);
  const [workspace, setWorkspace] = useState(""),
    [demo, setDemo] = useState(true),
    [page, setPage] = useState<Page>("overview"),
    [rid, setRid] = useState("");
  const [error, setError] = useState(""),
    [toast, setToast] = useState(""),
    [busy, setBusy] = useState(false),
    [mobile, setMobile] = useState(false);
  const [modal, setModal] = useState<
      "auth" | "provider" | "content" | "workspace" | "remove" | null
    >(null),
    [provider, setProvider] = useState<Provider | null>(null),
    [content, setContent] = useState<Content | null>(null),
    [removeId, setRemoveId] = useState("");
  const [configured, setConfigured] = useState<string[]>([]),
    [search, setSearch] = useState(""),
    [sort, setSort] = useState("views"),
    [revision, setRevision] = useState(0);
  const refresh = () => setRevision((v) => v + 1);
  const notify = (text: string) => setToast(text);
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(""), 6500);
      return () => clearTimeout(timer);
    }
  }, [toast]);
  useEffect(() => {
    api<Status>("/status")
      .then((s) => {
        setStatus(s);
        if (s.user) {
          setDemo(false);
          setWorkspace(s.workspaces[0]?.id || "");
        }
      })
      .catch((e) => setError(e.message));
    const result = new URLSearchParams(location.search).get("oauth");
    if (result) {
      notify(
        result === "connected"
          ? "Conta autorizada. A primeira coleta está na fila."
          : result === "cancelled"
            ? "Autorização cancelada."
            : "A plataforma não concluiu a autorização. Confira o aplicativo e tente novamente.",
      );
      history.replaceState(null, "", location.pathname);
      setPage("connections");
    }
  }, []);
  useEffect(() => {
    if (!status || (!demo && !workspace)) return;
    const controller = new AbortController();
    setError("");
    setData(null);
    const load = () =>
      api<Dataset>(
        demo ? "/demo" : "/data",
        { signal: controller.signal },
        workspace,
      )
        .then(setData)
        .catch((e) => {
          if (e.name !== "AbortError") setError(e.message);
        });
    load();
    const timer = setInterval(load, 20000);
    return () => {
      controller.abort();
      clearInterval(timer);
    };
  }, [status?.user?.id, demo, workspace, revision, status?.setup_required]);
  useEffect(() => {
    if (!status?.user || !workspace) return;
    api<{ configured: string[] }>("/apps", {}, workspace)
      .then((v) => setConfigured(v.configured))
      .catch(() => setConfigured([]));
  }, [status?.user?.id, workspace, revision]);
  const r =
    data?.resources.find((item) => item.id === rid) || data?.resources[0];
  const items =
    data?.contents
      .filter(
        (c) => !search || c.title.toLowerCase().includes(search.toLowerCase()),
      )
      .sort((a, b) =>
        sort === "published"
          ? b.published.localeCompare(a.published)
          : (b.views ?? -1) - (a.views ?? -1),
      ) || [];
  function navigate(next: Page) {
    setPage(next);
    setSearch("");
    setMobile(false);
  }
  function openResource(id: string) {
    setRid(id);
    setPage("overview");
  }
  function openContent(c: Content) {
    setContent(c);
    setModal("content");
  }
  async function action(fn: () => Promise<void>) {
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      notify(e instanceof Error ? e.message : "Ocorreu um erro.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="shell">
      <aside className={"sidebar " + (mobile ? "show" : "")}>
        <Brand />
        <div className="workspace-box">
          <div className="workspace-icon">T</div>
          <div>
            <small>ÁREA DE TRABALHO</small>
            {status?.user && !demo ? (
              <select
                aria-label="Área de trabalho"
                value={workspace}
                onChange={(e) => {
                  setWorkspace(e.target.value);
                  setRid("");
                }}
              >
                {status.workspaces.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            ) : (
              <strong>Estúdio de demonstração</strong>
            )}
          </div>
        </div>
        <span className="nav-caption">SEU ESTÚDIO</span>
        <nav>
          {nav.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={"nav-item " + (page === id ? "active" : "")}
              onClick={() => navigate(id)}
            >
              <Icon size={19} />
              {label}
              {id === "channels" && data && (
                <span className="nav-count">{data.resources.length}</span>
              )}
            </button>
          ))}
        </nav>
        <span className="nav-caption nav-spacer">GERENCIAR</span>
        <nav>
          <button
            className={"nav-item " + (page === "connections" ? "active" : "")}
            onClick={() => navigate("connections")}
          >
            <Plug size={19} />
            Conexões
          </button>
          <button
            className={"nav-item " + (page === "settings" ? "active" : "")}
            onClick={() => navigate("settings")}
          >
            <Settings2 size={19} />
            Configurações
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="open-source">
            <Code2 size={19} />
            <div>
              <strong>Aberto por natureza.</strong>
              <p>Seus canais. Seus dados.</p>
              <span>Apache-2.0 · v0.1.0</span>
            </div>
          </div>
          <button
            className="profile"
            onClick={() =>
              status?.user ? navigate("settings") : setModal("auth")
            }
          >
            <span className="user-avatar">
              {status?.user?.name.slice(0, 1) || "C"}
            </span>
            <span>
              <strong>{status?.user?.name || "Seu próximo capítulo"}</strong>
              <small>
                {status?.user ? "Instalação própria" : "Configure seu estúdio"}
              </small>
            </span>
            <ChevronRight size={16} />
          </button>
        </div>
      </aside>
      {mobile && (
        <button
          className="mobile-backdrop"
          aria-label="Fechar menu"
          onClick={() => setMobile(false)}
        />
      )}
      <div className="main">
        <header className="topbar">
          <div className="crumb">
            <button
              className="icon-btn mobile-menu"
              aria-label="Abrir menu"
              onClick={() => setMobile(true)}
            >
              <Menu size={22} />
            </button>
            <span>Seu estúdio</span>
            <ChevronRight size={14} />
            <strong>
              {nav.find((s) => s.id === page)?.label ||
                (page === "connections" ? "Conexões" : "Configurações")}
            </strong>
          </div>
          <div className="top-actions">
            <ThemeButton
              resolved={theme.resolved}
              onChange={theme.setPreference}
            />
            <span className="local-status">
              <span /> Instalação própria
            </span>
            <button
              className="btn small-btn"
              onClick={() => navigate("connections")}
            >
              <Plus size={16} />
              Conectar canal
            </button>
          </div>
        </header>
        <main>
          {status?.testing && (
            <div className="qa-banner">
              <ShieldCheck size={16} />
              <strong>Ambiente QA</strong>
              <span>
                Dados fictícios persistidos para testes. Integrações e
                sincronizações simuladas.
              </span>
            </div>
          )}
          {demo && (
            <div className="demo-banner">
              <span>
                <Sparkles size={16} />
                <strong>Explore o Canalytics</strong>
                <span>Você está vendo dados fictícios de demonstração.</span>
              </span>
              <button
                onClick={() =>
                  status?.user ? setDemo(false) : setModal("auth")
                }
              >
                {status?.user ? "Voltar aos meus dados" : "Criar meu estúdio"}
                <ArrowUpRight size={15} />
              </button>
            </div>
          )}
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                {page === "overview"
                  ? "SEU CONTEÚDO, EM PERSPECTIVA"
                  : "CANALYTICS / " +
                    (page === "connections"
                      ? "CONEXÕES"
                      : page === "settings"
                        ? "CONFIGURAÇÕES"
                        : "ESTÚDIO")}
              </div>
              <h1>{titles[page][0]}</h1>
              <p>{titles[page][1]}</p>
            </div>
          </div>
          {error && (
            <div className="alert" role="alert">
              {error}
              <button
                className="text-btn"
                onClick={() => {
                  if (!status) location.reload();
                  else refresh();
                }}
              >
                Tentar novamente
              </button>
            </div>
          )}
          {!status || (!data && !error) ? (
            <div className="loading">
              <LoaderCircle className="spin" />
              Carregando seu estúdio…
            </div>
          ) : null}
          {data &&
            page === "overview" &&
            (r ? (
              <Dashboard
                key={r.id}
                data={data}
                r={r}
                workspace={workspace}
                onSelect={setRid}
                onContent={openContent}
                onLibrary={() => navigate("content")}
                notify={notify}
                refresh={refresh}
              />
            ) : (
              <div className="card">
                <Empty
                  title="Seu próximo capítulo começa aqui."
                  action={
                    <button
                      className="btn primary"
                      onClick={() => navigate("connections")}
                    >
                      <Plus size={17} />
                      Conectar primeiro canal
                    </button>
                  }
                >
                  Conecte uma conta para importar o histórico disponível e
                  acompanhar suas próximas conquistas.
                </Empty>
              </div>
            ))}
          {data &&
            (page === "channels" ||
              page === "live" ||
              page === "community") && (
              <>
                <ChannelCards
                  items={data.resources.filter(
                    (item) =>
                      page === "channels" ||
                      item.kind === (page === "live" ? "stream" : "community"),
                  )}
                  demo={demo}
                  onOpen={openResource}
                />
                {!data.resources.some(
                  (item) =>
                    page === "channels" ||
                    item.kind === (page === "live" ? "stream" : "community"),
                ) && (
                  <div className="card">
                    <Empty
                      title="Comece conectando uma plataforma"
                      action={
                        <button
                          className="btn primary"
                          onClick={() => navigate("connections")}
                        >
                          Explorar conectores
                        </button>
                      }
                    >
                      As métricas aparecerão aqui depois da primeira
                      sincronização.
                    </Empty>
                  </div>
                )}
                {page !== "channels" && (
                  <div className="info-box">
                    <Info size={18} />
                    <p>
                      {page === "live"
                        ? "O estado da transmissão reflete a última coleta. Espectadores simultâneos são amostras, não audiência única nem média oficial da live."
                        : "Membros e presença são contagens aproximadas da plataforma. Esta versão não lê mensagens nem executa moderação."}
                    </p>
                  </div>
                )}
              </>
            )}
          {data && page === "content" && (
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>
                    Biblioteca de conteúdos{" "}
                    <span className="count">{items.length}</span>
                  </h2>
                  <p>
                    Contadores acumulados por publicação, sem somar plataformas.
                  </p>
                </div>
                <div className="table-controls">
                  <label className="search">
                    <Search size={16} />
                    <input
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Buscar conteúdo"
                      aria-label="Buscar conteúdo"
                    />
                  </label>
                  <select
                    aria-label="Ordenação"
                    value={sort}
                    onChange={(e) => setSort(e.target.value)}
                  >
                    <option value="views">Mais vistos</option>
                    <option value="published">Mais recentes</option>
                  </select>
                </div>
              </div>
              <ContentTable items={items} data={data} onOpen={openContent} />
            </section>
          )}
          {status && page === "connections" && (
            <>
              <div className="connection-intro">
                <div>
                  <Plug size={23} />
                  <strong>Uma conexão. Mais contexto.</strong>
                  <p>
                    Cadastre o aplicativo da plataforma e autorize cada conta.
                    Você pode conectar mais de uma conta por serviço.
                  </p>
                </div>
                <Badge tone="green">
                  <ShieldCheck size={13} />
                  Credenciais criptografadas
                </Badge>
              </div>
              <div className="connector-grid">
                {status.catalog.map((p) => (
                  <article className="card connector" key={p.id}>
                    <div className="between">
                      <span
                        className="provider-logo"
                        style={{ color: p.color, background: p.color + "12" }}
                      >
                        {p.name.slice(0, 2)}
                      </span>
                      <Badge tone={p.status === "implemented" ? "green" : ""}>
                        {p.status === "implemented"
                          ? "Implementado"
                          : p.status === "experimental"
                            ? "Experimental"
                            : "Planejado"}
                      </Badge>
                    </div>
                    <h2>{p.name}</h2>
                    <p>{p.description}</p>
                    <div className="capabilities">
                      {p.capabilities.map((c) => (
                        <span key={c}>{c}</span>
                      ))}
                    </div>
                    <button
                      className="btn full"
                      disabled={p.status === "planned"}
                      onClick={() => {
                        setProvider(p);
                        setModal("provider");
                      }}
                    >
                      {configured.includes(p.id) && !demo
                        ? "Conectar outra conta"
                        : "Configurar conexão"}
                      {p.status !== "planned" && <Plus size={16} />}
                    </button>
                  </article>
                ))}
              </div>
              <section className="card">
                <div className="card-heading">
                  <div>
                    <h2>Contas conectadas</h2>
                    <p>Sincronização, permissões e histórico de execução.</p>
                  </div>
                  <button
                    className="icon-btn"
                    aria-label="Atualizar conexões"
                    onClick={refresh}
                  >
                    <RefreshCw size={17} />
                  </button>
                </div>
                {!data?.connections.length ? (
                  <Empty
                    title={
                      demo
                        ? "Conexões reais aparecem aqui"
                        : "Nenhuma conta conectada"
                    }
                  >
                    {demo
                      ? "Saia da demonstração para configurar suas credenciais."
                      : "Escolha uma plataforma acima para iniciar."}
                  </Empty>
                ) : (
                  data.connections.map((c) => (
                    <div className="connection-row" key={c.id}>
                      <div>
                        <strong>{labelProvider(c.provider)}</strong>
                        <p>
                          {c.last_sync
                            ? "Última coleta: " +
                              new Date(c.last_sync).toLocaleString("pt-BR")
                            : "Aguardando primeira coleta"}
                        </p>
                        {c.error && <p className="negative">{c.error}</p>}
                        <small>
                          {data.jobs.find((j) => j.connection_id === c.id)
                            ?.status === "running"
                            ? "Sincronizando…"
                            : data.jobs.find((j) => j.connection_id === c.id)
                                  ?.status === "pending"
                              ? "Na fila"
                              : c.status === "error"
                                ? "Precisa de atenção"
                                : "Ativa"}
                        </small>
                      </div>
                      <div className="row-actions">
                        <button
                          className="btn"
                          disabled={busy}
                          onClick={() =>
                            action(async () => {
                              const result = await api<{ url: string }>(
                                "/oauth/" + c.provider + "/start",
                                post({ connection_id: c.id }),
                                workspace,
                              );
                              location.assign(result.url);
                            })
                          }
                        >
                          Reautorizar
                        </button>
                        <button
                          className="btn"
                          disabled={busy}
                          onClick={() =>
                            action(async () => {
                              await api(
                                "/connections/" + c.id + "/sync",
                                post({}),
                                workspace,
                              );
                              notify("Coleta adicionada à fila.");
                              refresh();
                            })
                          }
                        >
                          <RefreshCw size={15} />
                          Sincronizar
                        </button>
                        <button
                          className="icon-btn danger"
                          aria-label="Desconectar conta"
                          onClick={() => {
                            setRemoveId(c.id);
                            setModal("remove");
                          }}
                        >
                          <Trash2 size={17} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </section>
            </>
          )}
          {status && page === "settings" && (
            <div className="settings-grid">
              <section className="card">
                <div className="card-heading">
                  <div>
                    <h2>Sua instalação</h2>
                    <p>Controle local, código aberto e dados portáteis.</p>
                  </div>
                  <Code2 size={20} />
                </div>
                <div className="detail-list">
                  <div>
                    <span>Versão</span>
                    <strong>{status.version} · prévia</strong>
                  </div>
                  <div>
                    <span>Licença</span>
                    <a
                      href="https://www.apache.org/licenses/LICENSE-2.0"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Apache-2.0 <ExternalLink size={12} />
                    </a>
                  </div>
                  <div>
                    <span>Armazenamento</span>
                    <strong>SQLite no servidor</strong>
                  </div>
                  <div>
                    <span>Conta</span>
                    <strong>{status.user?.email || "Demonstração"}</strong>
                  </div>
                </div>
                <ThemeSelect
                  value={theme.preference}
                  onChange={theme.setPreference}
                />
                <div className="settings-actions">
                  {status.user ? (
                    <>
                      <button
                        className="btn"
                        onClick={() => setDemo((v) => !v)}
                      >
                        {demo ? "Ver meus dados" : "Explorar demonstração"}
                      </button>
                      <button
                        className="btn"
                        onClick={() =>
                          action(async () => {
                            await api("/logout", post({}));
                            setStatus(await api<Status>("/status"));
                            setDemo(true);
                            setWorkspace("");
                            setData(null);
                          })
                        }
                      >
                        Sair da conta
                      </button>
                    </>
                  ) : (
                    <button
                      className="btn primary"
                      onClick={() => setModal("auth")}
                    >
                      {status.setup_required ? "Criar administrador" : "Entrar"}
                    </button>
                  )}
                </div>
              </section>
              <section className="card">
                <div className="card-heading">
                  <div>
                    <h2>Áreas de trabalho</h2>
                    <p>Separe os projetos e canais de cada operação.</p>
                  </div>
                  <Layers3 size={20} />
                </div>
                <div className="workspace-list">
                  {status.workspaces.map((w) => (
                    <div key={w.id}>
                      <strong>{w.name}</strong>
                      <Badge>Responsável</Badge>
                    </div>
                  ))}
                </div>
                <div className="settings-actions">
                  <button
                    className="btn"
                    onClick={() =>
                      status.user ? setModal("workspace") : setModal("auth")
                    }
                  >
                    <Plus size={16} />
                    Nova área
                  </button>
                </div>
              </section>
              <div className="info-box">
                <Info size={20} />
                <p>
                  Esta prévia atende instalações com um administrador. Convites
                  de equipe, cobrança, publicação e moderação ficam para versões
                  futuras. Cada conector informa as métricas que realmente
                  consegue fornecer.
                </p>
              </div>
            </div>
          )}
          <footer>
            <span>
              <span className="footer-dot" /> Canalytics · feito para quem cria
            </span>
            <span>Open source. Seu estúdio, suas possibilidades.</span>
          </footer>
        </main>
      </div>
      <Modal
        open={modal === "auth"}
        onClose={() => setModal(null)}
        title={
          status?.setup_required ? "Crie seu estúdio" : "Bem-vindo de volta"
        }
        description={
          status?.setup_required
            ? "A primeira conta será a administradora desta instalação."
            : "Entre para acessar seus canais e conexões."
        }
      >
        <form
          className="form"
          onSubmit={(e) => {
            e.preventDefault();
            const values = Object.fromEntries(new FormData(e.currentTarget));
            action(async () => {
              await api(
                status?.setup_required ? "/setup" : "/login",
                post(values),
              );
              const s = await api<Status>("/status");
              setStatus(s);
              setWorkspace(s.workspaces[0]?.id || "");
              setDemo(false);
              setModal(null);
              notify(
                "Seu estúdio está pronto. Conecte uma plataforma para começar.",
              );
              setPage("connections");
            });
          }}
        >
          {status?.setup_required && (
            <>
              <label>
                Seu nome
                <input
                  name="name"
                  autoComplete="name"
                  required
                  maxLength={80}
                />
              </label>
              <label>
                Nome da área de trabalho
                <input
                  name="workspace"
                  defaultValue="Meu estúdio"
                  required
                  maxLength={80}
                />
              </label>
            </>
          )}
          <label>
            E-mail
            <input type="email" name="email" autoComplete="username" required />
          </label>
          <label>
            Senha
            <input
              type="password"
              name="password"
              autoComplete={
                status?.setup_required ? "new-password" : "current-password"
              }
              minLength={status?.setup_required ? 12 : 1}
              maxLength={200}
              required
            />
            {status?.setup_required && (
              <small>Use pelo menos 12 caracteres.</small>
            )}
          </label>
          <button className="btn primary full" disabled={busy}>
            {busy && <LoaderCircle className="spin" size={16} />}{" "}
            {status?.setup_required ? "Criar meu estúdio" : "Entrar"}
          </button>
        </form>
      </Modal>
      <Modal
        open={modal === "provider"}
        onClose={() => {
          setModal(null);
          refresh();
        }}
        title={"Conectar " + (provider?.name || "")}
        description="Autorize apenas os dados que deseja acompanhar."
      >
        {provider && status && (
          <ConnectorDialog
            key={provider.id}
            provider={provider}
            status={status}
            demo={demo}
            workspace={workspace}
            configured={configured.includes(provider.id)}
            notify={notify}
            onReady={() => {
              if (status.user) {
                setDemo(false);
                setModal(null);
              } else setModal("auth");
            }}
          />
        )}
      </Modal>
      <Modal
        open={modal === "content"}
        onClose={() => setModal(null)}
        title={content?.title || "Conteúdo"}
        description="Os contadores abaixo são acumulados desde a publicação."
      >
        {content && data && (
          <ContentDetail
            key={content.id}
            content={content}
            data={data}
            workspace={workspace}
            notify={notify}
          />
        )}
      </Modal>
      <Modal
        open={modal === "workspace"}
        onClose={() => setModal(null)}
        title="Nova área de trabalho"
        description="Os canais e credenciais ficam separados por área."
      >
        <form
          className="form"
          onSubmit={(e) => {
            e.preventDefault();
            const name = new FormData(e.currentTarget).get("name");
            action(async () => {
              const w = await api<{ id: string }>(
                "/workspaces",
                post({ name }),
              );
              setStatus(await api<Status>("/status"));
              setWorkspace(w.id);
              setDemo(false);
              setModal(null);
              setPage("connections");
            });
          }}
        >
          <label>
            Nome
            <input name="name" required maxLength={80} />
          </label>
          <button className="btn primary" disabled={busy}>
            Criar área
          </button>
        </form>
      </Modal>
      <Modal
        open={modal === "remove"}
        onClose={() => setModal(null)}
        title="Desconectar esta conta?"
        description="Esta ação remove as credenciais, métricas e anotações desta conexão no Canalytics."
      >
        <div className="form">
          <p>
            Para revogar a autorização na origem, remova também o acesso nas
            configurações da plataforma.
          </p>
          <button
            className="btn danger-solid"
            disabled={busy}
            onClick={() =>
              action(async () => {
                const result = await api<{ message: string }>(
                  "/connections/" + removeId,
                  { method: "DELETE" },
                  workspace,
                );
                setModal(null);
                notify(result.message);
                refresh();
              })
            }
          >
            Desconectar e remover dados locais
          </button>
        </div>
      </Modal>
      {toast && (
        <div className="toast" role="status">
          <Info size={18} />
          <span>{toast}</span>
          <button
            className="icon-btn"
            aria-label="Fechar aviso"
            onClick={() => setToast("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
