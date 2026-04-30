Estrutura do Banco `enade_db`

(arquivo copiado para pasta deliverable para avaliação)

Coleções principais
-------------------
- `dim_avaliacao`
  - Campos principais (exemplo): `codigo`, `descricao`
  - Índices recomendados: `codigo`

- `dim_curso`
  - Campos principais (exemplo): `curso_id`, `nome`, `categoria` (publico/privado), `nivel`
  - Índices: `curso_id`

- `dim_desempenho`
  - Armazena registros por aluno: `aluno_id`, `curso_id`, `nota`, `ano`, `componentes`...
  - Índices: `aluno_id`

- `dim_municipio`
  - Campos: `municipio_id`, `nome`, `uf`, `populacao`...
  - Índices: `municipio_id`, `uf`

- `dim_oferta`
  - Descreve oferta/turno, modalidade, vagas
  - Índices: `oferta_id`

- `dim_perfil_estudante`
  - Campos socioeconômicos: `perfil_id`, `renda_familiar`, `escolaridade_pais`, `primeira_geracao`...
  - Índices: `perfil_id`

- `dim_uf`
  - Estados (UF), códigos e nome
  - Índices: `uf`

- `fato`
  - Tabela fato com registros por aluno/curso/ano
  - Campos chave: `aluno_id`, `curso_id`, `nota`, `ano`, `municipio_id`, `perfil_id`
  - Índices recomendados: `aluno_id`, `curso_id`, `ano`

Observações gerais
------------------
- Modelo proposto é um Star Schema: uma coleção fato e várias dimensões.
- Para consultas analíticas, prefira agregar via pipelines (aggregation framework) e precomputar resultados quando necessário (coleções `res_q1_*` etc.).
- Em ambientes com cota limitada (Atlas free), considere:
  - Usar nomes de campos compactos (economiza espaço em BSON)
  - Remover índices antes de grandes cargas e recriá-los depois
  - Carregar em etapas e monitorar crescimento do banco

Validação e regras
------------------
O script `mongo_create.py` cria regras básicas de validação (JSON Schema) para algumas coleções. Adapte as regras conforme o dicionário de dados original (ex.: tipos numéricos exatos, campos obrigatórios adicionais).

Índices
-------
Índices criados pelo script de criação:
- `dim_avaliacao.codigo` (asc)
- `dim_curso.curso_id` (asc)
- `dim_desempenho.aluno_id` (asc)
- `dim_municipio.municipio_id` (asc)
- `dim_oferta.oferta_id` (asc)
- `dim_perfil_estudante.perfil_id` (asc)
- `dim_uf.uf` (asc)
- `fato.aluno_id`, `fato.curso_id`, `fato.ano`

Melhorias possíveis
-------------------
- Especificar `unique` em índices que representam chaves naturais (quando aplicável).
- Criar índices compostos para queries frequentes (ex: `curso_id + ano`).
- Adicionar TTL indexes para dados temporários ou logs.

Exemplo de fluxo de uso
----------------------
1. `python mongo_create.py`  # cria coleções e índices
2. `python mongo_populate.py --replace --chunksize 20000`  # popula a base
3. `python run_all_queries_compact.py`  # gera as coleções de resultado analítico
4. Validar contagens com `check_collections_counts.py`

Se quiser, eu ajusto os validators JSON Schema para refletir exatamente os nomes/ tipos presentes nos CSVs do projeto.