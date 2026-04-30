Processo de Carga - ENADE (visão explicativa)

(arquivo copiado para pasta deliverable para avaliação)

Objetivo
--------
Documentar o processo recomendado para carregar os CSVs normalizados no MongoDB Atlas (ou local).

Resumo rápido
-------------
1. Criar o banco e coleções com `mongo_create.py` (validação simples e índices).
2. Popular as coleções com `mongo_populate.py` a partir da pasta `enade_normalizado/`.
3. Rodar `run_all_queries_compact.py` (já presente) para gerar as coleções `res_q*`.

Recomendações e boas práticas
---------------------------
- Ordem de carga: dimensões primeiro (ex: `dim_avaliacao`, `dim_curso`, `dim_uf`...), depois a coleção `fato`.
- Use `--replace` no script de população para recriar uma coleção quando necessário.
- Para bases grandes, use `chunksize` (ex.: 5k-50k) para reduzir memória e evitar timeouts no Atlas.
- Monitorar cota do Atlas (free tier 512MB): use compactação de campos (nomes menores) ou carregar em etapas e apagar coleções temporariamente se necessário.
- Sempre desabilitar índices pesados antes de inserir grandes volumes e recriá-los após a carga para acelerar inserções (não implementado automaticamente neste repositório).

Resumable / idempotência
-----------------------
- O script `mongo_populate.py` oferece flags `--replace` (apaga coleção) e `--resume` (pula inserção se coleção já existir).
- Para cargas interrompidas, reexecute com `--resume` para evitar reimportar dados já existentes.

Exemplos de comandos
--------------------
Criar coleções (com validação e índices):

```bash
python mongo_create.py
```

Popular todas as coleções (substitui se já existirem):

```bash
python mongo_populate.py --replace
```

Popular apenas `fato` e usar chunk de 20000:

```bash
python mongo_populate.py --collections fato --chunksize 20000
```

Dicas para debug
----------------
- Verifique `MONGO_URI` no arquivo `.env` antes de rodar.
- Use `check_collections_counts.py` (existente) para confirmar contagens pós-carga.
- Se houver erro de cota no Atlas, carregue coleções menores primeiro, apague temporariamente grandes coleções e reimporte em partes.

Contato
------
Para dúvidas sobre o script, abra uma issue ou solicite ajustes na lógica de chunking/compactação.