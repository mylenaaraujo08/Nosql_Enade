#!/usr/bin/env python3
"""
Cria o banco `enade_db`, coleções e índices recomendados.
Uso:
  python mongo_create.py [--drop]

--drop : apaga as coleções existentes antes de criar (útil em ambiente de desenvolvimento)

Requisitos: pymongo, python-dotenv
Arquivo copiado para avaliação.
"""
import os
import argparse
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "enade_db")

COLLECTIONS = {
	"dim_avaliacao": {
		"validator": {
			"$jsonSchema": {
				"bsonType": "object",
				"required": ["codigo", "descricao"],
				"properties": {
					"codigo": {"bsonType": "string"},
					"descricao": {"bsonType": "string"}
				}
			}
		},
		"indexes": [[("codigo", 1)],]
	},
	"dim_curso": {
		"validator": {
			"$jsonSchema": {
				"bsonType": "object",
				"required": ["curso_id", "nome"],
				"properties": {"curso_id": {"bsonType": "string"}, "nome": {"bsonType": "string"}}
			}
		},
		"indexes": [[("curso_id", 1)],]
	},
	"dim_desempenho": {
		"validator": {"$jsonSchema": {"bsonType": "object"}},
		"indexes": [[("aluno_id", 1)],]
	},
	"dim_municipio": {"validator": {"$jsonSchema": {"bsonType": "object"}}, "indexes": [[("municipio_id", 1)],]},
	"dim_oferta": {"validator": {"$jsonSchema": {"bsonType": "object"}}, "indexes": [[("oferta_id", 1)],]},
	"dim_perfil_estudante": {"validator": {"$jsonSchema": {"bsonType": "object"}}, "indexes": [[("perfil_id", 1)],]},
	"dim_uf": {"validator": {"$jsonSchema": {"bsonType": "object"}}, "indexes": [[("uf", 1)],]},
	"fato": {
		"validator": {
			"$jsonSchema": {
				"bsonType": "object",
				"required": ["aluno_id", "curso_id", "nota"],
				"properties": {
					"aluno_id": {"bsonType": "string"},
					"curso_id": {"bsonType": "string"},
					"nota": {"bsonType": ["double", "int"]},
					"ano": {"bsonType": "int"}
				}
			}
		},
		"indexes": [
			[("aluno_id", 1)],
			[("curso_id", 1)],
			[("ano", 1)],
		]
	}
}


def create_collections(client, drop=False):
	db = client[DB_NAME]
	for name, meta in COLLECTIONS.items():
		if drop and name in db.list_collection_names():
			print(f"Dropping collection {name}")
			db.drop_collection(name)
		if name in db.list_collection_names():
			print(f"Collection {name} already exists, skipping creation")
			coll = db[name]
		else:
			print(f"Creating collection {name}")
			opts = {}
			if "validator" in meta:
				opts["validator"] = meta["validator"]
			coll = db.create_collection(name, **opts) if opts else db.create_collection(name)
		# criar índices
		for idx in meta.get("indexes", []):
			index_fields = idx
			print(f"Creating index on {name}: {index_fields}")
			coll.create_index(index_fields)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--drop", action="store_true", help="Drop collections before creating")
	args = parser.parse_args()

	if not MONGO_URI:
		raise SystemExit("MONGO_URI não encontrado no .env")

	client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
	try:
		client.admin.command("ping")
	except Exception as e:
		raise SystemExit(f"Erro ao conectar ao MongoDB: {e}")

	create_collections(client, drop=args.drop)
	print("Pronto. Coleções e índices criados em:", DB_NAME)
	client.close()

