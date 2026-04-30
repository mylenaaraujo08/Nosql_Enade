from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv('MONGO_URI')
if not uri:
    print('MONGO_URI não encontrado')
    exit(1)

client = MongoClient(uri)
db = client['enade_db']

cols = db.list_collection_names()
print(f'Coleções no banco enade_db: {len(cols)}')
for c in sorted(cols):
    try:
        cnt = db[c].count_documents({})
    except Exception as e:
        cnt = f'erro: {e}'
    print(f'{c}: {cnt}')
