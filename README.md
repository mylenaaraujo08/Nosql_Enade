# Projeto ENADE + MongoDB

-Arquivos principais para avaliação:
-
- `nosql_mongo/app_visualizacao.py` - dashboard principal
- `nosql_mongo/mongo_create.py` - criação do banco e índices
- `nosql_mongo/mongo_populate.py` - população das coleções a partir dos CSVs
- `nosql_mongo/run_all_queries_compact.py` - geração das coleções de resultado das consultas
- `nosql_mongo/import_mongo_pandas_compact.py` - importação compacta dos dados
- `nosql_mongo/check_counts.py` - conferência de contagens no MongoDB
- `nosql_mongo/db_structure.md` - estrutura do banco
- `nosql_mongo/mongo_load_explainer.md` - explicação do processo de carga

Como executar o dashboard:

```powershell
& ".venv/Scripts/python.exe" -m streamlit run nosql_mongo/app_visualizacao.py
```

Como criar e carregar o banco:

```powershell
& ".venv/Scripts/python.exe" nosql_mongo/mongo_create.py
& ".venv/Scripts/python.exe" nosql_mongo/mongo_populate.py --replace
```
