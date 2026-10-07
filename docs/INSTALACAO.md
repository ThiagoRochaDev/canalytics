# Instalação e conectores

## Endereço e persistência

CANALYTICS_PUBLIC_URL deve ser a origem exata, sem subcaminho: http://localhost:8093 em desenvolvimento ou https://analytics.seudominio.example em servidor.

O cookie é HttpOnly/SameSite=Lax e Secure quando a origem é HTTPS. O callback OAuth precisa receber a mesma sessão que iniciou o fluxo. Não misture localhost e 127.0.0.1 no navegador. Em desenvolvimento, o login em localhost:5178 compartilha o host com o callback localhost:8093.

CANALYTICS_DATA_DIR define o diretório do SQLite e de secrets.key. A execução local usa ./data e o Docker usa /data. Faça backup consistente do diretório com o serviço parado e proteja a cópia. Sem secrets.key os tokens não podem ser descriptografados. O sistema não oferece redefinição de senha por e-mail nesta prévia.

## Google / YouTube

Crie um OAuth Client do tipo web no seu projeto Google. Ative YouTube Data API v3 e YouTube Analytics API. Configure a tela de consentimento e usuários de teste quando aplicável.

Callback: /api/oauth/youtube/callback na origem configurada.

Escopos de leitura: youtube.readonly e yt-analytics.readonly. O checkbox de receita acrescenta yt-analytics-monetary.readonly. O escopo financeiro é opcional e não garante elegibilidade ou dados monetizados.

Cada autorização usa o canal selecionado no fluxo Google/YouTube. Repita para outras contas e Brand Accounts. Papéis delegados no Studio não devem ser presumidos como acesso pela API.

Consulta diária de 180 dias e catálogo de até 500 vídeos. Tráfego, países e dispositivos são consultas separadas. A retenção é buscada sob demanda para vídeo pertencente ao catálogo daquele canal. Impressões e CTR via Reporting API não estão implementados.

Referências: [OAuth do YouTube](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps), [métricas](https://developers.google.com/youtube/analytics/metrics), [relatórios](https://developers.google.com/youtube/analytics/channel_reports).

## Twitch

Cadastre o aplicativo no console de desenvolvedores e use /api/oauth/twitch/callback.

O fluxo solicita moderator:read:followers, usa o token do usuário e valida a autorização antes das coletas. Lê perfil, transmissão atual, seguidores e até 100 VODs. A consulta de seguidores pode ficar indisponível por permissão; isso é mostrado como aviso.

São snapshots a cada 15 minutos, enquanto o serviço está ativo. Não equivalem aos relatórios financeiros, à audiência única nem à média oficial de toda a transmissão.

Referências: [OAuth](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/), [validação de tokens](https://dev.twitch.tv/docs/authentication/validate-tokens/), [Helix](https://dev.twitch.tv/docs/api/reference/).

## Discord — experimental

Crie um aplicativo e seu bot. Configure /api/oauth/discord/callback. Guarde Client ID, Client Secret e Bot Token na tela de conexão.

Escopos identify, guilds e bot; permissão de bot View Channels. O fluxo de código deve estar habilitado para devolver o code junto à instalação. A conta que autoriza precisa administrar o servidor escolhido. O backend verifica a associação, o papel de administrador/Manage Guild e a presença do bot na coleta.

Não solicita conteúdo de mensagens, não usa Gateway e não executa moderação. Coleta números aproximados de membros e presença e a quantidade de canais. O histórico começa com a autorização.

Referência: [OAuth2 no Discord](https://docs.discord.com/developers/topics/oauth2).

## TikTok — experimental

Cadastre Login Kit para web e Display API, com os escopos user.info.basic, user.info.stats e video.list, conforme elegibilidade do aplicativo. Use /api/oauth/tiktok/callback e informe Client Key no campo Client ID/Key.

Coleta perfil, estatísticas e até 200 vídeos em páginas de 20. São contadores acumulados e snapshots, não acesso universal a todos os relatórios do TikTok Studio. Não publica conteúdos.

Referências: [Login Kit web](https://developers.tiktok.com/docs/en/login-kit-web), [tokens](https://developers.tiktok.com/docs/en/oauth-user-access-token-management).

## Reconectar, remover e verificar problemas

- Reautorizar: renova o vínculo existente. Escolha o mesmo canal. O histórico permanece.
- Conectar outra conta: cria um vínculo adicional; duplicação do mesmo recurso é recusada.
- Sincronizar: enfileira uma coleta, sem duplicar job em andamento.
- Remover: exige confirmação na UI e elimina credenciais da conta e dados associados no banco local. A configuração do aplicativo permanece disponível para outras contas.
- Revogação remota: faça também nas configurações do Google/Twitch/TikTok ou da integração Discord. A ferramenta não revoga automaticamente grants que podem ser compartilhados.
- Erros 401/403: confira autorização, escopos, revisão do aplicativo e quotas.
- Erros temporários: o worker tenta novamente e mostra o estado no painel.
- Dados desatualizados: confira última coleta e período disponível. Não há apagamento automático de histórico nesta prévia.

Antes de disponibilizar uma instância para o público, a operação precisa concluir a validação real, políticas de privacidade e os requisitos de retenção/revogação aplicáveis aos dados de cada provedor. A documentação não substitui as condições da plataforma.
