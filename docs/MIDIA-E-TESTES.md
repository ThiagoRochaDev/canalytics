# Demonstração, mídia e validação

Entrega revisada em 7 de outubro de 2026. As imagens mostram o Canalytics 0.1.0 com **dados fictícios**, explicitamente identificados na interface.

## Temas e screenshots do repositório

O controle no topo alterna claro/escuro. Em Configurações, também é possível seguir o sistema. A preferência fica no navegador; não muda os dados do canal.

![Canalytics com os temas claro e escuro](images/themes.png)

| Tela | Screenshot |
| --- | --- |
| Analytics claro | [dashboard-light.jpg](images/dashboard-light.jpg) |
| Analytics escuro | [dashboard-dark.jpg](images/dashboard-dark.jpg) |
| Canais | [channels.jpg](images/channels.jpg) |
| Biblioteca | [contents.jpg](images/contents.jpg) |
| Conectores | [connectors.jpg](images/connectors.jpg) |
| Twitch | [twitch.jpg](images/twitch.jpg) |
| Celular claro | [mobile-light.jpg](images/mobile-light.jpg) |
| Celular escuro | [mobile-dark.jpg](images/mobile-dark.jpg) |

Os screenshots pertencem ao ambiente QA: quatro recursos TGR fictícios, histórico persistido em SQLite e respostas de plataforma simuladas. Não são dados de canais reais.

## Vídeos e material de divulgação

O pacote gerado está em output/media/index.html, com oito MP4 em output/media/videos. Os vídeos são **sequências legendadas de capturas reais dos fluxos testados**, sem áudio e sem gravação contínua do cursor. Não foram usadas telas inventadas ou imagens de IA.

1. Analytics: períodos, comparação, métrica, CSV e detalhamentos de público.
2. Conteúdos: busca, ordenação, detalhes e retenção simulada.
3. Canais: YouTube, Twitch, Discord, TikTok, lives e comunidades.
4. Conexões: configuração, permissão financeira opcional, fila e diálogo de remoção.
5. Organização: diário persistente e áreas de trabalho separadas.
6. Temas: claro, escuro, persistência e seguir o sistema.
7. Celular: dashboard, menu, conectores e temas.
8. Autenticação: logout, formulário e login da conta fictícia.

Há seis artes PNG de 1080 × 1350, vídeo de 30 segundos e texto para LinkedIn em output/media/linkedin. Os dois PDFs ficam em output/pdf. O material está anexado à [release v0.1.0](https://github.com/ThiagoRochaDev/canalytics/releases/tag/v0.1.0). Nenhuma postagem foi enviada ao LinkedIn.

output/ fica fora do versionamento para não incluir bancos, logs e arquivos privados de QA. Os screenshots sanitizados para documentação ficam em docs/images. O ZIP de divulgação inclui apenas mídia selecionada, CSV fictício, PDFs e a matriz de validação.

## Matriz de cobertura

| Funcionalidade | Interface | Automação/API | Limite |
| --- | --- | --- | --- |
| Períodos e comparação | Capturada; 7/28/custom e alternância de métrica | 3 testes de cálculo | Comparação precisa de intervalos completos |
| Tráfego, dispositivo, países e disponibilidade | Capturados | Normalização YouTube testada | Detalhamentos usam intervalo de coleta |
| Biblioteca e retenção | Busca, ordenação, detalhes e curva capturados | Rejeição de vídeo de outro recurso testada | Curva QA simulada |
| CSV | Botão documentado | Exportação autenticada: 180 registros; null e fórmula testados | Download pelo navegador não foi homologado |
| Múltiplos recursos | Quatro plataformas capturadas | Isolamento de áreas testado | Audiências não são somadas |
| Configuração | Credenciais fictícias salvas e formulário limpo | Criptografia e ausência de eco testadas | Nenhuma credencial real usada |
| OAuth e reautorização | Formulário/callback documentados | Estado, sessão, replay, expiração e histórico testados | Fluxo externo real não realizado |
| Sincronização | Fila e conclusão capturadas | Idempotência, erro sem tokens e exclusão em andamento testados | Coleta QA simulada |
| Remover conexão | Diálogo capturado e cancelado | Remoção local e isolamento testados | Sem revogação externa automática |
| Diário e áreas | Persistência após reload e projeto vazio capturados | Autorização e isolamento testados | Um administrador; sem convites |
| Temas e celular | Persistência; menu; largura sem overflow verificados | Build TypeScript passou | Preferência local ao navegador |
| Conta | Login/logout QA capturados | Cadastro inicial, sessão, CSRF e logout testados | Sem recuperação por e-mail |

## Resultados da execução local

- 14 testes Python passaram.
- 3 testes de cálculos TypeScript passaram.
- Build TypeScript/Vite de produção passou.
- Configuração Docker Compose válida.
- Engine Docker inativo: imagem não construída/executada nesta máquina.
- Sem testes de OAuth ou métricas em contas reais de provedores.
- Repositório público: [https://github.com/ThiagoRochaDev/canalytics](https://github.com/ThiagoRochaDev/canalytics); aplicação hospedada publicamente não foi implantada.

## Reproduzir o QA

Execute a partir da raiz, com as dependências do backend e o frontend compilado:

    .venv\Scripts\python.exe scripts\qa_server.py

Abra http://localhost:8094/qa/open. Esse endpoint e a conta de teste existem **somente nesse helper**, nunca no servidor de produção.

Cada execução cria um banco novo em output/qa. O helper substitui os coletores por fixtures em seu próprio processo; não chama APIs externas. Seu cookie é separado do servidor principal.

Não exponha ou implante o helper. Ele usa uma conta pública de teste e entrada facilitada para captura local. A aplicação normal deve iniciar por scripts/start.ps1 ou scripts/start.sh.

A conta fictícia é qa@canalytics.example, com senha canalytics-test-only-2026. Ela não é credencial de uma conta externa.

## Reproduzir os artefatos

As capturas e output/media/manifest.json são criadas durante a verificação de UI. Para usar as capturas desta entrega, baixe o ZIP da [release v0.1.0](https://github.com/ThiagoRochaDev/canalytics/releases/tag/v0.1.0) e extraia seu conteúdo dentro de output/. Depois:

    python scripts/build_media.py
    python scripts/build_pdfs.py
    python scripts/package_media.py

Requisitos de mídia: Pillow, ReportLab, pypdf, FFmpeg e fontes Segoe UI (Windows) ou DejaVu (Linux). A geração usa os screenshots locais e não acessa contas. Para revisar PDFs, renderize todas as páginas com Poppler. Os scripts não coletam screenshots por conta própria.
