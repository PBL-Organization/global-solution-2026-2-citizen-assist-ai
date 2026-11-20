# Citizen Assist AI — Global Solution 2026.2 (FIAP)

Assistente de triagem informativa em linha de comando (CLI), desenvolvido em **Python puro** (restrito às Fases 1 a 6, sem `try/except`), voltado à orientação cidadã em **Documentação**, **Serviços Públicos** e **Direitos e Assistência**.

---

## 1. Integrantes da Equipe
* **José Elias Aleixo Lopes** — RM568858
* **Sarah Mendes Machado De Oliveira** — RM570514
* **Gustavo Veloso Marchese dos Santos** — RM568930
* **Allan Victor Santos de Almeida Jesus** — RM573218

---

## 2. Visão Geral e Problema Resolvido
O **Citizen Assist AI** centraliza orientações verificadas sobre serviços públicos e direitos básicos (como RG, CPF, Título de Eleitor, Carteira de Trabalho Digital, seguro-desemprego, INSS, Cartão SUS, Tarifa Social de Energia, Passe Livre, Bolsa Família, Procon, FGTS, BPC/LOAS e matrícula escolar), exigindo citação de fonte oficial e bloqueando respostas sem respaldo documental ou ambíguas.

---

## 3. Arquitetura do Projeto
* **`data/base.json`**: Base de conhecimento estruturada com 15 registros validados distribuídos em 3 temas (`Documentacao`, `Servicos Publicos` e `Direitos e Assistencia`), contendo campos obrigatórios (`id`, `tema`, `palavras_chave`, `pergunta_exemplo`, `orientacao_resumida`, `referencia_fonte`, `url_fonte`, `data_verificacao`).
* **`src/sistema.py`**: Script principal contendo carregamento defensivo via condicionais (`os.path.exists`, `os.access`, `.strip()`, `startswith`, validação de chaves obrigatórias), motor de busca linear $O(n)$, grafo de temas, *guardrails* booleanos, templates de resposta (Modelos A e B) e menu interativo CLI.
* **`tests/relatorio_testes.md`**: Bateria empírica de 12 testes, cálculo de métricas com o módulo nativo `time` e registro do teste de usabilidade com melhorias futuras.
* **`docs/uso_ia.md`**: Registro transparente do uso de IA generativa, prompts utilizados, auditoria manual e correções aplicadas.
* **`docs/link_video.txt`**: Arquivo com os links do repositório e do vídeo pitch.

---

## 4. Algoritmo de Busca e Navegação em Grafo
1. **Sanitização de texto (`sanitizar_texto`)**: Converte para minúsculas, remove acentos via `unicodedata.normalize("NFD", ...)`, substitui pontuações por espaços e gera a lista de tokens com `.split()`.
2. **Pontuação e busca linear $O(n)$ (`buscar_orientacoes`)**: Calcula o *score* pela interseção entre os tokens da consulta e as `palavras_chave` do registro (somando `+1` para correspondência de termo composto exato) e ordena por pontuação decrescente com critério determinístico de desempate (`id`, `pergunta_exemplo` e índice).
3. **Grafo de temas (`construir_grafo` e `assuntos_relacionados`)**: Representa os temas como nós em um dicionário de adjacência e sugere até 3 assuntos relacionados (excluindo o próprio registro consultado) no mesmo tema e nos temas vizinhos.

---

## 5. Estratégia de Prompts, Formatação e Guardrails
* **Modelos de Resposta (Frente C)**:
  * **Modelo A (Objetivo)**: Apresenta resumo direto, dúvida de referência, ID do registro, fonte oficial, link, data de verificação e aviso de que não substitui canais oficiais.
  * **Modelo B (Didático)**: Organiza a resposta em orientação contextualizada, checklist de ação, fonte oficial e aviso de confirmação.
* **Guardrails Booleanos (`avaliar_guardrails`)**: Bloqueiam respostas quando há ausência de correspondência (`score_principal == 0`), base fora do domínio ou ambiguidade (empate no maior *score* entre múltiplos registros), exibindo aviso explícito de limitação em vez de gerar informações inventadas.

---

## 6. Métricas e Bateria de Testes (QA)
Na execução de **12 casos de teste** (`tests/relatorio_testes.md`) cobrindo dúvidas diretas, reformulações, entradas vazias, ambiguidades e temas fora do escopo, com medição via módulo nativo `time` (`time.perf_counter()`):
* **Taxa de Acerto:** **83,33%** (10 acertos em 12 testes).
* **Tempo Médio de Resposta:** **0,3473 ms**.

---

## 7. Teste de Usabilidade e Melhorias Futuras
Em avaliação com usuário externo no terminal:
* **Dificuldades identificadas**: Uso de sinônimos/termos coloquiais não presentes nas palavras-chave (como *"energia barata"* ou *"situação eleitoral"*) e dúvida inicial ao digitar texto livre antes de escolher uma opção numérica do menu.
* **Melhorias futuras justificadas**:
  1. **Ampliação de sinônimos e variações vocabulares** na base/busca para reduzir falhas semânticas em reformulações.
  2. **Suporte a busca direta a partir da entrada principal e feedback de navegação mais claro** no menu CLI.

---

## 8. Como Executar o Projeto
1. Clone o repositório e acesse a pasta:
   bash
   git clone https://github.com/PBL-Organization/global-solution-2026-2-citizen-assist-ai.git https://github.com/PBL-Organization/global-solution-2026-2-citizen-assist-ai.git
   cd global-solution-2026-2-citizen-assist-ai

   9. Ética e Uso de IA
Conforme documentado em docs/uso_ia.md, a equipe utilizou o Google Gemini como apoio técnico/arquitetural sob auditoria humana rigorosa, corrigindo manualmente links que retornavam erro HTTP 404 na versão inicial da base, removendo blocos try/except para manter estrita aderência às Fases 1 a 6 e filtrando o registro atual nos assuntos relacionados.

10. Vídeo Pitch
Link do Vídeo: https://youtu.be/-_45vLXptYU
