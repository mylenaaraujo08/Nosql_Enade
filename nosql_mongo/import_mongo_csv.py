import os
import csv
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def converter_tipo(valor):
    """Converte string para tipos apropriados (int, float, None)"""
    if valor is None or valor == '' or valor == 'None':
        return None
    try:
        return int(valor)
    except ValueError:
        try:
            return float(valor)
        except ValueError:
            return valor

def processar_csv(caminho, colecao, chunk_size=10000):
    """Processa CSV em chunks e insere no MongoDB"""
    total = 0
    lote = []
    
    with open(caminho, 'r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            # Converter valores
            doc = {k: converter_tipo(v) for k, v in linha.items()}
            lote.append(doc)
            
            if len(lote) >= chunk_size:
                result = colecao.insert_many(lote)
                total += len(result.inserted_ids)
                lote = []
                print(f"  ... {total} documentos", end='\r')
    
    # Inserir resto
    if lote:
        result = colecao.insert_many(lote)
        total += len(result.inserted_ids)
    
    return total

def main():
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print('Erro: MONGO_URI não encontrado no .env')
        return

    try:
        client = MongoClient(mongo_uri)
        db = client['enade_db']
        client.admin.command('ping')
        print("✓ Conectado ao MongoDB - banco: [enade_db]\n")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return

    pasta = 'enade_normalizado'
    arquivos_csv = sorted([f for f in os.listdir(pasta) if f.endswith('.csv')])

    for arquivo_csv in arquivos_csv:
        caminho = os.path.join(pasta, arquivo_csv)
        nome_colecao = arquivo_csv.replace('.csv', '')
        
        # Mapear enade para fato
        if nome_colecao == 'enade':
            nome_colecao = 'fato'
        
        try:
            print(f"→ Carregando {arquivo_csv} em colecao [{nome_colecao}]...")
            
            colecao = db[nome_colecao]
            db.drop_collection(nome_colecao)
            
            total = processar_csv(caminho, colecao, chunk_size=10000)
            
            print(f"✓ [{nome_colecao}]: {total} documentos inseridos")
                
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo_csv}: {str(e)[:150]}")

if __name__ == "__main__":
    main()
