#!/usr/bin/env python3
"""
Popula as coleções do Mongo a partir dos CSVs em `enade_normalizado/`.
Uso:
  python mongo_populate.py [--collections dim_curso,fato] [--chunksize 10000] [--replace]

Flags:
  --collections : lista separada por vírgula das coleções a popular (por padrão popula todas mapeadas)
  --chunksize   : número de linhas por lote ao inserir (padrão 10000)
  --replace     : apaga a coleção antes de popular
  --resume      : pula se a coleção já existir e não estiver vazia

Requisitos: pandas, pymongo, python-dotenv
Arquivo copiado para avaliação.
"""
import os
import argparse
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'enade_db')
CSV_DIR = os.path.join(os.path.dirname(__file__), 'enade_normalizado')

# Mapeamento: collection -> arquivo.csv
COLLECTION_FILES = {
	'dim_avaliacao': 'dim_avaliacao.csv',
	'dim_curso': 'dim_curso.csv',
	'dim_desempenho': 'dim_desempenho.csv',
	'dim_municipio': 'dim_municipio.csv',
	'dim_oferta': 'dim_oferta.csv',
	'dim_perfil_estudante': 'dim_perfil_estudante.csv',
	'dim_uf': 'dim_uf.csv',
	'fato': 'fato.csv'
}


def insert_chunks(collection, csv_path, chunksize=10000, replace=False, resume=False):
	client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
	db = client[DB_NAME]
	coll = db[collection]

	if replace and collection in db.list_collection_names():
		print(f"Apagando coleção {collection} (flag --replace)")
		db.drop_collection(collection)
		coll = db[collection]

	if resume:
		count = coll.count_documents({})
		if count > 0:
			print(f"Coleção {collection} já contém {count:,} documentos, pulando (--resume)")
			client.close()
			return

	if not os.path.exists(csv_path):
		print(f"Arquivo não encontrado: {csv_path}")
		client.close()
		return

	inserted = 0
	for chunk in pd.read_csv(csv_path, chunksize=chunksize, encoding='utf-8'):
		records = chunk.where(pd.notnull(chunk), None).to_dict(orient='records')
		if records:
			try:
				coll.insert_many(records)
				inserted += len(records)
				print(f"{collection}: inseridos {inserted:,} registros até agora")
			except Exception as e:
				print(f"Erro ao inserir lote em {collection}: {e}")
				break

	print(f"Concluído: {collection} - total aproximado inserido: {inserted:,}")
	client.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--collections', type=str, help='Lista separada por vírgula das coleções a popular')
	parser.add_argument('--chunksize', type=int, default=10000)
	parser.add_argument('--replace', action='store_true')
	parser.add_argument('--resume', action='store_true')
	args = parser.parse_args()

	if not MONGO_URI:
		raise SystemExit('MONGO_URI não encontrado no .env')

	to_run = list(COLLECTION_FILES.keys())
	if args.collections:
		to_run = [c.strip() for c in args.collections.split(',') if c.strip() in COLLECTION_FILES]

	for coll in to_run:
		csv_file = os.path.join(CSV_DIR, COLLECTION_FILES[coll])
		print(f"Populando {coll} a partir de {csv_file} (chunksize={args.chunksize})")
		insert_chunks(coll, csv_file, chunksize=args.chunksize, replace=args.replace, resume=args.resume)

	print('Todos os processos de população finalizados.')

