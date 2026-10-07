# Arquitetura da prévia 0.1.0

## Organização

- apps/web: React 19 + TypeScript + Vite, gráficos Recharts, diálogos Radix e estilos responsivos.
- apps/api/canalytics/main.py: FastAPI, sessões, áreas, OAuth, exportação e arquivos estáticos.
- store.py: SQLite com WAL, transações, escopo por área e criptografia Fernet.
- oauth.py: fluxos oficiais e renovação de tokens serializada.
- worker.py: fila persistida, recuperação após reinício, tentativas limitadas e agendamento.
- connectors/: adaptadores independentes; nenhum scraping ou senha da plataforma.
- demo.py: fixture determinística fictícia, servida em endpoint separado.
- tests/: autorização, isolamento, cache, OAuth, conectores e falhas.
- docs/: decisões, escopo e operação.

## Caminho de uma coleta

Autorização → credenciais criptografadas → conexão → job persistido → conector → normalização → transação SQLite → painel por recurso.

O worker usa uma thread para consultas bloqueantes e mantém a API disponível. Um índice único permite apenas um job pendente/em execução por conexão. O agendador volta a jobs interrompidos e usa intervalos de 24 h (YouTube/TikTok), 15 min (Twitch) e 1 h (Discord). Erros transitórios têm até três tentativas por job; a conexão segue no agendamento com intervalo de recuperação.

**Execute um único processo Uvicorn nesta versão.** Escala horizontal exige fila externa, locks distribuídos e migrações de banco; o SQLite local não é apresentado como infraestrutura SaaS multiworker.

## Modelo de dados

Usuários → membros → áreas de trabalho → aplicativos OAuth versionados → conexões → recursos.

Por recurso são persistidos relatórios diários, snapshots, catálogo acumulado, detalhamentos e notas. Fonte, intervalo consultado e última coleta acompanham os dados. O catálogo é uma janela recente documentada, não arquivo integral de todos os conteúdos publicados.

Tokens não entram no frontend. Uma configuração nova do aplicativo gera uma versão; conexões existentes continuam referindo a configuração original até reautorização. A chave local nunca é enviada pelo servidor.

## Contrato de conectores

Connector.pull(credentials, app) retorna:

- resources: recursos autorizados com external_id, nome, modo e capabilities.
- daily: medições por dia, com fonte e significado definidos.
- snapshot: contagem observada naquele instante, quando aplicável.
- contents: catálogo com métricas lifetime.
- breakdowns: dimensões com intervalo e unidade.
- interval: período diário substituído atomicamente para aceitar correções do provedor.
- warnings e sync_seconds: cobertura e frequência de atualização.

Na versão atual, cada conexão administra um recurso. Para suportar vários recursos em uma única coleta, o contrato deve passar a relacionar cada série a seu external_id explicitamente.

Novos adaptadores nativos entram no registro CONNECTORS e no CATALOG. Há descoberta opcional de coletores Python instalados pelo operador via entry point canalytics.connectors. **Isso ainda não é um marketplace plug-and-play:** novos provedores também precisam integrar seus fluxos ao módulo OAuth e ao catálogo. O operador só deve instalar código de confiança; não existe execução de plugins enviados pela interface.

## O que significa “melhor analytics”

O diferencial planejado é contexto, profundidade e fluxo de trabalho: múltiplas contas, anotações, evolução, comparação válida e dados portáteis. A ferramenta não afirma possuir métricas privadas que a plataforma não fornece nem apresenta inferências como relatórios oficiais.

Nesta prévia:
- Somente séries do mesmo canal são comparadas.
- Dias ausentes permanecem ausentes.
- Receita ausente é nula.
- Saldo de inscritos usa ganhos menos perdas retornados pelo próprio provedor.
- Não são calculados escores opacos, sobreposição de público ou previsões.
- Detalhamentos de público usam o intervalo fixo da coleta, mostrado em cada card.
- A UI não classifica um vídeo como Shorts apenas pela duração.

## Próximas decisões

PostgreSQL/filas para serviço gerenciado, migrações versionadas, convites/RBAC de equipe, políticas de retenção por plataforma, atualização de períodos históricos, contrato OAuth extensível, relatórios por vídeo/período e Reporting API.
