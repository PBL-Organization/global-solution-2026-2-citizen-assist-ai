"""
=============================================================================
PROJETO: Citizen Assist AI (Global Solution 2026.2 - FIAP)
ARQUIVO: sistema.py
FRENTE RESPONSÁVEL: Frente B (Core Backend, Algoritmos de Busca & Navegação)
INTEGRANTE: Squad CitizenTech
DESCRIÇÃO: Script principal contendo o menu CLI, pipeline de sanitização de 
           texto, busca linear pontuada (score), exibição de fontes auditadas 
           e arquitetura de descoberta dinâmica de UX.
STACK: Python Puro (Restrito estritamente às Fases 1 a 6)
=============================================================================
"""

import os
import json

def carregar_base(caminho: str = "data/base.json") -> list:
    """
    Realiza a leitura defensiva da base de conhecimento JSON sem utilizar try/except.
    Conforme diretrizes das Fases 1 a 6, utiliza validações condicionais puras.
    """
    if not os.path.exists(caminho):
        print(f"[ERRO CRÍTICO] Arquivo de base não encontrado em: {caminho}")
        return []
    
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
        
    if not conteudo.strip():
        print("[AVISO] O arquivo base.json está vazio.")
        return []
        
    dados = json.loads(conteudo)
    
    # Extração segura da lista de registros
    if isinstance(dados, dict) and "registros" in dados:
        lista_registros = dados["registros"]
    elif isinstance(dados, list):
        lista_registros = dados
    else:
        lista_registros = []

    # Validação defensiva de chaves obrigatórias por registro
    chaves_obrigatorias = [
        "id", "tema", "palavras_chave", 
        "pergunta_exemplo", "orientacao_resumida", 
        "referencia_fonte", "url_fonte", "data_verificacao"
    ]
    
    registros_validados = []
    for reg in lista_registros:
        valido = True
        for chave in chaves_obrigatorias:
            if chave not in reg:
                valido = False
                break
        if valido:
            registros_validados.append(reg)

    return registros_validados

def sanitizar_texto(texto: str) -> list:
    """
    Pipeline de normalização textual: converte para minúsculas, remove 
    pontuações básicas e quebra a frase em tokens (lista de palavras).
    """
    texto_limpo = texto.lower().strip()
    for char in ["?", "!", ".", ",", ";", ":", "-", '"', "'", "º", "°"]:
        texto_limpo = texto_limpo.replace(char, "")
    return texto_limpo.split()

def buscar_orientacao(tokens_usuario: list, registros: list) -> dict:
    """
    Algoritmo de Busca Linear O(n) com pontuação (Score Heurístico).
    Cruza os tokens da consulta com as palavras-chave cadastradas no JSON.
    """
    melhor_registro = None
    maior_score = 0

    for reg in registros:
        score = 0
        palavras_chave = reg.get("palavras_chave", [])
        
        for token in tokens_usuario:
            if token in palavras_chave:
                score += 1
                
        if score > maior_score:
            maior_score = score
            melhor_registro = reg

    if maior_score > 0:
        return melhor_registro
    return None

def exibir_relacionados(tema_atual: str, id_atual: int, registros: list):
    """
    Módulo de UX (Arquitetura de Descoberta): exibe uma mini-lista dinâmica 
    de sugestões do mesmo tema, filtrando e excluindo o ID atual exibido.
    """
    print("\n--- 💡 Você também pode querer saber sobre ---")
    encontrados = 0
    for reg in registros:
        if reg.get("tema") == tema_atual and reg.get("id") != id_atual:
            print(f"  ▪ {reg.get('pergunta_exemplo')}")
            encontrados += 1
            if encontrados >= 3:  # Limita a 3 sugestões limpas na tela
                break
                
    if encontrados == 0:
        print("  (Nenhuma outra sugestão cadastrada neste tema)")

def main():
    registros = carregar_base()
    if not registros:
        print("[ERRO] Sistema encerrado. Verifique o arquivo data/base.json.")
        return

    print("=" * 60)
    print("      CITIZEN ASSIST AI - ORIENTAÇÃO CIDADÃ INTELIGENTE")
    print("=" * 60)
    print(f"Base carregada com sucesso. Total de registros validados: {len(registros)}")

    while True:
        print("\n[1] Consultar Dúvida Cidadã")
        print("[2] Listar Todos os Temas Disponíveis")
        print("[0] Encerrar Sistema")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "0":
            print("\nEncerrando o Citizen Assist AI. Bom trabalho, engenheiro!")
            break
            
        elif opcao == "1":
            pergunta = input("\nDigite sua dúvida (ex: Como tirar 2 via do RG?): ")
            tokens = sanitizar_texto(pergunta)
            
            if not tokens:
                print("[AVISO] Entrada vazia. Por favor, digite uma consulta válida.")
                continue
                
            resultado = buscar_orientacao(tokens, registros)
            
            if resultado:
                print("\n" + "=" * 50)
                print(f"RESULTADO ENCONTRADO (Tema: {resultado.get('tema')})")
                print("=" * 50)
                print(f"Dúvida: {resultado.get('pergunta_exemplo')}")
                print(f"Orientação: {resultado.get('orientacao_resumida')}")
                print(f"Órgão/Fonte: {resultado.get('referencia_fonte')}")
                print(f"Link Oficial: {resultado.get('url_fonte')}")
                print(f"Data de Verificação: {resultado.get('data_verificacao')}")
                print("=" * 50)
                
                # Executa a arquitetura de descoberta de UX
                exibir_relacionados(resultado.get('tema'), resultado.get('id'), registros)
            else:
                print("\n[GUARDRAIL ATIVADO] Não encontrei orientações específicas para sua busca.")
                print("Dica: Tente usar termos-chave mais diretos (ex: 'rg', 'cpf', 'seguro-desemprego').")
                
        elif opcao == "2":
            print("\n--- Temas Cadastrados na Base ---")
            temas = []
            for r in registros:
                t = r.get("tema")
                if t not in temas:
                    temas.append(t)
            for t in temas:
                print(f"  • {t}")
        else:
            print("\n[ERRO] Opção inválida. Escolha 1, 2 ou 0 no menu.")

if __name__ == "__main__":
    main()