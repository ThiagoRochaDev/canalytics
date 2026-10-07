# Segurança

Canalytics 0.1.0 é uma prévia para instalação própria com um administrador. Ainda não foi auditado para operação SaaS pública.

## Controles implementados

- Sessões opacas com hash no SQLite, expiração, HttpOnly/SameSite=Lax e Secure sob HTTPS.
- Senhas derivadas com scrypt e salt aleatório.
- Verificação de origem para mutações, cabeçalho explícito de requisição e controle de hosts.
- OAuth state aleatório, armazenado como hash, de uso único e vinculado à sessão, provedor e área.
- PKCE no fluxo Google; outros fluxos usam o modelo documentado de cliente web confidencial.
- Tokens, refresh tokens e secrets criptografados com Fernet.
- SQL parametrizado e autorização por associação à área.
- Exportações com proteção contra fórmulas em células.
- Nenhuma credencial retorna nas respostas de listagem ou mensagens de erro.
- Execução local em loopback e container sem usuário root.

## Operação

Mantenha banco, chave de criptografia e backups privados. A chave reside junto do banco: protege contra vazamento isolado do banco, não contra comprometimento completo do host. No Windows, aplique ACLs adequadas ao diretório; modo POSIX 0600 não substitui ACLs.

Use HTTPS em acesso remoto, faça o primeiro cadastro antes de expor a instalação e preserve CANALYTICS_PUBLIC_URL. Não ative logs de acesso que registrem URLs de callback OAuth contendo códigos. Configure o proxy para omitir ou mascarar essas URLs.

Há limitação de tentativas por processo; não há MFA, convites ou recuperação de senha por e-mail. Use um único processo de API e proteja a instalação com controles adequados à operação.

Remover uma conexão no painel apaga os dados associados e tokens locais. Revogue também o acesso no provedor. Não há exclusão automática por prazo nesta prévia; a política de retenção precisa ser concluída antes de publicação de um serviço gerenciado.

## Relato de vulnerabilidades

Não publique credenciais, provas de exploração com dados reais nem detalhes que permitam comprometer uma instalação ativa. Use [Report a vulnerability](https://github.com/ThiagoRochaDev/canalytics/security/advisories/new) para enviar um relato privado ao mantenedor. O repositório tem Private Vulnerability Reporting habilitado.

Inclua versão, passos mínimos com dados sintéticos e impacto observado.
