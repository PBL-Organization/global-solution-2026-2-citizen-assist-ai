"""
=============================================================================
PROJETO: Citizen Assist AI (Global Solution 2026.2 - FIAP)
ARQUIVO: sistema.py
FRENTE RESPONSÁVEL: Frente A (Persistência) & Frente B (Core e Busca)
DESCRIÇÃO: Script principal contendo o menu CLI, sanitização de texto,
           busca linear pontuada, fontes auditadas e navegação por temas.
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


def _caminho_base_padrao() -> str:
    raiz = os.path.dirname(os.path.abspath(__file__))
    # Ajuste para buscar na pasta data/ na raiz do projeto
    return os.path.join(os.path.dirname(raiz), "data", "base.json")


def carregar_base(caminho: Optional[str] = None) -> List[Registro]:
    """
    Carrega e valida defensivamente a base JSON utilizando estritamente
    programação defensiva condicional (Fases 1 a 6, sem try/except).
    """
    caminho = caminho or _caminho_base_padrao()

    # 1. Validação física: Verifica se o arquivo existe no disco
    if not os.path.exists(caminho):
        print(f"[ERRO CRÍTICO] Arquivo de base não encontrado em: {caminho}")
        return []

    # 2. Validação condicional de permissão de leitura (Substitui tratamento de OSError)
    if not os.access(caminho, os.R_OK):
        print(f"[ERRO] Sem permissão de leitura para o arquivo: {caminho}")
        return []

    # Leitura segura do fluxo de texto bruto
    with open(caminho, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    # 3. Validação condicional de conteúdo vazio
    conteudo_limpo = conteudo.strip()
    if not conteudo_limpo:
        print("[AVISO] O arquivo base.json está vazio.")
        return []

    # 4. Validação estrutural defensiva (Substitui o JSONDecodeError da Fase 7)
    # Um JSON válido em Python deve iniciar obrigatoriamente com '{' ou '['
    if not (conteudo_limpo.startswith("{") or conteudo_limpo.startswith("[")):
        print("[ERRO] O conteúdo do arquivo não possui uma estrutura JSON válida.")
        return []

    # Decodificação segura após as barreiras condicionais
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


def _sem_acentos(texto: str) -> str:
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(
        caractere
        for caractere in normalizado
        if unicodedata.category(caractere) != "Mn"
    )


def sanitizar_texto(texto: str) -> List[str]:
    """Normaliza texto, remove acentos e pontuação e retorna tokens."""
    texto_limpo = _sem_acentos(str(texto).lower().strip())
    caracteres_validos: List[str] = []
    for caractere in texto_limpo:
        if caractere.isalnum() or caractere.isspace():
            caracteres_validos.append(caractere)
        else:
            caracteres_validos.append(" ")
    return "".join(caracteres_validos).split()


def _tokens_palavras_chave(palavras_chave: Iterable[object]) -> List[str]:
    tokens: List[str] = []
    for palavra in palavras_chave:
        tokens.extend(sanitizar_texto(str(palavra)))
    return tokens


def pontuar_registro(tokens_usuario: Sequence[str], registro: Registro) -> int:
    """Calcula a pontuação pela interseção com as palavras-chave."""
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
    # Substituindo try/except interno por checagem condicional de tipo
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
    """Realiza busca linear O(n), ordenada por score e desempate determinístico."""
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
    """Mantém a API original e retorna somente o melhor resultado."""
    resultados = buscar_orientacoes(tokens_usuario, registros)
    return resultados[0][1] if resultados else None


def construir_grafo(registros: Sequence[Registro]) -> Grafo:
    """Cria um grafo de adjacência entre os temas presentes na base."""
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
    """Obtém registros do tema atual e dos temas vizinhos no grafo."""
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


def exibir_relacionados(
    registro: Registro,
    registros: Sequence[Registro],
    grafo: Grafo,
    limite: int = 3,
) -> None:
    """Exibe sugestões relacionadas ao resultado encontrado."""
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


def exibir_resultado(registro: Registro, score: Optional[int] = None) -> None:
    """Exibe uma orientação e suas fontes auditadas."""
    print("\n" + "=" * 60)
    print(f"RESULTADO ENCONTRADO (Tema: {registro.get('tema', 'não informado')})")
    print("=" * 60)
    print(f"Dúvida relacionada: {registro.get('pergunta_exemplo', 'não informada')}")
    print(f"Orientação: {registro.get('orientacao_resumida', 'não informada')}")
    print(f"Fonte oficial: {registro.get('referencia_fonte', 'não informada')}")
    if registro.get("url_fonte"):
        print(f"Link oficial: {registro.get('url_fonte')}")
    print(f"Data de verificação: {registro.get('data_verificacao', 'não informada')}")
    if score is not None:
        print(f"Pontuação da busca: {score}")
    print("Aviso: confirme a informação nos canais oficiais antes de tomar decisões.")
    print("=" * 60)


def escolher_opcao(mensagem: str, opcoes_validas: Sequence[str]) -> str:
    """Solicita uma opção até que o usuário informe uma alternativa válida."""
    while True:
        opcao = input(mensagem).strip()
        if opcao in opcoes_validas:
            return opcao
        print(f"[ERRO] Opção inválida. Escolha: {', '.join(opcoes_validas)}.")


def escolher_tema(registros: Sequence[Registro]) -> Optional[str]:
    """Exibe os temas e permite selecionar um deles."""
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


def consultar(pergunta: str, registros: Sequence[Registro], grafo: Grafo) -> None:
    """Processa uma consulta livre e mostra o melhor resultado."""
    tokens = sanitizar_texto(pergunta)
    if not tokens:
        print("[AVISO] A consulta não pode ficar vazia. Digite uma dúvida válida.")
        return

    resultados = buscar_orientacoes(tokens, registros)
    if not resultados:
        print("\n[GUARDRAIL ATIVADO] Não encontrei orientação correspondente na base curada.")
        print(
            "Não vou inventar uma resposta. Consulte um canal oficial ou tente "
            "RG, CPF, INSS ou seguro-desemprego."
        )
        return

    score, resultado = resultados[0]
    exibir_resultado(resultado, score)
    exibir_relacionados(resultado, registros, grafo)


def main() -> None:
    registros = carregar_base()
    if not registros:
        print("[ERRO] Sistema encerrado por falta de dados na base.")
        return

    grafo = construir_grafo(registros)
    print("=" * 60)
    print("      CITIZEN ASSIST AI - ORIENTAÇÃO CIDADÃ INTELIGENTE")
    print("=" * 60)
    print(f"Base carregada com sucesso. Total de registros validados: {len(registros)}")

    while True:
        print("\n[1] Fazer busca livre")
        print("[2] Navegar por temas")
        print("[3] Listar todos os temas")
        print("[0] Sair do sistema")
        opcao = escolher_opcao("Escolha uma opção: ", ["0", "1", "2", "3"])

        if opcao == "0":
            print("\nEncerrando o Citizen Assist AI. Até logo!")
            break

        if opcao == "1":
            consultar(input("Digite sua dúvida: "), registros, grafo)

        elif opcao == "2":
            tema = escolher_tema(registros)
            if tema is None:
                continue

            filtrados = [registro for registro in registros if registro.get("tema") == tema]
            print(f"\n--- Orientações de {tema} ---")
            for registro in filtrados:
                print(f"• {registro.get('pergunta_exemplo')}")

            pergunta = input(
                "Digite uma dúvida para buscar neste tema (ou Enter para voltar): "
            )
            if pergunta.strip():
                consultar(pergunta, filtrados, grafo)

        else:
            print("\n--- Temas cadastrados e conexões do grafo ---")
            for tema, vizinhos in grafo.items():
                conexoes = ", ".join(vizinhos) or "nenhum"
                print(f"• {tema} (relacionado a: {conexoes})")


if __name__ == "__main__":
    main()