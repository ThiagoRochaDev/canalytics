import { useState } from "react";
import { ArrowUpRight, ExternalLink, Info, LoaderCircle } from "lucide-react";
import type { Provider, Status } from "./types";
import { api, post } from "./api";
export default function ConnectorDialog({
  provider: p,
  status,
  demo,
  workspace,
  configured,
  onReady,
  notify,
}: {
  provider: Provider;
  status: Status;
  demo: boolean;
  workspace: string;
  configured: boolean;
  onReady: () => void;
  notify: (s: string) => void;
}) {
  const [saved, setSaved] = useState(configured),
    [busy, setBusy] = useState(false);
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
  if (!status.user || demo)
    return (
      <div className="form">
        <p>
          Configure sua instalação para autorizar contas reais. A demonstração
          usa somente dados fictícios.
        </p>
        <button className="btn primary" onClick={onReady}>
          {status.user ? "Voltar aos meus dados" : "Configurar meu estúdio"}
        </button>
      </div>
    );
  return (
    <div className="form">
      <div className="info-box">
        <Info size={17} />
        <p>{p.limitations}</p>
      </div>
      <a className="text-btn" href={p.docs} target="_blank" rel="noreferrer">
        Documentação oficial <ExternalLink size={14} />
      </a>
      <label>
        URL de redirecionamento
        <input
          readOnly
          value={status.public_url + "/api/oauth/" + p.id + "/callback"}
          onFocus={(e) => e.target.select()}
        />
        <small>Cadastre exatamente esta URL no aplicativo da plataforma.</small>
      </label>
      <form
        className="form compact"
        onSubmit={(e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const values = Object.fromEntries(new FormData(form));
          run(async () => {
            await api("/apps/" + p.id, post(values), workspace);
            setSaved(true);
            form.reset();
            notify("Credenciais salvas. Agora autorize sua conta.");
          });
        }}
      >
        {p.fields.map((f) => (
          <label key={f}>
            {f === "client_id"
              ? p.id === "tiktok"
                ? "Client Key"
                : "Client ID"
              : f === "bot_token"
                ? "Bot token"
                : "Client secret"}
            <input
              name={f}
              type={f === "client_id" ? "text" : "password"}
              autoComplete="off"
              required
            />
          </label>
        ))}
        <button className="btn full" disabled={busy}>
          {saved ? "Salvar novas credenciais" : "Salvar credenciais"}
        </button>
      </form>
      <form
        className="form compact"
        onSubmit={(e) => {
          e.preventDefault();
          const monetary =
            new FormData(e.currentTarget).get("monetary") === "on";
          run(async () => {
            const result = await api<{ url: string }>(
              "/oauth/" + p.id + "/start",
              post({ monetary }),
              workspace,
            );
            location.assign(result.url);
          });
        }}
      >
        {p.id === "youtube" && (
          <label className="check-label">
            <input type="checkbox" name="monetary" />
            Solicitar também dados de receita
          </label>
        )}
        <button className="btn primary full" disabled={!saved || busy}>
          {busy ? <LoaderCircle className="spin" size={16} /> : null}Autorizar
          na plataforma <ArrowUpRight size={16} />
        </button>
      </form>
    </div>
  );
}
