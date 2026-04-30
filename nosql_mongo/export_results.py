#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para exportar resultados das 8 queries para CSV
Cada resultado é salvo em um arquivo CSV pronto para visualização
"""

import os
import csv
from datetime import datetime
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    raise RuntimeError('MONGO_URI não encontrado no .env')

DB_NAME = "enade_db"

# Configurações de exportação
EXPORT_DIR = "resultados_graficos"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Definição das 8 queries e seus campos
QUERIES = {
    "Q1": {
        "collection": "res_q1_ranking_cursos",
        "titulo": "Ranking de Cursos por Desempenho",
        "campos": ["curso", "qtd_alunos", "media_nota_geral"]
    },
    "Q2": {
        "collection": "res_q2_desempenho_uf_regiao",
        "titulo": "Desempenho por UF e Região",
        "campos": ["uf", "regiao", "qtd_alunos", "media_nota"]
    },
    "Q3": {
        "collection": "res_q3_gap_publico_privado",
        "titulo": "Gap Público vs Privado por Curso",
        "campos": ["curso", "categoria", "qtd", "media_nota"]
    },
    "Q4": {
        "collection": "res_q4_primeira_geracao",
        "titulo": "Primeira Geração vs Escolaridade Parental",
        "campos": ["primeira_geracao", "escolaridade_pai", "qtd", "media_nota"]
    },
    "Q5": {
        "collection": "res_q5_jornada_trabalho",
        "titulo": "Jornada de Trabalho vs Desempenho",
        "campos": ["jornada", "qtd", "media_nota", "min_nota", "max_nota"]
    },
    "Q6": {
        "collection": "res_q6_avaliacao_infraestrutura",
        "titulo": "Avaliação de Infraestrutura vs Desempenho",
        "campos": ["avaliacao_equipamentos", "qtd", "media_nota"]
    },
    "Q7": {
        "collection": "res_q7_vulnerabilidade",
        "titulo": "Vulnerabilidade Econômica por Faixa de Desempenho",
        "campos": ["faixa_nota", "renda_familiar", "qtd"]
    },
    "Q8": {
        "collection": "res_q8_delta_municipio_uf",
        "titulo": "Delta Município vs Média Estadual",
        "campos": ["municipio", "uf", "media_nota_municipio", "media_nota_uf", "delta"]
    }
}

def criar_diretorio():
    """Cria diretório de exportação se não existir"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"✓ Diretório criado: {EXPORT_DIR}")

def conectar_mongodb():
    """Conecta ao MongoDB Atlas"""
    try:
        client = MongoClient(MONGO_URI)
        # Verificar conexão
        client.admin.command('ping')
        print("✓ Conectado ao MongoDB")
        return client
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        raise

def obter_documentos(db, colecao):
    """Obtém todos os documentos de uma coleção"""
    try:
        docs = list(db[colecao].find({}))
        return docs
    except Exception as e:
        print(f"✗ Erro ao buscar {colecao}: {e}")
        return []

def limpar_documento(doc, campos_desejados):
    """Remove _id e campos indesejados, mantém só os campos desejados"""
    doc_limpo = {}
    
    # Se a lista de campos foi definida, manter apenas esses
    if campos_desejados:
        for campo in campos_desejados:
            if campo in doc:
                valor = doc[campo]
                # Formatar valores decimais com 2 casas
                if isinstance(valor, float):
                    doc_limpo[campo] = round(valor, 2)
                else:
                    doc_limpo[campo] = valor
            else:
                doc_limpo[campo] = ""
    else:
        # Se não houver campos definidos, manter todos menos _id
        for chave, valor in doc.items():
            if chave != "_id":
                if isinstance(valor, float):
                    doc_limpo[chave] = round(valor, 2)
                else:
                    doc_limpo[chave] = valor
    
    return doc_limpo

def exportar_csv(colecao, docs, nome_arquivo, campos):
    """Exporta documentos para CSV"""
    if not docs:
        print(f"  ⚠ Nenhum documento em {colecao}")
        return 0
    
    caminho = os.path.join(EXPORT_DIR, nome_arquivo)
    
    try:
        # Limpar documentos
        docs_limpos = [limpar_documento(doc, campos) for doc in docs]
        
        # Determinar campos do CSV
        campos_csv = campos if campos else list(docs_limpos[0].keys())
        
        # Escrever CSV
        with open(caminho, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos_csv)
            writer.writeheader()
            writer.writerows(docs_limpos)
        
        print(f"  ✓ {nome_arquivo} ({len(docs)} linhas)")
        return len(docs)
    except Exception as e:
        print(f"  ✗ Erro ao exportar {nome_arquivo}: {e}")
        return 0

def exportar_json(colecao, docs, nome_arquivo, campos):
    """Exporta documentos para JSON"""
    if not docs:
        return
    
    caminho = os.path.join(EXPORT_DIR, nome_arquivo)
    
    try:
        docs_limpos = [limpar_documento(doc, campos) for doc in docs]
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(docs_limpos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ✗ Erro ao exportar JSON {nome_arquivo}: {e}")

def main():
    print("\n" + "="*60)
    print("EXPORTANDO RESULTADOS DAS QUERIES")
    print("="*60 + "\n")
    
    # Criar diretório
    criar_diretorio()
    
    # Conectar ao MongoDB
    client = conectar_mongodb()
    db = client[DB_NAME]
    
    # Estatísticas
    total_docs = 0
    queries_processadas = 0
    
    # Exportar cada query
    for numero_query, config in QUERIES.items():
        colecao = config["collection"]
        titulo = config["titulo"]
        campos = config["campos"]
        
        print(f"\n{numero_query}: {titulo}")
        
        # Buscar documentos
        docs = obter_documentos(db, colecao)
        
        if docs:
            # Exportar CSV
            nome_csv = f"{numero_query}_resultado.csv"
            qtd = exportar_csv(colecao, docs, nome_csv, campos)
            
            # Exportar JSON
            nome_json = f"{numero_query}_resultado.json"
            exportar_json(colecao, docs, nome_json, campos)
            
            total_docs += qtd
            queries_processadas += 1
        else:
            print(f"  ⚠ Nenhum dado encontrado")
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DA EXPORTAÇÃO")
    print("="*60)
    print(f"✓ Queries processadas: {queries_processadas}/8")
    print(f"✓ Total de documentos exportados: {total_docs}")
    print(f"✓ Diretório: {os.path.abspath(EXPORT_DIR)}")
    print(f"✓ Arquivos gerados: {queries_processadas} CSV + {queries_processadas} JSON")
    print("\nOs arquivos estão prontos para gerar gráficos!")
    print("="*60 + "\n")
    
    client.close()

if __name__ == "__main__":
    main()
