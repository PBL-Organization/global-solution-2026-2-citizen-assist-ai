# Registro de Uso de Inteligência Artificial — Citizen Assist AI

Este documento registra com transparência como ferramentas de Inteligência Artificial Generativa foram empregadas como apoio técnico durante o desenvolvimento do projeto **Citizen Assist AI** (Global Solution 2026.2 — FIAP), detalhando os prompts utilizados, as limitações identificadas e as intervenções críticas realizadas pela equipe.

---

## 1. Ferramentas Utilizadas
* **Google Gemini (Modo Mentor Técnico / Sparring Arquitetural):** Utilizado para ideação da estrutura de dados (`data/base.json`), refatoração de código para conformidade pedagógica (Fases 1 a 6) e revisão de documentação.

---

## 2. Estratégia de Prompts Aplicada
Para evitar respostas genéricas e garantir aderência às restrições da disciplina, adotamos **Prompts Estruturados com Restrição de Escopo**:
* **Contexto e Papel:** Definição de restrição estrita aos conceitos de Python das **Fases 1 a 6** (proibição de `try/except`, POO avançada ou frameworks externos).
* **Formato de Saída:** Exigência de esquema JSON padronizado com chaves obrigatórias (`id`, `tema`, `palavras_chave`, `pergunta_exemplo`, `orientacao_resumida`, `referencia_fonte`, `url_fonte`, `data_verificacao`).

---

## 3. Validação Crítica e Intervenções Humanas (Auditoria)

A equipe não aceitou nenhuma saída da IA sem auditoria técnica e verificação manual. Durante o processo, identificamos **três falhas críticas** geradas pelo modelo que foram corrigidas manualmente:

1. **Alucinação de URLs e Links Quebrados (Erro 404):**
   * *Problema detectado:* Na geração inicial da base de conhecimento (`data/base.json`), a IA sugeriu *deep links* governamentais desatualizados ou inexistentes que retornavam erro `HTTP 404` ao serem testados no navegador (especificamente nas rotas da **ANEEL — Tarifa Social**, **Ministério dos Transportes — Passe Livre** e **Caixa Econômica Federal — Saque-Aniversário FGTS**).
   * *Correção aplicada:* Todos os 15 registros foram auditados manualmente no navegador e substituídos por URLs institucionais raiz e rotas oficiais ativas (`gov.br`, `caixa.gov.br`, `poupatempo.sp.gov.br`).

2. **Violação de Escopo Pedagógico (`try/except`):**
   * *Problema detectado:* Durante a unificação do motor de busca (`src/sistema.py`), a IA introduziu blocos de tratamento de exceções (`try/except OSError` e `try/except json.JSONDecodeError`), recurso pertencente à Fase 7 e fora do escopo autorizado.
   * *Correção aplicada:* Refatoramos a função `carregar_base()` para utilizar **programação defensiva baseada estritamente em condicionais puras** (`os.path.exists()`, `os.access(..., os.R_OK)`, `.strip()` e verificação estrutural com `.startswith("{")` / `.startswith("[")`).

3. **Repetições na Experiência do Usuário (UX):**
   * *Problema detectado:* A primeira versão da sugestão de "assuntos relacionados" exibia a própria pergunta recém-consultada pelo usuário na lista de recomendações.
   * *Correção aplicada:* Adicionamos filtro explícito por identificador (`id != id_atual`) e navegação por grafo de temas adjacentes.
