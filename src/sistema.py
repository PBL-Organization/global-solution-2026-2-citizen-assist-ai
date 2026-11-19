"""
=============================================================================
PROJETO: Citizen Assist AI (Global Solution 2026.2 - FIAP)
ARQUIVO: sistema.py
FRENTES INTEGRADAS: Frente A (Persistência), Frente B (Busca & Grafo)
                    e Frente C (Guardrails Booleanos & Prompts/Respostas)
DESCRIÇÃO: Script principal contendo menu CLI, carregamento defensivo sem
           try/except (Fases 1-6), busca linear pontuada O(n), grafo de temas,
           guardrails booleanos e formatação estruturada (Modelos A e B).
STACK: Python Puro (Restrito estritamente às Fases 1 a 6 - Sem try/except)
=============================================================================
"""

from __future__ import annotations

import json
import os
import unicodedata
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Registro = Dict[str, object]
Grafo = Dict[str, List[str]]
PONTUACAO_MINIMA = 1

TEMAS_RELACIONADOS: Dict[str, List[str]] = {
    "Documentacao": ["Servicos Publicos", "Direitos e Assistencia"],
    "Servicos Publicos": ["Documentacao", "Direitos e Assistencia"],
    "Direitos e Assistencia": ["Servicos Publicos", "Documentacao"],
}

CHAVES_OBRIGATORIAS = [
    "id",
    "tema",
    "palavras_chave",
    "pergunta_exemplo",
    "orientacao_resumida",
    "referencia_fonte",
    "url_fonte",
    "data_verificacao",
]

# ==============================================================================
# MODELOS DE INSTRUÇÃO E FORMATAÇÃO (FRENTE C - FASE 5)
# ==============================================================================
SYSTEM_PROMPT_MODELO_A = (
    "Você é um assistente de triagem informativa para serviços ao cidadão. "
    "Use EXCLUSIVAMENTE os fatos do contexto oficial, em Linguagem Simples, "
    "sem falar em primeira pessoa como órgão público e incluindo o aviso final."
)

TEMPLATE_RESPOSTA_MODELO_A = (
    "\n============================================================\n"
    "RESULTADO ENCONTRADO (Modelo A - Objetivo | Tema: {tema} | Score: {score})\n"
    "============================================================\n"
    "Resumo:\n"
    "  {orientacao_resumida}\n\n"
    "Detalhes e Orientações:\n"
    "  • Dúvida de referência: {pergunta_exemplo}\n"
    "  • Registro ID: {id_registro}\n\n"
    "Fonte Oficial:\n"
    "  • Órgão: {referencia_fonte}\n"
    "  • Link: {url_fonte}\n"
    "  • Verificado em: {data_verificacao}\n\n"
    "Aviso: Esta é uma resposta informativa gerada por assistente automatizado "
    "e não substitui os canais oficiais. Confirme prazos, taxas e exigências "
    "diretamente no portal oficial indicado antes de realizar sua solicitação.\n"
    "============================================================"
)

SYSTEM_PROMPT_MODELO_B = (
    "Você é um guia digital de orientação cidadã. Seja cordial, didático, "
    "fiel ao contexto oficial e explícito sobre a ausência de vínculo oficial."
)

TEMPLATE_RESPOSTA_MODELO_B = (
    "\n============================================================\n"
    "GUIA CIDADÃO (Modelo B - Didático | Tema: {tema} | Score: {score})\n"
    "============================================================\n"
    "1. O que você precisa saber:\n"
    "  Sobre '{pergunta_exemplo}': {orientacao_resumida}\n\n"
    "2. Checklist de Ação:\n"
    "  1) Leia a orientação acima e confira os requisitos do serviço.\n"
    "  2) Acesse o canal oficial indicado para iniciar ou validar o processo.\n\n"
    "3. Onde essa informação foi consultada:\n"
    "  • Fonte: {referencia_fonte}\n"
    "  • Link oficial: {url_fonte}\n"
    "  • Data de verificação: {data_verificacao}\n\n"
    "4. Aviso de Confirmação:\n"
    "  Aviso: Este atendimento é apenas informativo e não representa um canal "
    "oficial do governo. Valide sempre os dados atualizados no link oficial.\n"
    "============================================================"
)

MENSAGEM_SEM_CORRESPONDENCIA = (
    "\n[GUARDRAIL ATIVADO] Não encontrei informações correspondentes na base "
    "oficial consultada para esta dúvida.\n"
    "Para evitar dados incorretos ou desatualizados, este assistente não gera "
    "respostas sem respaldo documental nem atua como canal oficial.\n"
    "O que fazer: reformule com termos-chave (ex.: RG, CPF, INSS, seguro-desemprego, "
    "FGTS, tarifa social) ou consulte diretamente o portal oficial do órgão.\n"
    "Aviso: Este sistema é um assistente informacional experimental e não "
    "substitui os canais oficiais."
)

MENSAGEM_AMBIGUIDADE_CABECALHO = (
    "\n[GUARDRAIL ATIVADO - AMBIGUIDADE] Sua consulta corresponde a mais de um "
    "registro com a mesma pontuação.\n"
    "Para evitar orientação imprecisa, veja as opções mais próximas encontradas:\n"
)


# ==============================================================================
# PERSISTÊNCIA DEFENSIVA (FRENTE A - FASES 1 A 6, SEM TRY/EXCEPT)
# ==============================================================================
def _caminho_base_padrao() -> str:
    """Resolve o caminho padrão de data/base.json a partir da pasta src/."""
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)
    return os.path.join(raiz_projeto, "data", "base.json")


def carregar_base(caminho: Optional[str] = None) -> List[Registro]:
    """
    Carrega e valida defensivamente a base JSON usando apenas condicionais
    (Fases 1 a 6, sem try/except).
    """
    caminho = caminho or _caminho_base_padrao()

    # 1. Verifica existência física do arquivo no sistema de arquivos
    if not os.path.exists(caminho):
        print(f"[ERRO CRÍTICO] Arquivo de base não encontrado em: {caminho}")
        return []

    # 2. Verifica permissão de leitura antes de abrir o arquivo
    if not os.access(caminho, os.R_OK):
        print(f"[ERRO] Sem permissão de leitura para o arquivo: {caminho}")
        return []

    # 3. Lê o conteúdo bruto em UTF-8
    with open(caminho, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    # 4. Verifica se o arquivo não está vazio ou só com espaços
    conteudo_limpo = conteudo.strip()
    if not conteudo_limpo:
        print("[AVISO] O arquivo base.json está vazio.")
        return []

    # 5. Valida início estrutural de JSON ('{' para objeto ou '[' para lista)
    if not (conteudo_limpo.startswith("{") or conteudo_limpo.startswith("[")):
        print("[ERRO] O conteúdo do arquivo não possui estrutura JSON válida.")
        return []

    dados = json.loads(conteudo)

    if isinstance(dados, dict) and isinstance(dados.get("registros"), list):
        lista_registros = dados["registros"]
    elif isinstance(dados, list):
        lista_registros = dados
    else:
        print("[ERRO] Formato da base inválido.")
        return []

    registros_validados: List[Registro] = []
    for registro in lista_registros:
        if not isinstance(registro, dict):
            continue
        if all(chave in registro for chave in CHAVES_OBRIGATORIAS):
            registros_validados.append(registro)

    return registros_validados


# ==============================================================================
# MOTOR DE BUSCA E NAVEGAÇÃO EM GRAFO (FRENTE B - O(n))
# ==============================================================================
def _sem_acentos(texto: str) -> str:
    """Remove acentos e marcas diacríticas mantendo caracteres base."""
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(
        caractere
        for caractere in normalizado
        if unicodedata.category(caractere) != "Mn"
    )


def sanitizar_texto(texto: str) -> List[str]:
    """Normaliza texto, remove acentos e pontuação e retorna lista de tokens."""
    texto_limpo = _sem_acentos(str(texto).lower().strip())
    caracteres_validos: List[str] = []
    for caractere in texto_limpo:
        if caractere.isalnum() or caractere.isspace():
            caracteres_validos.append(caractere)
        else:
            caracteres_validos.append(" ")
    return "".join(caracteres_validos).split()


def _tokens_palavras_chave(palavras_chave: Iterable[object]) -> List[str]:
    """Tokeniza e normaliza todas as palavras-chave de um registro."""
    tokens: List[str] = []
    for palavra in palavras_chave:
        tokens.extend(sanitizar_texto(str(palavra)))
    return tokens


def pontuar_registro(tokens_usuario: Sequence[str], registro: Registro) -> int:
    """Calcula a pontuação pela interseção com palavras-chave e termos compostos."""
    palavras_chave = registro.get("palavras_chave", [])
    if not isinstance(palavras_chave, list):
        return 0

    tokens_chave = set(_tokens_palavras_chave(palavras_chave))
    score = len(set(tokens_usuario).intersection(tokens_chave))
    consulta = " ".join(tokens_usuario)

    for palavra in palavras_chave:
        chave = " ".join(sanitizar_texto(str(palavra)))
        if chave and " " in chave and chave in consulta:
            score += 1

    return score


def _criterio_desempate(registro: Registro, indice: int) -> Tuple[int, str, int]:
    """Define critério determinístico de desempate sem usar try/except."""
    id_val = registro.get("id", indice + 1)
    if isinstance(id_val, int):
        identificador = id_val
    elif isinstance(id_val, str) and id_val.isdigit():
        identificador = int(id_val)
    else:
        identificador = indice + 1

    return (
        identificador,
        str(registro.get("pergunta_exemplo", "")).casefold(),
        indice,
    )


def buscar_orientacoes(
    tokens_usuario: Sequence[str], registros: Sequence[Registro]
) -> List[Tuple[int, Registro]]:
    """Executa busca linear O(n) ordenada por score decrescente e desempate."""
    resultados: List[Tuple[int, Registro, int]] = []
    for indice, registro in enumerate(registros):
        score = pontuar_registro(tokens_usuario, registro)
        if score >= PONTUACAO_MINIMA:
            resultados.append((score, registro, indice))

    resultados.sort(
        key=lambda item: (-item[0], _criterio_desempate(item[1], item[2]))
    )
    return [(score, registro) for score, registro, _ in resultados]


def buscar_orientacao(
    tokens_usuario: Sequence[str], registros: Sequence[Registro]
) -> Optional[Registro]:
    """Retorna apenas o registro melhor pontuado, ou None se não houver match."""
    resultados = buscar_orientacoes(tokens_usuario, registros)
    return resultados[0][1] if resultados else None


def construir_grafo(registros: Sequence[Registro]) -> Grafo:
    """Constrói um grafo de adjacência (dicionário de listas) entre os temas."""
    temas: List[str] = []
    for registro in registros:
        tema = str(registro.get("tema", "")).strip()
        if tema and tema not in temas:
            temas.append(tema)

    grafo: Grafo = {tema: [] for tema in temas}
    for tema in temas:
        vizinhos_preferenciais = TEMAS_RELACIONADOS.get(tema, [])
        grafo[tema] = [vizinho for vizinho in vizinhos_preferenciais if vizinho in grafo]
        if not grafo[tema]:
            grafo[tema] = [outro for outro in temas if outro != tema]

    return grafo


def assuntos_relacionados(
    registro: Registro,
    registros: Sequence[Registro],
    grafo: Grafo,
    limite: int = 3,
) -> List[Registro]:
    """Busca registros relacionados no mesmo tema e nos temas vizinhos do grafo."""
    tema = str(registro.get("tema", ""))
    temas_visitados = [tema] + grafo.get(tema, [])
    relacionados: List[Registro] = []

    for tema_visitado in temas_visitados:
        for candidato in registros:
            if candidato is registro or candidato in relacionados:
                continue
            if str(candidato.get("tema", "")) == tema_visitado:
                relacionados.append(candidato)
                if len(relacionados) >= limite:
                    return relacionados

    return relacionados


# ==============================================================================
# GUARDRAILS BOOLEANOS E PREPARAÇÃO DE RESPOSTA (FRENTE C - FASES 3 E 5)
# ==============================================================================
def montar_estado_recuperacao(
    resultados: Sequence[Tuple[int, Registro]],
    base_completa: Sequence[Registro],
) -> Dict[str, object]:
    """
    Consolida os sinais da recuperação para avaliação booleana dos guardrails.
    """
    dentro_do_dominio = len(base_completa) > 0

    if not resultados:
        return {
            "score_principal": 0,
            "dentro_do_dominio": dentro_do_dominio,
            "is_ambiguous": False,
            "candidatos_ambiguos": [],
            "registro_vencedor": None,
        }

    score_principal, registro_vencedor = resultados[0]

    # Detecta ambiguidade quando há empate exato no maior score (> 0)
    empatados: List[Registro] = []
    for score_item, reg_item in resultados:
        if score_item == score_principal and score_principal > 0:
            empatados.append(reg_item)

    is_ambiguous = len(empatados) > 1
    candidatos_ambiguos = [
        f"[{reg.get('tema')}] {reg.get('pergunta_exemplo')}"
        for reg in empatados[:3]
    ]

    return {
        "score_principal": score_principal,
        "dentro_do_dominio": dentro_do_dominio,
        "is_ambiguous": is_ambiguous,
        "candidatos_ambiguos": candidatos_ambiguos,
        "registro_vencedor": registro_vencedor,
    }


def avaliar_guardrails(estado: Dict[str, object]) -> Dict[str, object]:
    """
    Expressão booleana simplificada de bloqueio:
      acionar_guardrail = sem_correspondencia or fora_do_escopo or ambigua
    """
    score_principal = int(estado.get("score_principal", 0))
    dentro_do_dominio = bool(estado.get("dentro_do_dominio", False))
    is_ambiguous = bool(estado.get("is_ambiguous", False))

    sem_correspondencia = score_principal == 0
    fora_do_escopo = not dentro_do_dominio
    ambigua = is_ambiguous

    acionar_guardrail = sem_correspondencia or fora_do_escopo or ambigua

    if not acionar_guardrail:
        return {
            "permitido": True,
            "motivo": None,
            "mensagem": None,
        }

    if sem_correspondencia or fora_do_escopo:
        return {
            "permitido": False,
            "motivo": "SEM_CORRESPONDENCIA_OU_FORA_ESCOPO",
            "mensagem": MENSAGEM_SEM_CORRESPONDENCIA,
        }

    candidatos = estado.get("candidatos_ambiguos", [])
    linhas_candidatos = ""
    if isinstance(candidatos, list):
        for item in candidatos:
            linhas_candidatos += f"  • {item}\n"

    mensagem_ambigua = (
        MENSAGEM_AMBIGUIDADE_CABECALHO
        + linhas_candidatos
        + "Aviso: Este sistema é um assistente informacional e não substitui "
          "os canais oficiais."
    )
    return {
        "permitido": False,
        "motivo": "CONSULTA_AMBIGUA",
        "mensagem": mensagem_ambigua,
    }


def formatar_resposta_estruturada(
    registro: Registro,
    score: int,
    modelo: str = "A",
) -> str:
    """
    Formata a resposta final usando os modelos A (objetivo) ou B (didático),
    preservando rigorosamente os dados auditados da base.
    """
    dados_formatacao = {
        "id_registro": registro.get("id", "N/A"),
        "tema": registro.get("tema", "não informado"),
        "pergunta_exemplo": registro.get("pergunta_exemplo", "não informada"),
        "orientacao_resumida": registro.get("orientacao_resumida", "não informada"),
        "referencia_fonte": registro.get("referencia_fonte", "não informada"),
        "url_fonte": registro.get("url_fonte", "não informada"),
        "data_verificacao": registro.get("data_verificacao", "não informada"),
        "score": score,
    }

    if modelo.upper() == "B":
        return TEMPLATE_RESPOSTA_MODELO_B.format(**dados_formatacao)
    return TEMPLATE_RESPOSTA_MODELO_A.format(**dados_formatacao)


def exibir_relacionados(
    registro: Registro,
    registros: Sequence[Registro],
    grafo: Grafo,
    limite: int = 3,
) -> None:
    """Exibe sugestões relacionadas ao resultado encontrado via grafo."""
    print("\n--- Assuntos relacionados (navegação pelo grafo) ---")
    relacionados = assuntos_relacionados(registro, registros, grafo, limite)

    if not relacionados:
        print("  (Nenhuma outra sugestão cadastrada neste tema)")
        return

    for indice, relacionado in enumerate(relacionados, start=1):
        print(
            f"  {indice}. [{relacionado.get('tema')}] "
            f"{relacionado.get('pergunta_exemplo')}"
        )


# ==============================================================================
# INTERFACE CLI E FLUXO PRINCIPAL
# ==============================================================================
def escolher_opcao(mensagem: str, opcoes_validas: Sequence[str]) -> str:
    """Solicita uma opção válida até que o usuário informe uma entrada aceita."""
    while True:
        opcao = input(mensagem).strip()
        if opcao in opcoes_validas:
            return opcao
        print(f"[ERRO] Opção inválida. Escolha: {', '.join(opcoes_validas)}.")


def escolher_tema(registros: Sequence[Registro]) -> Optional[str]:
    """Lista os temas disponíveis e retorna o tema escolhido ou None."""
    temas: List[str] = []
    for registro in registros:
        tema = str(registro.get("tema", "")).strip()
        if tema and tema not in temas:
            temas.append(tema)

    if not temas:
        print("[AVISO] Não há temas cadastrados.")
        return None

    print("\n--- Temas disponíveis ---")
    for indice, tema in enumerate(temas, start=1):
        print(f"[{indice}] {tema}")

    while True:
        escolha = input("Escolha o número do tema (ou 0 para voltar): ").strip()
        if escolha == "0":
            return None
        if escolha.isdigit() and 1 <= int(escolha) <= len(temas):
            return temas[int(escolha) - 1]
        print("[ERRO] Selecione um número válido ou 0 para voltar.")


def consultar(
    pergunta: str,
    registros_escopo: Sequence[Registro],
    grafo: Grafo,
    base_completa: Optional[Sequence[Registro]] = None,
    modelo: str = "A",
) -> None:
    """
    Executa o pipeline completo: sanitização -> busca O(n) -> guardrails
    booleanos -> formatação estruturada -> sugestões via grafo.
    """
    base_referencia = base_completa if base_completa is not None else registros_escopo
    tokens = sanitizar_texto(pergunta)

    if not tokens:
        print("[AVISO] A consulta não pode ficar vazia. Digite uma dúvida válida.")
        return

    resultados = buscar_orientacoes(tokens, registros_escopo)
    estado = montar_estado_recuperacao(resultados, base_referencia)
    decisao = avaliar_guardrails(estado)

    if not bool(decisao.get("permitido", False)):
        print(str(decisao.get("mensagem", MENSAGEM_SEM_CORRESPONDENCIA)))
        return

    score_vencedor = int(estado["score_principal"])
    registro_vencedor = estado["registro_vencedor"]
    if not isinstance(registro_vencedor, dict):
        print(MENSAGEM_SEM_CORRESPONDENCIA)
        return

    print(formatar_resposta_estruturada(registro_vencedor, score_vencedor, modelo=modelo))
    exibir_relacionados(registro_vencedor, base_referencia, grafo)


def main() -> None:
    registros = carregar_base()
    if not registros:
        print("[ERRO] Sistema encerrado por falta de dados válidos na base.")
        return

    grafo = construir_grafo(registros)
    modelo_ativo = "A"

    print("=" * 60)
    print("      CITIZEN ASSIST AI - ORIENTAÇÃO CIDADÃ INTELIGENTE")
    print("=" * 60)
    print(f"Base carregada com sucesso. Total de registros validados: {len(registros)}")

    while True:
        print(f"\n[Modelo de resposta ativo: {modelo_ativo}]")
        print("[1] Fazer busca livre")
        print("[2] Navegar por temas")
        print("[3] Listar todos os temas e conexões do grafo")
        print("[4] Alternar estilo de resposta (Modelo A / Modelo B)")
        print("[0] Sair do sistema")

        opcao = escolher_opcao("Escolha uma opção: ", ["0", "1", "2", "3", "4"])

        if opcao == "0":
            print("\nEncerrando o Citizen Assist AI. Até logo!")
            break

        if opcao == "1":
            consultar(
                input("Digite sua dúvida: "),
                registros,
                grafo,
                base_completa=registros,
                modelo=modelo_ativo,
            )

        elif opcao == "2":
            tema = escolher_tema(registros)
            if tema is None:
                continue

            filtrados = [
                registro for registro in registros if registro.get("tema") == tema
            ]
            print(f"\n--- Orientações de {tema} ---")
            for registro in filtrados:
                print(f"• {registro.get('pergunta_exemplo')}")

            pergunta = input(
                "Digite uma dúvida para buscar neste tema (ou Enter para voltar): "
            )
            if pergunta.strip():
                consultar(
                    pergunta,
                    filtrados,
                    grafo,
                    base_completa=registros,
                    modelo=modelo_ativo,
                )

        elif opcao == "3":
            print("\n--- Temas cadastrados e conexões do grafo ---")
            for tema, vizinhos in grafo.items():
                conexoes = ", ".join(vizinhos) or "nenhum"
                print(f"• {tema} (relacionado a: {conexoes})")

        else:
            modelo_ativo = "B" if modelo_ativo == "A" else "A"
            print(f"\n[OK] Estilo de resposta alterado para Modelo {modelo_ativo}.")


if __name__ == "__main__":
    main()
