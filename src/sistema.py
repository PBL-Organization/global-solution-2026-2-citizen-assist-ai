"""
=============================================================================
PROJETO: Citizen Assist AI (Global Solution 2026.2 - FIAP)
ARQUIVO: sistema.py
FRENTE RESPONSÁVEL: Frente B (Core Backend, Algoritmos de Busca & Navegação)
DESCRIÇÃO: Script principal contendo o menu CLI, pipeline de sanitização de 
           texto, busca linear pontuada (score) e exibição de fontes auditadas.
STACK: Python Puro (Restrito às Fases 1 a 6)
=============================================================================
"""

import os
import json

def carregar_base(caminho: str = "data/base.json") -> list:
    #Carrega a base de conhecimento de forma defensiva
    if not os.path.exists(caminho):
        print(f"[ERRO CRÍTICO] Arquivo de base não encontrado em: {caminho}")
        return []
    
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
        
    if not conteudo.strip():
        print("[AVISO] O arquivo base.json está vazio.")
        return []
        
    dados = json.loads(conteudo)
    if isinstance(dados, dict) and "registros" in dados:
        return dados["registros"]
    elif isinstance(dados, list):
        return dados
    return []

def sanitizar_texto(texto: str) -> list:
    #Normaliza o texto do usuário: transforma em minúsculas e quebra em tokens.
    texto_limpo = texto.lower().strip()
    # Remove pontuações simples manualmente (Python puro)
    for char in ["?", "!", ".", ",", ";", ":", "-", '"', "'"]:
        texto_limpo = texto_limpo.replace(char, "")
    return texto_limpo.split()

def buscar_orientacao(tokens_usuario: list, registros: list) -> dict:
    """
    Executa busca linear O(n) pontuada (score) cruzando os tokens do usuário
    com as palavras-chave cadastradas no JSON.
    """
    melhor_registro = None
    maior_score = 0

    for reg in registros:
        score = 0
        palavras_chave = reg.get("palavras_chave", [])
        
        # Conta quantas palavras da consulta batem com as palavras-chave do registro
        for token in tokens_usuario:
            if token in palavras_chave:
                score += 1
                
        if score > maior_score:
            maior_score = score
            melhor_registro = reg

    # Se encontrou ao menos 1 correspondência relevante
    if maior_score > 0:
        return melhor_registro
    return None

def exibir_relacionados(tema_atual: str, registros: list):
    """Simula a navegação por grafo/temas relacionados (Fase 4)."""
    print("\n--- Assuntos Relacionados no Mesma Tema ---")
    encontrados = 0
    for reg in registros:
        if reg.get("tema") == tema_atual and encontrados < 2:
            print(f"• Dúvida: {reg.get('pergunta_exemplo')}")
            encontrados += 1

def main():
    registros = carregar_base()
    if not registros:
        print("[ERRO] Sistema encerrado por falta de dados na base.")
        return

    print("=" * 60)
    print("      CITIZEN ASSIST AI - ORIENTAÇÃO CIDADÃ INTELIGENTE")
    print("=" * 60)
    print(f"Base carregada com sucesso. Total de registros: {len(registros)}")

    while True:
        print("\n[1] Consultar Dúvida")
        print("[2] Listar Todos os Temas Disponíveis")
        print("[0] Sair do Sistema")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "0":
            print("\nEncerrando o Citizen Assist AI. Até logo!")
            break
            
        elif opcao == "1":
            pergunta = input("\nDigite sua dúvida (ex: Como tirar 2 via do RG?): ")
            tokens = sanitizar_texto(pergunta)
            
            if not tokens:
                print("[AVISO] Por favor, digite uma consulta válida.")
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
                
                # Exibe navegação complementar
                exibir_relacionados(resultado.get('tema'), registros)
            else:
                print("\n[GUARDRAIL ATIVADO] Não encontrei orientações específicas para sua busca.")
                print("Dica: Tente usar palavras-chave mais diretas (ex: 'rg', 'cpf', 'seguro-desemprego').")
                
        elif opcao == "2":
            print("\n--- Temas Cadastrados na Base ---")
            temas = []
            for r in registros:
                t = r.get("tema")
                if t not in temas:
                    temas.append(t)
            for t in temas:
                print(f"• {t}")
        else:
            print("\n[ERRO] Opção inválida. Escolha 1, 2 ou 0.")

if __name__ == "__main__":
    main()