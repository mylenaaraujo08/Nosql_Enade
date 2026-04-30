import os

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DB_NAME = "enade_db"
CSV_DIR = "enade18-23_normalizado"
CHUNK_SIZE = 50000

COLLECTIONS = {
	"avaliacao.csv": {
		"name": "dim_avaliacao",
		"id": "id_avaliacao",
		"rename": {
			"avaliacao_dificuldade_fg": "dfg",
			"avaliacao_dificuldade_ce": "dce",
			"avaliacao_equipamentos": "eqp",
			"avaliacao_ambiente": "amb",
		},
	},
	"cursos.csv": {
		"name": "dim_curso",
		"id": "id_curso",
		"rename": {
			"nome_curso": "curso",
		},
	},
	"desempenho.csv": {
		"name": "dim_desempenho",
		"id": "id_desempenho",
		"rename": {
			"nota_geral": "ng",
			"nota_formacao_geral": "nfg",
			"nota_componentes_especifico": "nce",
		},
	},
	"municipios.csv": {
		"name": "dim_municipio",
		"id": "id_municipio",
		"rename": {
			"nome_municipio": "mun",
			"uf": "uf",
		},
	},
	"oferta_curso.csv": {
		"name": "dim_oferta",
		"id": "id_oferta",
		"rename": {
			"id_curso": "curso",
			"id_municipio": "mun",
			"modalidade_graduacao": "mod",
			"turno_graduacao": "turno",
			"categoria_administrativa": "cat",
		},
	},
	"perfil_estudante.csv": {
		"name": "dim_perfil_estudante",
		"id": "id_perfil_estudante",
		"rename": {
			"sexo": "sex",
			"idade": "ida",
			"cor_raca": "cor",
			"ano_fim_ensino_medio": "fim_em",
			"ano_ingresso_graduacao": "ing_gr",
			"tipo_escola_ensino_medio": "esc",
			"primeira_geracao": "prim_gen",
			"escolaridade_pai": "esc_pai",
			"escolaridade_mae": "esc_mae",
			"motivacao_curso": "mot",
			"renda_familiar": "renda",
			"horas_trabalho": "hrs_trab",
			"cotas": "cotas",
		},
	},
	"ufs.csv": {
		"name": "dim_uf",
		"id": "uf",
		"rename": {
			"regiao": "reg",
		},
	},
	"fato_enade.csv": {
		"name": "fato",
		"id": "id_participacao",
		"rename": {
			"ano_enade": "ano",
			"id_oferta": "of",
			"id_perfil_estudante": "pf",
			"id_desempenho": "de",
			"id_avaliacao": "av",
		},
	},
}


def connect():
	mongo_uri = os.getenv("MONGO_URI")
	if not mongo_uri:
		raise RuntimeError("MONGO_URI nao encontrado no .env")
	client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
	client.admin.command("ping")
	return client


def compact_records(df, id_column, rename_map):
	df = df.rename(columns=rename_map)
	df[id_column] = df[id_column]
	records = df.where(pd.notna(df), None).to_dict("records")
	for record in records:
		record["_id"] = record.pop(id_column)
	return records


def import_csv(db, csv_file, spec):
	csv_path = os.path.join(CSV_DIR, csv_file)
	collection_name = spec["name"]
	id_column = spec["id"]
	rename_map = spec["rename"]

	if not os.path.exists(csv_path):
		print(f"- ausente: {csv_file}")
		return 0

	print(f"\n-> {csv_file} -> [{collection_name}]")
	if collection_name in db.list_collection_names():
		db.drop_collection(collection_name)

	total = 0
	for chunk_idx, chunk in enumerate(pd.read_csv(csv_path, chunksize=CHUNK_SIZE, encoding="utf-8"), start=1):
		records = compact_records(chunk, id_column, rename_map)
		if records:
			db[collection_name].insert_many(records, ordered=False)
			total += len(records)
			print(f"   lote {chunk_idx}: {total:,}")

	print(f"OK [{collection_name}] {total:,}")
	return total


def main():
	client = connect()
	db = client[DB_NAME]

	print(f"Conectado ao MongoDB. DB: {DB_NAME}")
	print("Limpando colecoes existentes para reimportacao do zero...")
	for spec in COLLECTIONS.values():
		db.drop_collection(spec["name"])

	total = 0
	for csv_file, spec in COLLECTIONS.items():
		total += import_csv(db, csv_file, spec)

	print("\nResumo final")
	print(f"Total inserido: {total:,}")
	client.close()


if __name__ == "__main__":
	main()

