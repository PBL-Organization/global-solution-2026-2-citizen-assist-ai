# Relatório de Testes e Qualidade (QA) — Citizen Assist AI

**Frente Responsável:** Frente D — QA (Qualidade), Métricas de Desempenho & Produção de Vídeo  
**Metodologia:** Bateria empírica de 12 casos de teste cobrindo dúvidas diretas, reformulações, entradas vazias, ambiguidades e consultas fora do escopo, com medição de tempo via módulo nativo `time` (`time.perf_counter()`).

---

## 1. Bateria de Testes (12 Consultas Obrigatórias)

| ID | Categoria | Pergunta / Entrada | Resposta Esperada | Resposta Obtida | Status | Tempo (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | Dúvida Direta | `Como tirar a segunda via do RG?` | Registro ID 1 (Documentação - RG / Poupatempo) | Registro ID 1 (`top_id=1`) com fonte oficial e 3 assuntos relacionados | **Acerto** | 0.4970 |
| **T02** | Dúvida Direta | `Como regularizar a situação do meu CPF?` | Registro ID 2 (Documentação - CPF / Receita Federal) | Registro ID 2 (`top_id=2`) com fonte oficial e 3 assuntos relacionados | **Acerto** | 0.5623 |
| **T03** | Dúvida Direta | `Como consultar minha situação eleitoral?` | Registro ID 3 (Documentação - Título de Eleitor / TSE) | Registro ID 2 (`top_id=2` - CPF, empate/pontuação pela palavra `situacao`) | **Erro** | 0.3421 |
| **T04** | Dúvida Direta | `Como acessar a Carteira de Trabalho Digital?` | Registro ID 4 (Documentação - CTPS Digital / Gov.br) | Registro ID 4 (`top_id=4`) com fonte oficial e 3 assuntos relacionados | **Acerto** | 0.3223 |
| **T05** | Dúvida Direta | `Como tirar 2 via de certidão de nascimento?` | Registro ID 5 (Documentação - Certidão / Registradores.br) | Registro ID 5 (`top_id=5`) com fonte oficial e 3 assuntos relacionados | **Acerto** | 0.3431 |
| **T06** | Dúvida Direta | `Como dar entrada no seguro-desemprego?` | Registro ID 6 (Serviços Públicos - Seguro-Desemprego / Gov.br) | Registro ID 6 (`top_id=6`) com fonte oficial e 3 assuntos relacionados | **Acerto** | 0.3188 |
| **T07** | Reformulação | `perdi meu rg e quero fazer outro` | Registro ID 1 (Documentação - Segunda via de RG) | Registro ID 1 (`top_id=1`) identificado via palavra-chave `rg` | **Acerto** | 0.4911 |
| **T08** | Reformulação | `beneficio de energia barata cadunico` | Registro ID 9 (Serviços Públicos - Tarifa Social de Energia) | Registro ID 7 (`top_id=7` - INSS, por correspondência com `beneficio`) | **Erro** | 0.4763 |
| **T09** | Entrada Vazia | `""` (Enter sem texto) | Validação de entrada vazia sem encerrar ou quebrar o sistema | Aviso exibido: *"A consulta não pode ficar vazia. Digite uma dúvida válida."* | **Acerto** | 0.0085 |
| **T10** | Entrada Vazia | `"   "` (apenas espaços) | Sanitização remove espaços e aciona bloqueio de consulta vazia | Aviso exibido: *"A consulta não pode ficar vazia. Digite uma dúvida válida."* | **Acerto** | 0.0054 |
| **T11** | Ambiguidade | `idoso deficiencia` | Guardrail de ambiguidade (empate entre ID 10 Passe Livre e ID 14 BPC/LOAS) | Guardrail de ambiguidade ativado exibindo ambas as opções próximas | **Acerto** | 0.3735 |
| **T12** | Fora do Escopo | `Como abrir um MEI?` | Guardrail de limitação sem inventar resposta (`score == 0`) | Guardrail ativado informando ausência na base e recomendando canal oficial | **Acerto** | 0.4276 |

---

## 2. Indicadores Empíricos de Desempenho

* **Total de Testes Executados:** 12
* **Total de Acertos:** 10
* **Total de Erros:** 2 (T03 e T08, causados por variação vocabular/sinônimos não indexados)
* **Taxa de Acerto (%):**
  $$\text{Taxa de Acerto} = \left(\frac{10}{12}\right) \times 100 = \mathbf{83,33\%}$$
* **Tempo Médio de Resposta:**
  $$\text{Tempo Médio} = \frac{4,1680\text{ ms}}{12} = \mathbf{0,3473\text{ ms}}$$

---

## 3. Teste de Usabilidade e Melhorias Futuras

* **Perfil do Usuário Avaliado:** 1 usuário externo (sem contato prévio com o código-fonte), executando busca livre, navegação por temas, visualização de assuntos relacionados e encerramento via CLI.
* **Dificuldades Observadas:**
  1. Quando o usuário digita uma dúvida usando sinônimos coloquiais (ex.: *"energia barata"* em vez de *"tarifa social"* ou *"situação eleitoral"* sem a palavra *"título"*), o motor retorna um tema diferente ou aciona o guardrail.
  2. No menu principal em modo texto, o usuário inicialmente não percebeu que precisava digitar o número da opção (`1`, `2`, `3`, `4` ou `0`) antes de escrever a pergunta diretamente.

### Melhorias Futuras Justificadas
1. **Expansão de Sinônimos e Variações Morfológicas (Stemming/Dicionário de Sinônimos):**  
   * *Justificativa:* Nos testes T03 e T08 e no teste de usabilidade, consultas válidas falharam porque o usuário empregou sinônimos (`eleitoral`, `energia barata`, `cadunico`) ausentes da lista `palavras_chave`. Expandir os sinônimos na base JSON ou aplicar normalização de radicais elevaria a taxa de acerto para próximo de 100%.
2. **Atalho de Busca Direta e Feedback Visual Aprimorado no CLI:**  
   * *Justificativa:* Durante o teste de usabilidade, o usuário tentou digitar a pergunta logo na tela inicial do menu. Permitir que qualquer texto digitado diretamente no prompt principal (fora das opções numéricas `0`–`4`) já dispare uma busca livre tornaria a interação mais intuitiva e reduziria erros de entrada.
