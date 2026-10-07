# Canalytics — arquitetura de conectores e expansão de plataformas

Versão 0.2 • 6 de outubro de 2026 • Visão de arquitetura e roadmap

Atualização: a prévia 0.1.0 foi implementada após autorização. Consulte [IMPLEMENTACAO.md](IMPLEMENTACAO.md) para distinguir capacidades atuais e futuras, e [ARQUITETURA.md](ARQUITETURA.md) para o contrato inicial dos adaptadores.

## 1. Direção confirmada

Canalytics será uma plataforma open source para gestão e análise de conteúdos, lives e comunidades. YouTube, Twitch, Discord, TikTok e Bilibili entram na visão do produto, com possibilidade de adicionar outras plataformas.

Para o criador, a experiência desejada é: escolher o conector, autorizar o Canalytics, selecionar as contas ou recursos e acompanhar as funções habilitadas.

A extensibilidade é um compromisso de arquitetura. “Qualquer plataforma” não é uma promessa de suporte imediato: é necessário haver integração oficial adequada, acesso aprovado e conector implementado e validado. Consentimento não cria permissões ou endpoints que o provedor não oferece.

**Analytics é o núcleo do produto:** cada conector deverá declarar sua cobertura de métricas, histórico e detalhamento para sustentar o painel analítico do recurso. A validação de uma integração precisa demonstrar o valor analítico disponível, além de confirmar que a autorização funciona. Os critérios de qualidade estão na seção 5.1 do [planejamento principal](PLANEJAMENTO.md).

## 2. Três áreas de produto

| Área | Recursos acompanhados | Decisões apoiadas |
|---|---|---|
| Conteúdo | Canais, perfis, vídeos, publicações e clips | O que publicar, quais resultados acompanhar e o que atualizar |
| Ao vivo | Canais de transmissão, sessões, agendas e eventos | Quando transmitir e como acompanhar a sessão |
| Comunidade | Servidores, canais de conversa, eventos e atividade agregada | Como organizar, comunicar e moderar com as permissões disponíveis |

Uma área de trabalho pode ter recursos nas três áreas. Dados e ações continuam vinculados ao recurso e à plataforma de origem.

## 3. Matriz inicial de conectores

Todos os conectores abaixo estão **planejados**, não implementados. A leitura documental identifica caminhos possíveis, não certifica acesso em produção.

| Plataforma | Acesso planejado | Primeira capacidade a validar | Expansão possível | Limite relevante |
|---|---|---|---|---|
| YouTube | Autorização Google por canal/contexto | Metadados e relatórios de consumo, inscritos e interação | Receita autorizada, retenção, alcance e gestão de conteúdo | Relatórios têm escopos e combinações próprias; agregação exige enquadramento |
| Twitch | Autorização da conta e eventos suportados | Canal, estado da live, espectadores atuais, seguidores e agenda conforme acesso | Assinaturas autorizadas, clips, atualização do canal e gestão da agenda | Contagem atual não é histórico completo nem receita; funcionalidades variam por autorização |
| Discord | Instalação do aplicativo/bot no servidor por quem tiver permissão | Recursos autorizados e atividade agregada a partir dos eventos disponíveis | Comunicação, eventos e moderação explicitamente habilitadas | Permissões por servidor/canal e intents; login de usuário sozinho não basta |
| TikTok | Login Kit e produtos/escopos aprovados | Perfil, vídeos e contadores expostos | Publicação ou envio de rascunhos com autorização própria | Não presumir acesso a todo o painel do criador, receita ou lives |
| Bilibili | Aplicativo na plataforma aberta e autorização prevista por ela | Confirmar elegibilidade e acesso a dados de criador/conteúdo | Conteúdo e serviços de live conforme produtos aprovados | Endpoints, métricas, regiões e requisitos de credenciamento ainda precisam de validação |

A Twitch documenta consulta de streams, seguidores, assinaturas e ações de canal na [API oficial](https://dev.twitch.tv/docs/api/reference/), e entrega eventos por [EventSub](https://dev.twitch.tv/docs/eventsub/). Relatórios chamados “Analytics” para jogos e extensões não equivalem automaticamente ao histórico analítico completo de um streamer.

O Discord usa instalação e permissões próprias para bots; determinados eventos e campos dependem de intents privilegiados. Fontes: [OAuth2 e bots](https://docs.discord.com/developers/topics/oauth2) e [Gateway e intents](https://docs.discord.com/developers/events/gateway#privileged-intents). Não planejar automação de contas pessoais por self-bots nem coleta indiscriminada de conversas.

O TikTok distingue leitura de perfil/vídeos, estatísticas e publicação em seus [escopos](https://developers.tiktok.com/docs/en/tiktok-api-scopes). O [objeto de vídeo](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object) inclui contadores como visualizações, comentários e compartilhamentos. Uso em produção depende da aprovação aplicável, descrita no [guia de revisão](https://developers.tiktok.com/docs/en/app-review-guidelines).

O [portal oficial da Bilibili](https://open.bilibili.com/) apresenta ingresso, verificação de identidade, criação de aplicativo e autorização. A documentação pública consultada não foi suficiente para confirmar o conjunto de métricas; o conector permanece em investigação de viabilidade.

## 4. Experiência de conexão

1. Abrir “Conexões” e escolher a plataforma.
2. Ver quais dados e ações a integração oferece.
3. Autorizar na plataforma; quando necessário, instalar o bot/aplicativo.
4. Selecionar os recursos aos quais realmente foi concedido acesso.
5. Associar os recursos à área de trabalho correta.
6. Ver o que está disponível, o que depende de permissão adicional e a cobertura do histórico.
7. Iniciar importação e acompanhar progresso.
8. Reconectar, reduzir permissões ou remover a integração a qualquer momento.

Estados visíveis: não conectado, aguardando autorização, importando, ativo, acesso parcial, reconexão necessária, limite temporário, erro e desconectado.

A central deve permitir várias contas do mesmo provedor e várias instalações por área. Uma conexão não será tratada como sinônimo de um único canal.

## 5. Capacidades e permissões

O produto não habilitará tudo apenas porque uma conexão existe. A disponibilidade efetiva é a interseção entre:

- O que o conector implementa.
- O que o provedor oferece e aprovou para o aplicativo.
- O que a pessoa autorizou.
- O que o papel dessa pessoa permite no recurso.
- O que seu papel no Canalytics permite.

Famílias de capacidades propostas:

| Família | Exemplos | Regra |
|---|---|---|
| Identificação | Perfil e descoberta de recursos | Não assumir acesso a todos os recursos da conta |
| Leitura | Conteúdo, métricas, agenda, estado da live | Escopos mínimos e recursos explicitamente vinculados |
| Financeiro | Receita e monetização disponíveis | Permissão e visibilidade separadas |
| Publicação | Envio ou alteração de conteúdo | Prévia, destino e autorização da ação |
| Comunidade | Comunicação e moderação | Permissões próprias por servidor/canal |
| Eventos | Alterações de estado e novos eventos | Deduplicação e tratamento de perda/reconexão |

Dar permissão técnica ao aplicativo permite oferecer uma ação; não é uma ordem para publicar, enviar mensagens ou moderar automaticamente. Automações futuras terão regras explicitamente ativadas pelo usuário.

No serviço hospedado, cadastraremos os aplicativos das integrações. Na instalação própria, o operador configurará essas credenciais uma vez; o usuário final seguirá o fluxo de autorização. Instalações independentes não herdam automaticamente aprovações do serviço Cloud.

## 6. Contrato de um conector

O núcleo deverá conhecer um contrato estável; as particularidades de cada provedor ficam no adaptador.

Cada conector declara:

- Identidade, versão, mantenedor, licença, status e links oficiais.
- Métodos de autorização, instalação, renovação e revogação suportados.
- Tipos de recurso e descoberta/paginação.
- Catálogo de capacidades e permissões exigidas.
- Catálogo de métricas com definição, unidade, período e regra de agregação.
- Sincronização, cursores e cobertura histórica.
- Eventos suportados, modo de entrega e verificação de origem.
- Ações disponíveis e estrutura para prévia, execução e resultado.
- Limites de uso, tratamento de erros, retenção e limpeza.
- Testes de contrato e documentação de operação.

Não exigir que um conector implemente todas as famílias. Um conector apenas de leitura deve ser útil; a interface mostrará o subconjunto validado.

Separar estados do catálogo — planejado, experimental, validado e descontinuado — dos estados de cada conexão do usuário. Somente conectores disponíveis mostrarão o botão de conexão.

## 7. Modelo de dados comum sem distorcer métricas

Identificar recurso por provedor, tipo e ID externo. Vincular acesso à área de trabalho separadamente. Um ID numérico de uma plataforma nunca será confundido com o mesmo número em outra.

Objetos centrais: área de trabalho, conta externa, autorização/instalação, recurso, conteúdo, sessão de transmissão, observação de métrica, evento, tarefa e ação auditada.

O núcleo mantém campos comuns e extensões específicas. Servidor Discord não será armazenado como se fosse um canal de vídeo, nem mensagem como se fosse uma visualização.

Regras de comparação:

- Seguidores, membros de comunidade e assinaturas pagas são conceitos separados.
- Views de plataformas distintas preservam suas definições; totais combinados só serão oferecidos quando semântica e políticas permitirem.
- A mesma pessoa em duas redes não será contada como uma pessoa única sem base válida.
- Comparações precisam de intervalo, cobertura e granularidade compatíveis.
- Relatórios históricos, snapshots de contadores e eventos coletados desde a conexão terão rótulos distintos.
- Diferença entre dois contadores acumulados não será apresentada automaticamente como relatório oficial de atividade do período.
- Métricas calculadas terão método e limitações declarados, quando permitidas.
- Mensagens brutas não serão requisito padrão para medir volume agregado de atividade.

A política de agregação do YouTube continua válida dentro de um produto multiplataforma; conectar outro provedor não remove essa restrição. Ver [políticas do YouTube](https://developers.google.com/youtube/terms/developer-policies).

## 8. Operação e ciclo de vida

Combinar tarefas agendadas, webhooks e conexões persistentes conforme o serviço. Para Discord e outros conectores que dependam de sessão contínua, prever processo de eventos separado da aplicação web. Não vincular a arquitetura exclusivamente a requisições curtas de uma hospedagem.

Requisitos futuros de aceitação:

- Cobertura de métricas, histórico e recortes declarada e comprovada por conexão.
- Valores conferidos contra a fonte em consultas equivalentes, com divergências explicadas.
- Investigação de resultados e exportação coerentes com o painel analítico do recurso.

- Eventos repetidos não duplicam contagens ou ações.
- Uma falha de conector não interrompe os outros.
- Renovação ou revogação é tratada segundo o tipo de credencial.
- Desconectar um servidor não revoga um token compartilhado usado legitimamente em outros servidores.
- Desconexão interrompe tarefas e eventos do vínculo e aplica sua política de exclusão.
- Exportações, filas e webhooks respeitam o isolamento entre clientes.
- Permissões são reavaliadas após mudança de papel no provedor.
- Cotas têm limites por provedor e distribuição justa por cliente.
- Tokens ficam no servidor, com criptografia e logs sem segredos.
- Atualizações do conector preservam o histórico e registram mudanças de definição.
- Repetição de uma ação externa após falha ambígua exige reconciliação, para não publicar ou moderar duas vezes.

Cada conector terá sua própria política de armazenamento e exclusão. A maior retenção permitida por um provedor não se estende aos demais.

## 9. Conectores e comunidade open source

Separar desenvolvimento/instalação de código de autorização de contas. Autorizar o TikTok, por exemplo, não instalará código arbitrário enviado por um terceiro.

Planejar adaptadores mantidos no repositório, um guia de contribuição e testes comuns. Conectores comunitários poderão ser propostos com documentação, licença compatível e responsável pela manutenção. Sua entrada no serviço hospedado passa por revisão; uma versão aberta poderá ter conectores locais sob responsabilidade de seu operador.

Um SDK e um catálogo público de extensões serão evolução do contrato depois de comprová-lo com integrações reais. Não criar um marketplace antes dessa validação.

## 10. Sequência proposta

1. Detalhar central de conexões, recursos e matriz de permissões.
2. Usar YouTube como primeiro conector, aproveitando a pesquisa existente.
3. Validar Twitch como segundo, para testar o modelo de transmissão e eventos.
4. Incluir Discord para provar o modelo de instalação em comunidades e processos persistentes.
5. Implementar TikTok conforme aprovação dos produtos e escopos necessários.
6. Avançar Bilibili após confirmar credenciamento, documentação e recursos disponíveis.
7. Abrir contribuições de novos conectores sobre um contrato já validado.

A ordem é uma recomendação, não uma decisão já aprovada. A investigação de elegibilidade de TikTok e Bilibili pode começar cedo na futura fase técnica, para identificar dependências externas.

O primeiro piloto precisa de pelo menos duas plataformas para demonstrar que a arquitetura é realmente extensível. Não prometer todos os conectores prontos no lançamento inicial.

## 11. Telas previstas para detalhar

- Visão geral: recursos conectados, resultados por plataforma e pendências.
- Conexões: catálogo, contas, permissões, capacidades e saúde da integração.
- Conteúdos: biblioteca e histórico onde disponíveis.
- Ao vivo: sessões, estado e agenda dos serviços compatíveis.
- Comunidades: servidores e atividade autorizada.
- Relatórios: métricas e filtros compatíveis com cada fonte.
- Equipe e configurações: acesso por recurso, operações e ciclo de vida dos dados.

Este documento preserva a visão ampliada do produto. A implementação atual está em IMPLEMENTACAO.md; nenhum conector foi homologado em conta de produção ou publicado como serviço externo.
