import os
from collections import defaultdict
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
if not uri:
	raise RuntimeError("MONGO_URI não encontrado no .env")

client = MongoClient(uri, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000)
db = client["enade_db"]
client.admin.command("ping")
print("Conectado ao MongoDB: enade_db\n")


def drop_and_replace(collection_name, docs):
	if collection_name in db.list_collection_names():
		db.drop_collection(collection_name)
	docs = list(docs)
	if docs:
		db[collection_name].insert_many(docs)
	return db[collection_name].count_documents({})


def load_lookup(collection_name):
	lookup = {}
	for doc in db[collection_name].find({}, projection=None):
		key = doc.get("_id")
		if key is not None:
			lookup[key] = doc
	return lookup


def query_q1():
	print("Q1: Ranking Cursos por Desempenho")
	start = datetime.now()
	des_lookup = load_lookup("dim_desempenho")
	oferta_lookup = load_lookup("dim_oferta")
	curso_lookup = load_lookup("dim_curso")

	agg = defaultdict(lambda: {"qtd_alunos": 0, "soma_nota": 0.0})
	for doc in db.fato.find({}, {"of": 1, "de": 1}):
		des = des_lookup.get(doc.get("de"))
		of = oferta_lookup.get(doc.get("of"))
		if not des or not of:
			continue
		curso = curso_lookup.get(of.get("curso"))
		if not curso:
			continue
		nota = des.get("ng")
		if nota is None:
			continue
		nome = curso.get("curso")
		if nome is None:
			continue
		bucket = agg[nome]
		bucket["qtd_alunos"] += 1
		bucket["soma_nota"] += float(nota)

	resultados = []
	for curso, stats in agg.items():
		if stats["qtd_alunos"] >= 1000:
			resultados.append(
				{
					"curso": curso,
					"qtd_alunos": stats["qtd_alunos"],
					"media_nota_geral": round(stats["soma_nota"] / stats["qtd_alunos"], 2),
				}
			)
	resultados.sort(key=lambda x: x["media_nota_geral"], reverse=True)
	resultados = resultados[:20]
	count = drop_and_replace("res_q1_ranking_cursos", resultados)
	elapsed = (datetime.now() - start).total_seconds()
	print(f"  ✓ {count} documentos em {elapsed:.1f}s")


def query_q2():
	print("Q2: Desempenho por UF e Região")
	start = datetime.now()
	mun_lookup = load_lookup("dim_municipio")
	uf_lookup = load_lookup("dim_uf")
	des_lookup = load_lookup("dim_desempenho")
	oferta_lookup = load_lookup("dim_oferta")

	agg = defaultdict(lambda: {"qtd_alunos": 0, "soma_nota": 0.0})
	for doc in db.fato.find({}, {"of": 1, "de": 1}):
		of = oferta_lookup.get(doc.get("of"))
		des = des_lookup.get(doc.get("de"))
		if not of or not des:
			continue
		mun = mun_lookup.get(of.get("mun"))
		if not mun:
			continue
		uf = uf_lookup.get(mun.get("uf"))
		if not uf:
			continue
		nota = des.get("ng")
		if nota is None:
			continue
		key = (mun.get("uf"), uf.get("reg"))
		bucket = agg[key]
		bucket["qtd_alunos"] += 1
		bucket["soma_nota"] += float(nota)

	resultados = []
	for (uf, regiao), stats in agg.items():
		resultados.append(
			{
				"uf": uf,
				"regiao": regiao,
				"qtd_alunos": stats["qtd_alunos"],
				"media_nota": round(stats["soma_nota"] / stats["qtd_alunos"], 2),
			}
		)
	resultados.sort(key=lambda x: x["uf"])
	count = drop_and_replace("res_q2_desempenho_uf_regiao", resultados)
	elapsed = (datetime.now() - start).total_seconds()
	print(f"  ✓ {count} documentos em {elapsed:.1f}s")

