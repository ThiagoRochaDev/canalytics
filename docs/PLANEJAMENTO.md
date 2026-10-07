# Canalytics — planejamento do produto

Versão 0.3 • 6 de outubro de 2026 • Proposta para discussão — analytics como núcleo, integração por conectores

Canalytics é o nome escolhido pelo usuário para o produto. A licença adotada é Apache-2.0, seguindo a proposta do Observa. Domínio e preços ainda não estão definidos. A escolha do nome não representa verificação de disponibilidade de marca ou domínio.

## 1. Direção acordada e estado atual

Criar uma plataforma open source para monitorar e gerenciar conteúdo, transmissões e comunidades em várias plataformas, por meio de conectores autorizados pelo usuário. YouTube, Twitch, Discord, TikTok e Bilibili fazem parte da visão do produto. Cada conector poderá atender várias contas e recursos, conforme as APIs e permissões da plataforma.

Descrição proposta: **Canalytics — seus conteúdos, lives e comunidades em um só lugar.**

**Prioridade confirmada:** analytics profundo é o núcleo do produto. O Canalytics deverá acompanhar métricas, evolução e histórico de cada canal/recurso e ajudar a investigar seus resultados. A ambição é melhorar a experiência de análise dos painéis nativos nas capacidades acessíveis, conforme os critérios da seção 5.1.

A direção confirmada é uma arquitetura extensível. A ordem de implementação dos conectores continua em discussão; a autorização do usuário não garante acesso a recursos que a plataforma não oferece. O detalhamento está em [CONECTORES.md](CONECTORES.md).

A implementação foi autorizada em 6 de outubro de 2026. A prévia 0.1.0 implementa a base descrita em [IMPLEMENTACAO.md](IMPLEMENTACAO.md); este documento preserva a visão ampliada e inclui funcionalidades futuras. Não houve publicação do serviço nem criação de repositório público.

A estrutura exploratória anterior foi preservada localmente em .scaffold. A arquitetura adotada na prévia é React/Vite + FastAPI/SQLite, com instalação própria e Docker. As integrações reais ainda precisam de homologação com credenciais dos provedores.

## 2. Proposta de valor

Ajudar criadores, streamers e equipes a entender a evolução de seus conteúdos, transmissões e comunidades, com histórico confiável, ações de gestão autorizadas e controle dos próprios dados.

Público inicial proposto: criadores, streamers e pequenas equipes com presença em várias plataformas. Agências serão uma expansão, com áreas separadas por cliente e permissões explícitas.

Perguntas que o produto deve responder:

- Como cada canal, perfil ou comunidade evoluiu na respectiva plataforma?
- Quais vídeos geram visualizações, tempo assistido e inscritos?
- Onde o público abandona os vídeos?
- Quais fontes de tráfego e públicos aparecem nos relatórios?
- O que mudou após uma publicação ou alteração editorial?
- Quais canais, lives e comunidades precisam de atenção e quais dados ainda estão pendentes?
- Quais ações estão disponíveis em cada conexão e quais exigem nova autorização?

O diferencial proposto combina conectores extensíveis, gestão de conteúdo e comunidades, explicação dos números, portabilidade e operação transparente. Essa hipótese de posicionamento precisa ser validada com criadores.

## 3. Código aberto e serviço hospedado

| Modalidade | Proposta | Quem opera |
|---|---|---|
| Community | Código aberto, núcleo funcional completo e instalação documentada em servidor próprio | O operador configura infraestrutura, credenciais das plataformas, atualizações e backups |
| Cloud | Mesmo núcleo, hospedagem gerenciada, sincronização e suporte | Nós operamos a infraestrutura e os aplicativos cadastrados nas plataformas |

Recomendação: cobrar pela hospedagem, operação e suporte. Definir limites e preços após medir custo por canal ativo, volume de vídeos, tarefas, armazenamento e atendimento.

A instalação aberta deverá funcionar sem assinatura ou conta no serviço Cloud. Cada instalação terá seus próprios requisitos de infraestrutura e acesso às APIs. Não prometer canais ilimitados.

## 4. Escopo por etapa

### MVP — primeira versão utilizável

| Área | Entrega | Critério de aceite |
|---|---|---|
| Conectores e contas | Catálogo de integrações, autorização por plataforma, seleção de recursos, reconexão e remoção de acesso | Múltiplas contas e recursos funcionam sem sobrescrever autorizações |
| Recursos disponíveis | Mostrar métricas e ações habilitadas por conexão | A interface respeita API, aprovação do aplicativo, permissões do usuário e acesso ao recurso |
| Áreas de trabalho | Separação por criador/cliente e organização por grupos | Um cliente não acessa dados, arquivos ou tarefas de outro |
| Analytics por canal/recurso | Evolução, métricas disponíveis, comparação de períodos e investigação até os detalhes suportados | O criador consegue analisar resultados com fonte, cobertura, atualização e definições explícitas |
| Histórico | Séries diárias; 7, 28, 90 dias e intervalo personalizado | Período pedido e período disponível claramente diferenciados |
| Desempenho dos conteúdos | Biblioteca pesquisável, ordenação e análise por conteúdo/formato onde suportada | Totais e métricas do período são distintos; o usuário identifica os conteúdos que explicam os resultados do próprio canal |
| Organização | Grupos, notas e registro de decisões | Informação persistente e acesso autorizado |
| Exportação | CSV por canal e período | Arquivo reproduz filtros, unidade e granularidade |
| Operação | Atualização agendada, atualização manual limitada e retentativas | Falhas não apagam dados válidos nem duplicam resultados |
| Controle dos dados | Desconexão, revogação e exclusão do histórico associado | Ciclo de exclusão verificável |
| Demonstração | Exemplos fictícios sem autorizar plataformas externas | Dados demonstrativos nunca se misturam aos reais |

Neste MVP, “gerenciar” significa organizar contas, canais, perfis, comunidades, acessos e trabalho interno. A arquitetura de conectores deve ser validada com ao menos duas plataformas diferentes antes de ser considerada estável. Ações externas de publicação e moderação terão uma etapa própria.

### Expansão analítica

- Reporting API para alcance, impressões, CTR de thumbnails e importações em lote.
- Retenção por trecho e filtros de público compatíveis com cada relatório.
- Comparações de vídeos em janelas equivalentes após publicação, quando os dados permitirem.
- Metas e alertas com regras explicáveis e cobertura suficiente.
- Relatórios recorrentes e papéis de equipe, incluindo controle de acesso financeiro.
- Calendário editorial e registro de experimentos, sem afirmar causalidade automaticamente.

### Gestão nas plataformas conectadas

- Edição de metadados e gestão de playlists/comentários quando suportadas.
- Upload e programação de conteúdo conforme as permissões de cada serviço.
- Gestão de transmissões e agenda onde a API oferecer essas ações.
- Comunicação e moderação de comunidades, com permissões próprias.
- Prévia da alteração, plataforma e recurso de destino explícitos e confirmação por ação ou lote.

Essa etapa exigirá permissões adicionais e auditoria das ações.

Fora do compromisso inicial: aplicativo móvel nativo, geração de vídeos, infraestrutura própria para retransmitir vídeo, benchmarks entre clientes, previsões de viralização e substituição completa dos painéis nativos. Novas plataformas são extensões previstas; nenhuma será anunciada como suportada antes da validação de seu conector.

## 5. Catálogo de métricas

Promessa proposta: “todas as métricas disponíveis para os recursos autorizados pelas integrações suportadas”. Cada serviço terá seu catálogo. A tabela abaixo detalha o YouTube; os demais conectores são tratados em [CONECTORES.md](CONECTORES.md).

Não misturar views de vídeos, espectadores simultâneos, seguidores, assinaturas pagas e membros de comunidade em um único indicador. A visão conjunta preservará definição, fonte e granularidade. Não prometer equivalência total com os painéis nativos.

| Família | Exemplos | Fonte planejada |
|---|---|---|
| Cadastro e totais | Vídeos, publicação, status, estatísticas atuais | Data API |
| Consumo | Views, engaged views, minutos assistidos, duração média e percentual assistido | Analytics API |
| Crescimento e interação | Inscritos ganhos/perdidos, likes, comentários e compartilhamentos | Analytics API |
| Retenção | Audiência por trecho do vídeo | Analytics API |
| Público | País, dispositivo, idade, gênero e origem do tráfego disponíveis | Analytics/Reporting |
| Monetização | Receita estimada, anúncios, CPM e reproduções monetizadas | Analytics/Reporting |
| Alcance | Impressões e CTR de thumbnails | Reporting API |
| Complementares | Playlists, cards, telas finais e lives | Relatórios específicos, após validação |

O catálogo oficial cobre métricas de consumo, retenção, interação e receita. Disponibilidade depende do relatório, dimensões, autorização e canal. Ver [métricas da Analytics API](https://developers.google.com/youtube/analytics/metrics).

Impressões e CTR de thumbnails constam nos [relatórios de alcance](https://developers.google.com/youtube/reporting/v1/reports/channel_reports) e no [catálogo da Reporting API](https://developers.google.com/youtube/reporting/v1/reports/metrics).

Cada métrica terá definição, fonte, unidade, granularidade, dimensões aceitas, permissões, regra de agregação e versão. Indicadores próprios e previsões exigem análise de enquadramento: as [políticas adicionais para métricas derivadas](https://developers.google.com/youtube/terms/derived-metrics-policy) condicionam suas permissões ao caso de uso aceito.

Regras do produto:

- Diferenciar zero, ausência de dados, falta de permissão, processamento pendente e erro.
- Exibir “dados até” e “última sincronização” separadamente.
- Comparar apenas períodos com cobertura compatível.
- Não somar percentuais, médias, CPM ou CTR; usar denominadores e regras corretas.
- Não deduplicar espectadores entre canais sem uma fonte apropriada.
- Preservar moeda e caráter estimado da receita.
- Guardar datas diárias no calendário da fonte e horários de processamento em UTC.
- Não identificar Shorts somente pela duração.
- Mostrar a origem de qualquer cálculo e distinguir dados oficiais de interpretações.

### 5.1. Analytics como núcleo do Canalytics — requisito confirmado

O objetivo é oferecer profundidade analítica comparável aos painéis nativos nas métricas acessíveis e uma experiência superior de investigação, organização e apoio à decisão. A qualidade será demonstrada por cobertura, consistência e utilidade, não pelo número de cartões na tela.

Os conectores fornecem acesso aos dados. O principal valor do produto é ajudar o criador a compreender os resultados de cada canal, perfil, transmissão ou comunidade.

| Área analítica | O que o criador deve conseguir analisar |
|---|---|
| Saúde e evolução do canal | Totais atuais, crescimento, ganhos e perdas, tendências e histórico com filtros de período |
| Desempenho de conteúdo | Resultados por vídeo/publicação, formato, série e grupo editorial; contribuição ao resultado do próprio canal |
| Alcance e descoberta | Impressões, cliques, CTR e fontes de tráfego onde essas métricas forem disponibilizadas |
| Consumo e retenção | Tempo assistido, duração média, percentual assistido e curvas por trecho quando disponíveis |
| Público e comunidade | Recortes agregados de audiência e atividade compatíveis com cada fonte |
| Monetização | Receita, indicadores financeiros e evolução com permissão e definições da plataforma |
| Lives | Histórico das sessões, duração, audiência disponível e cobertura das medições |
| Investigação | Abrir um indicador e chegar ao conteúdo, recorte ou intervalo que ajuda a explicar a mudança |

Capacidades de experiência propostas para superar o trabalho manual entre painéis:

- Painel detalhado de cada canal, além da visão de todas as conexões.
- Histórico navegável e comparação com períodos equivalentes, distinguindo dados incompletos.
- Filtros por formato, conteúdo, grupo editorial, público e origem de tráfego conforme a compatibilidade de cada relatório.
- Comparação de conteúdos em janelas equivalentes desde sua publicação quando os dados permitirem.
- Anotações sobre alterações de título, thumbnail, calendário e experimentos, sem atribuir causalidade automaticamente.
- Metas, alertas explicáveis, painéis salvos e relatórios reutilizáveis em etapas posteriores.
- Insights que apresentam a evidência, a interpretação e uma ação possível, deixando claro quando existe apenas uma hipótese.
- Visão conjunta de plataformas com definições preservadas e comparações somente quando forem válidas e permitidas.

Exemplo desejado, apenas ilustrativo: em vez de mostrar somente uma queda de visualizações, permitir investigar quais conteúdos e fontes de tráfego mudaram no período. Uma hipótese sobre título ou thumbnail precisa estar apoiada nos dados disponíveis; não será apresentada como causa comprovada.

Distinguir três camadas: números fornecidos pela plataforma; cálculos do Canalytics com método identificado e enquadramento permitido; interpretações ou recomendações com evidências e incertezas. Nenhuma camada deverá preencher métricas indisponíveis com números inventados.

Critérios de aceite para a primeira entrega analítica:

1. O criador consegue abrir um canal e consultar evolução, histórico, métricas de consumo/crescimento disponíveis e desempenho dos conteúdos.
2. Cada indicador permite identificar definição, fonte, período, cobertura e atualização.
3. Valores são conferidos com relatórios nativos equivalentes, quando acessíveis, usando os mesmos filtros e definições; divergências são explicadas.
4. Comparações tratam períodos incompletos, ausência de base anterior e diferenças de granularidade.
5. Um resultado pode ser investigado até o detalhe suportado pelo conector e exportado de forma consistente.
6. Uma análise interpretativa não confunde correlação, causalidade, estimativa e medição oficial.
7. O piloto verifica se o criador encontra uma resposta confiável com menos esforço do que no fluxo atual entre seus painéis.

Prioridade de entrega: profundidade e confiança no analytics antes de ampliar ações externas de publicação/moderação. Alcance, retenção avançada e monetização continuam sujeitos às capacidades de cada conector e à ordem do roadmap, mas fazem parte explícita da visão analítica. A promessa de ser “melhor” será uma meta de produto validada com usuários, não uma alegação de superioridade já comprovada.

## 6. Contas e autorização

Separar usuário do produto, área de trabalho, provedor, conta externa, autorização/instalação e recurso administrado. Os recursos podem ser canais, perfis ou servidores/comunidades. Sua identidade usa provedor, tipo e ID externo; email não identifica recurso nem substitui autorização.

Jornada: entrar no produto → escolher conector → autorizar no serviço ou instalar o aplicativo/bot → selecionar os recursos permitidos → ver as capacidades habilitadas → iniciar sincronização. Cada conta adicional terá sua própria conexão.

No serviço hospedado, a experiência será conectar e autorizar, depois de a integração estar cadastrada e aprovada. Na instalação própria, o operador configura os aplicativos e credenciais de cada provedor. Permissão de leitura não autoriza publicação ou moderação.

As observações seguintes são específicas do YouTube:

Não assumir que uma autorização retorna todos os canais administrados pela conta. Validar canal pessoal, Brand Account e reconexões. Convites do Studio não garantem acesso às APIs; essa limitação consta nas [permissões de canal](https://support.google.com/youtube/answer/9481328?hl=en).

Apresentar canais na mesma interface e somar dados de proprietários diferentes são operações distintas. A política restringe agregações entre content owners. Por isso, resultados serão inicialmente identificados por canal e cliente; totais de portfólio e comparações cruzadas dependem de validação do enquadramento. Uma área interna ou uma conta Google comum não prova a condição de content owner reconhecido. Ver [política de agregação, III.E.2](https://developers.google.com/youtube/terms/developer-policies).

Usar permissões mínimas de leitura, com receita opcional. Planejar a [verificação OAuth aplicável](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification) antes de oferecer acesso público.

## 7. Arquitetura proposta

Começar com uma aplicação modular, com interface/API e processadores de sincronização separados. Evitar muitos serviços antes de existir necessidade medida.

Fluxo: aplicação web → identidade/permissões → banco e fila → processadores → APIs oficiais → histórico consultável.

Componentes:

- Interface responsiva em português, preparada para outros idiomas.
- Backend dividido em identidade, conectores, recursos, consultas, organização e sincronização.
- Registro de conectores com capacidades, permissões, métricas, eventos e ações versionadas.
- Adaptadores para cada API, evitando regras de uma plataforma espalhadas pelo núcleo.
- Recepção de webhooks e processos persistentes para eventos de serviços que os exigirem.
- Banco relacional para permissões, histórico e controle de importação.
- Tarefas em segundo plano para sincronização, relatórios grandes e exclusão.
- Armazenamento substituível de arquivos, com retenção definida.
- Instalação por contêineres, migrações e backup/restauração documentados.
- Mesmas regras de negócio na edição aberta e na hospedada.

Preferência inicial: TypeScript e PostgreSQL, sem fechar framework, fila ou provedor agora. Registrar as escolhas após validar execução das tarefas, OAuth, volumes e facilidade de instalação.

O login do produto será independente das autorizações nas plataformas externas. A versão aberta não exigirá autenticação de uma plataforma de hospedagem específica. O template anterior será reavaliado antes de qualquer reaproveitamento.

Modelo conceitual:

| Entidade | Finalidade |
|---|---|
| Usuário, área e participação | Identidade, papéis e isolamento |
| Provedor e conector | Identificação, versão e capacidades declaradas |
| Conta externa, conexão e autorização/instalação | Escopos, credenciais protegidas, contexto e validade |
| Recurso e concessão de acesso | Provedor, tipo, ID externo e vínculo autorizado com a área |
| Conteúdo ou sessão de transmissão | Catálogo, metadados e extensões de cada plataforma |
| Observação de métrica | Valor, fonte, definição, recurso, intervalo e granularidade |
| Relatórios por dimensão | Público, tráfego e outros recortes |
| Retenção | Curva, vídeo e intervalo consultado |
| Tarefa e importação | Progresso, cursor, versão e tentativas |
| Nota e grupo | Organização editorial |
| Auditoria e exclusão | Ações e ciclo de vida dos dados |

Cada família de relatório terá granularidade explícita. Não cruzar todas as dimensões numa única tabela, pois isso pode duplicar contagens.

## 8. Sincronização e histórico

Proposta operacional: atualização agendada dos relatórios consolidados e eventos para lives e comunidades onde houver suporte. A frequência depende de cada conector e das cotas. Uma transmissão pode ter estado recente enquanto seu relatório financeiro continua atrasado.

Histórico consultado na API, medições coletadas desde a conexão e cálculos sobre amostras serão distinguidos. Cada conector terá regras próprias de retenção e revogação. Os detalhes de Reporting a seguir se referem ao YouTube.

Importar apenas o histórico disponível e mostrar sua cobertura. A Reporting API produz relatórios diários, pode levar até 48 horas para os primeiros e tem backfill limitado para novos jobs. Correções substituem o relatório anterior do mesmo período. Ver [processamento e histórico](https://developers.google.com/youtube/reporting/v1/reports/).

Requisitos planejados:

- Importação idempotente e versionada.
- Reprocessamento de janela recente para captar correções.
- Controle de cotas e distribuição justa entre clientes.
- Paginação e retomada de tarefas interrompidas.
- Erros de permissão, quota e indisponibilidade diferenciados.
- Tokens criptografados no servidor; credenciais fora do repositório e dos logs.
- Autorização verificada também em exportações e tarefas.
- Cancelamento das tarefas após revogação.

Retenção depende da categoria de dados. Implementar atualização, revalidação de autorização e exclusão conforme as [políticas de armazenamento do YouTube](https://developers.google.com/youtube/terms/developer-policies). Dados históricos autorizados não tornam irrestrita a retenção de todos os metadados. Pedidos de exclusão terão processamento rápido e tratamento definido para exportações e backups.

## 9. Licença e comunidade

Licença adotada na implementação: **Apache-2.0**, seguindo o Observa. A comparação abaixo registra alternativas consideradas no planejamento.

| Opção | Consequência principal | Preferência de produto |
|---|---|---|
| AGPL-3.0 | Exige oferta do código correspondente de versões modificadas aos usuários que interagem com elas pela rede, nos termos da licença | Reciprocidade nas melhorias de serviços derivados |
| Apache-2.0 | Permite amplo reaproveitamento, inclusive derivados proprietários, sob suas condições | Adoção e integração com menor obrigação de reciprocidade |

A decisão foi Apache-2.0. A licença permite uso comercial sob suas condições. Fontes: [AGPL na OSI](https://opensource.org/license/agpl-3.0) e [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

Repositório planejado:

- README, instalação, demonstração e limitações.
- Guia de instalação própria e configuração dos aplicativos de cada plataforma.
- Guia para contribuir com conectores, incluindo contrato, testes, permissões, fontes oficiais e manutenção.
- Contribuição, governança e relato privado de vulnerabilidades.
- Licença, avisos de terceiros e compatibilidade das dependências.
- Dados demonstrativos sintéticos, sem credenciais ou estatísticas privadas.
- Releases, changelog, migrações e atualização reproduzível.
- Termos de contribuição e titularidade definidos antes de contribuições externas.

Publicar o código e liberar o serviço são decisões separadas. Código aberto não implica tornar públicos os dados dos criadores.

## 10. Roadmap e critérios

| Etapa | Resultado | Condição para avançar |
|---|---|---|
| A. Planejamento, concluído | Escopo, jornadas, catálogo e decisões | Direção acordada; prévia implementada descrita em IMPLEMENTACAO.md |
| B. Validação técnica | Evidências com recursos autorizados de plataformas diferentes | Confirmar acesso, cobertura, permissões e contrato dos conectores |
| C. MVP | Analytics por canal, histórico, análise de conteúdos, ao menos dois conectores, organização e exportação | Verificar profundidade analítica da seção 5.1, consistência, isolamento e recuperação |
| D. Piloto | Uso por um pequeno grupo de criadores | Medir utilidade, confiabilidade e custo por canal |
| E. Lançamento | Repositório e instalação preparados; serviço operável | Licença definida e requisitos dos provedores atendidos |
| F. Expansão | Análise avançada, equipe e gestão | Priorizar pelo uso observado |

Não fixar lançamento antes da validação técnica. Existem dependências externas de verificação e acesso em cada provedor.

Qualidade a verificar futuramente: relatórios equivalentes ao Studio, períodos incompletos, tokens revogados, troca de escopo, isolamento entre clientes, importação repetida, relatórios corrigidos e restauração de backup.

Indicadores do piloto: tempo até primeiro resultado útil, conexões concluídas, sincronizações bem-sucedidas, idade dos dados, retorno semanal, decisões apoiadas pelo produto, custo por canal e solicitações de suporte. Medir uso do produto separadamente dos dados privados dos canais.

## 11. Decisões abertas

1. Identidade visual e domínio para Canalytics.
2. Licença: Apache-2.0, definida.
3. Prioridade entre criadores de vídeo, streamers e equipes de comunidade no primeiro piloto.
4. Profundidade da organização editorial no MVP.
5. Prioridade entre receita, alcance e retenção na expansão.
6. Ordem dos conectores e contas/servidores de teste para a futura validação técnica.
7. Preços e limites após medir custos.

A implementação da prévia foi autorizada e entregue no código. O próximo ciclo é homologar os conectores com contas reais e ampliar a cobertura analítica conforme IMPLEMENTACAO.md.
