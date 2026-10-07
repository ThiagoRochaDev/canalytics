# Contribuindo com o Canalytics

O projeto é Apache-2.0 e segue a proposta open source do Observa.

1. Descreva o problema, a plataforma afetada e um exemplo sem dados privados.
2. Faça mudanças pequenas e explique o resultado esperado.
3. Execute pytest, os testes de analytics do frontend e o build TypeScript/Vite.
4. Inclua testes para autorização, persistência e normalização quando essas áreas mudarem.
5. Diferencie capacidades implementadas, experimentais e planejadas.

Não inclua tokens, Client Secrets, cookies, bancos de usuários ou respostas reais privadas. Use fixtures fictícias com marcas TGR. Respeite fontes, unidades e significado temporal: uma contagem acumulada não é um relatório diário.

Novos conectores devem usar interfaces oficiais, documentar escopos, elegibilidade, limites, renovação e revogação. O contrato inicial está em docs/ARQUITETURA.md. Acesso por scraping ou senha da conta não faz parte da arquitetura.

Documente limites e disponibilidade; métricas indisponíveis devem ser null. Não some audiência entre plataformas como se fosse única. Execute a coleta com limites e mensagens de erro que não revelem segredos.

Ao submeter uma contribuição, você concorda em disponibilizá-la sob a licença Apache-2.0 do projeto. Abra issues e pull requests em https://github.com/ThiagoRochaDev/canalytics.
