# Estado da implementação — 0.1.0

A implementação foi autorizada em 6 de outubro de 2026, substituindo a restrição anterior de apenas planejar. O nome é Canalytics e a proposta segue o Observa: código aberto Apache-2.0, instalação própria e conectores.

## Entregue no código

- React/TypeScript/Vite + FastAPI + SQLite.
- Conta inicial de administrador, sessões, áreas de trabalho e separação de dados.
- Gráficos, filtros, catálogo, público, CSV, notas e demonstração sintética.
- Temas claro, escuro e sistema, com persistência da preferência e layout móvel.
- Screenshots sanitizados para o repositório e pacote local de vídeos, artes LinkedIn e PDFs.
- OAuth, credenciais criptografadas e renovação de tokens.
- Worker persistente, idempotência, novas tentativas e reconexão.
- Adaptadores YouTube, Twitch, Discord e TikTok; Bilibili identificado como planejado.
- Scripts locais, container, Compose e workflow CI.
- Testes de autorização, OAuth, isolamento, cache e cálculos.

## Validação e limites

Testes usam fixtures e mocks. Credenciais reais não foram fornecidas: autorização e métricas em contas de produção precisam de homologação. O código está publicado em [https://github.com/ThiagoRochaDev/canalytics](https://github.com/ThiagoRochaDev/canalytics). A aplicação continua destinada à instalação própria; nenhum serviço público foi implantado.

Não está implementado: cadastro público multiusuário, convites, cobrança, MFA, notificações externas, postagem, moderação, marketplace completo, previsões, comparação entre clientes, importação CSV nem Reporting API.

Esta versão usa um administrador e um worker por instalação. O usuário pode organizar vários canais e contas em áreas. Não confundir essa organização com um SaaS público finalizado.

## Prioridade do próximo ciclo

1. Homologar YouTube/Twitch com contas de teste reais e rever retenção/revogação.
2. Ampliar relatórios por vídeo/período, dados históricos e métricas oficiais disponíveis.
3. Equipes e papéis, logs de auditoria e operação gerenciada.
4. Estabilizar o contrato de autenticação de plugins.
5. Homologar Discord/TikTok e estudar acesso oficial à Bilibili.

Os documentos PLANEJAMENTO e CONECTORES preservam a visão ampliada; itens futuros nesses documentos não são promessa de implementação nesta versão.

## Validação visual e material de divulgação

Veja [a matriz de cobertura e os screenshots](MIDIA-E-TESTES.md). Foram preparados oito vídeos legendados por sequência de capturas, seis artes e dois PDFs, com dados fictícios explicitamente identificados. Nenhuma postagem externa foi enviada.

## Publicação open source

Repositório público: [https://github.com/ThiagoRochaDev/canalytics](https://github.com/ThiagoRochaDev/canalytics). Licença Apache-2.0. A [release v0.1.0](https://github.com/ThiagoRochaDev/canalytics/releases/tag/v0.1.0) reúne o pacote de mídia e os PDFs com dados fictícios. Relatos privados de segurança estão habilitados no GitHub.
