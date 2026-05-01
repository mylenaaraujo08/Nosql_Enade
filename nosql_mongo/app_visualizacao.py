#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Aplicativo Streamlit para Visualização de Análises ENADE - versão para avaliação

import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import numpy as np

# Configurações Streamlit
st.set_page_config(
	page_title="ENADE Analytics Dashboard",
	page_icon="📊",
	layout="wide",
	initial_sidebar_state="expanded"
)

# Carregar variáveis de ambiente a partir da raiz do projeto
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = "enade_db"

# Cores do tema
CORES_TEMA = {
	"primaria": "#7ab7ff",
	"secundaria": "#ffb357",
	"sucesso": "#45d483",
	"perigo": "#ff6b6b",
	"neutro": "#9aa4b2",
	"fundo_claro": "#111827",
	"card_bg": "#0f172a",
	"card_alt": "#111c33",
	"border": "#24324a",
	"texto_escuro": "#e5eefc",
	"texto_claro": "#ffffff"
}

# CSS Profissional e Moderno
st.markdown(f"""
	<style>
	/* Reset e Fundo Geral */
	* {{
		margin: 0;
		padding: 0;
	}}
    
	html, body, [data-testid="stAppViewContainer"] {{
		background: radial-gradient(circle at top left, #16243d 0%, #0b1220 45%, #070b14 100%) !important;
		color: {CORES_TEMA['texto_escuro']};
	}}

	[data-testid="stHeader"] {{
		background: transparent !important;
	}}
    
	[data-testid="stToolbar"] {{
		background: transparent !important;
	}}
    
	/* Sidebar Premium */
	[data-testid="stSidebar"] {{
		background: linear-gradient(180deg, #0f172a 0%, #101b30 100%) !important;
		border-right: 1px solid {CORES_TEMA['border']};
	}}
    
	[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
		color: {CORES_TEMA['texto_claro']} !important;
	}}
    
	[data-testid="stSidebar"] h1, 
	[data-testid="stSidebar"] h2,
	[data-testid="stSidebar"] h3,
	[data-testid="stSidebar"] p,
	[data-testid="stSidebar"] li {{
		color: {CORES_TEMA['texto_claro']} !important;
	}}
    
	[data-testid="stSidebar"] hr {{
		border-color: rgba(255,255,255,0.2) !important;
	}}
    
	/* Seletor de Query */
	[data-testid="stSidebar"] select,
	[data-testid="stSidebar"] [role="combobox"] {{
		background-color: rgba(15, 23, 42, 0.95) !important;
		color: {CORES_TEMA['texto_claro']} !important;
		border: 1px solid {CORES_TEMA['border']} !important;
		border-radius: 8px !important;
		padding: 10px !important;
		font-weight: bold !important;
	}}
    
	/* Header Principal */
	.header-container {{
		background: linear-gradient(135deg, #101b30 0%, #1f3d63 100%);
		padding: 30px;
		border-radius: 15px;
		margin-bottom: 30px;
		box-shadow: 0 10px 30px rgba(0,0,0,0.28);
		border: 1px solid rgba(122, 183, 255, 0.16);
	}}
    
	.dashboard-title {{
		color: {CORES_TEMA['texto_claro']};
		font-size: 36px;
		font-weight: bold;
		margin-bottom: 10px;
		text-shadow: 0 2px 4px rgba(0,0,0,0.2);
	}}
    
	.dashboard-subtitle {{
		color: rgba(255,255,255,0.9);
		font-size: 16px;
	}}
    
	/* Título da Query */
	.query-title {{
		color: #dbeafe;
		font-size: 32px;
		font-weight: 700;
		margin: 20px 0 10px 0;
		letter-spacing: -0.5px;
	}}
    
	/* Descrição/Badge */
	.query-description {{
		background: linear-gradient(135deg, #101b30 0%, #0d1728 100%);
		border-left: 5px solid {CORES_TEMA['primaria']};
		border-radius: 10px;
		padding: 18px 20px;
		margin-bottom: 30px;
		color: {CORES_TEMA['texto_escuro']};
		font-size: 15px;
		line-height: 1.6;
		box-shadow: 0 2px 8px rgba(31, 119, 180, 0.1);
	}}
    
	/* Cards Container */
	.card-container {{
		background-color: {CORES_TEMA['card_bg']};
		border-radius: 12px;
		padding: 25px;
		margin-bottom: 25px;
		box-shadow: 0 10px 24px rgba(0,0,0,0.24);
		border: 1px solid {CORES_TEMA['border']};
		transition: all 0.3s ease;
	}}
    
	.card-container:hover {{
		box-shadow: 0 4px 16px rgba(0,0,0,0.12);
		border-color: {CORES_TEMA['primaria']};
	}}
    
	.card-title {{
		font-size: 18px;
		font-weight: 700;
		color: {CORES_TEMA['primaria']};
		margin-bottom: 20px;
		border-bottom: 2px solid {CORES_TEMA['fundo_claro']};
		padding-bottom: 10px;
	}}
    
	/* Seção Headers */
	.section-header {{
		color: {CORES_TEMA['primaria']};
		font-size: 20px;
		font-weight: 700;
		margin: 25px 0 15px 0;
		padding-bottom: 12px;
		border-bottom: 3px solid {CORES_TEMA['primaria']};
		display: flex;
		align-items: center;
		gap: 10px;
	}}
    
	/* Métrica Card */
	.metric-card {{
		background: linear-gradient(135deg, #101b30 0%, #0b1322 100%);
		border-radius: 12px;
		padding: 20px;
		border-left: 5px solid {CORES_TEMA['primaria']};
		box-shadow: 0 6px 18px rgba(0,0,0,0.22);
		text-align: center;
		transition: all 0.3s ease;
	}}
    
	.metric-card:hover {{
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		border-left-color: {CORES_TEMA['secundaria']};
	}}
    
	.metric-label {{
		font-size: 13px;
		font-weight: 600;
		color: #aeb9ca;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-bottom: 8px;
	}}
    
	.metric-value {{
		font-size: 28px;
		font-weight: 800;
		color: #eff6ff;
		letter-spacing: -1px;
	}}
    
	.metric-unit {{
		font-size: 12px;
		color: #8da2c0;
		margin-top: 5px;
	}}
    
	/* Tabela Estilizada */
	.dataframe {{
		border-collapse: collapse !important;
		width: 100% !important;
	}}
    
	.dataframe tbody tr:nth-child(odd) {{
		background-color: #101b30 !important;
	}}
    
	.dataframe tbody tr:nth-child(even) {{
		background-color: {CORES_TEMA['card_alt']} !important;
	}}
    
	.dataframe tbody tr:hover {{
		background-color: rgba(122, 183, 255, 0.10) !important;
	}}
    
	.dataframe th {{
		background: linear-gradient(135deg, #243b61 0%, #111f38 100%) !important;
		color: {CORES_TEMA['texto_claro']} !important;
		font-weight: 700 !important;
		padding: 12px !important;
		text-align: left !important;
		border-bottom: 2px solid {CORES_TEMA['primaria']} !important;
	}}
    
	.dataframe td {{
		padding: 12px !important;
		border-bottom: 1px solid #e0e0e0 !important;
	}}
    
	/* Botões */
	.stButton > button {{
		background: linear-gradient(135deg, #2f67b5 0%, #163055 100%) !important;
		color: {CORES_TEMA['texto_claro']} !important;
		border: none !important;
		border-radius: 8px !important;
		padding: 12px 24px !important;
		font-weight: 600 !important;
		font-size: 14px !important;
		transition: all 0.3s ease !important;
		box-shadow: 0 2px 8px rgba(31, 119, 180, 0.2) !important;
	}}
    
	.stButton > button:hover {{
		transform: translateY(-2px) !important;
		box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3) !important;
	}}
    
	/* Alert de Sucesso */
	.stAlert {{
		border-radius: 10px !important;
		padding: 15px 20px !important;
		font-weight: 500 !important;
	}}

	/* Painel de apresentação */
	.intro-panel {{
		background: linear-gradient(135deg, rgba(16, 27, 48, 0.96) 0%, rgba(13, 23, 40, 0.96) 100%);
		border: 1px solid rgba(122, 183, 255, 0.14);
		border-radius: 16px;
		padding: 20px 22px;
		margin-bottom: 20px;
		box-shadow: 0 10px 24px rgba(0, 0, 0, 0.20);
	}}

	.intro-kicker {{
		color: #7ab7ff;
		font-size: 12px;
		font-weight: 800;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		margin-bottom: 8px;
	}}

	.intro-title {{
		color: #f4f7fb;
		font-size: 28px;
		font-weight: 800;
		line-height: 1.1;
		margin-bottom: 8px;
	}}

	.intro-text {{
		color: rgba(229, 238, 252, 0.84);
		font-size: 14px;
		line-height: 1.55;
		max-width: 980px;
	}}

	.compact-metrics {{
		background: rgba(15, 23, 42, 0.70);
		border: 1px solid rgba(36, 50, 74, 0.90);
		border-radius: 14px;
		padding: 14px 16px;
		margin: 14px 0 20px 0;
	}}

	.compact-stat {{
		padding: 8px 10px;
		border-radius: 10px;
		background: rgba(17, 28, 51, 0.88);
		border: 1px solid rgba(36, 50, 74, 0.85);
	}}

	.compact-label {{
		color: #9aa4b2;
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		margin-bottom: 2px;
	}}

	.compact-value {{
		color: #eff6ff;
		font-size: 15px;
		font-weight: 700;
		line-height: 1.25;
		word-break: break-word;
	}}

	.compact-note {{
		color: #8da2c0;
		font-size: 11px;
		margin-top: 2px;
	}}

	.small-section-title {{
		color: #dbeafe;
		font-size: 18px;
		font-weight: 700;
		margin: 12px 0 8px 0;
	}}
    
	/* Gráfico Container */
	.graph-container {{
		background-color: {CORES_TEMA['card_bg']};
		border-radius: 12px;
		padding: 25px;
		border: 1px solid {CORES_TEMA['border']};
		box-shadow: 0 10px 24px rgba(0,0,0,0.24);
		margin-bottom: 25px;
	}}

	.stDataFrame {{
		border: 1px solid {CORES_TEMA['border']};
		border-radius: 12px;
		overflow: hidden;
	}}
    
	/* Ajustes para o botão de download: texto preto e contraste */
	[data-testid="stDownloadButton"] > button,
	.stDownloadButton > button {{
		background: #ffffff !important;
		color: #000000 !important;
		border: 1px solid rgba(0,0,0,0.08) !important;
		box-shadow: none !important;
	}}

	/* Estilo do expander "Ver dados completos" - texto preto em modo claro */
	.streamlit-expanderHeader {{
		color: #000000 !important;
		font-weight: 600 !important;
	}}

	/* Remover quaisquer espaços em branco indesejados */
	[data-testid="stSidebar"] .stSelectbox {{
		background: transparent !important;
	}}

	/* Ocultar apenas o ícone SVG do dropdown na sidebar (não remover o contêiner de opções) */
	[data-testid="stSidebar"] [data-baseweb="select"] svg[data-baseweb="icon"] {{
		display: none !important;
	}}

	/* Camuflar o campo de busca/caixa no select na sidebar (modo claro e escuro) */
	[data-testid="stSidebar"] [data-baseweb="select"] div[value],
	[data-testid="stSidebar"] [data-baseweb="select"] input[role="combobox"],
	[data-testid="stSidebar"] [data-baseweb="select"] div[role="combobox"] {{
		background: inherit !important;
		border: none !important;
		box-shadow: none !important;
		color: inherit !important;
	}}
    
	</style>
""", unsafe_allow_html=True)

# Definição das queries com metadados SIMPLIFICADA
QUERIES_CONFIG = {
	"Q1": {
		"collection": "res_q1_ranking_cursos",
		"titulo": "📚 Ranking de Cursos por Desempenho",
		"descricao": "Análise dos cursos com melhor desempenho acadêmico no ENADE. Ranking baseado na média geral de notas dos alunos por curso.",
		"x": "curso",
		"y": "media_nota_geral",
		"color": None,
		"metricas": ["qtd_alunos", "media_nota_geral"]
	},
	"Q2": {
		"collection": "res_q2_desempenho_uf_regiao",
		"titulo": "🗺️ Desempenho por UF e Região",
		"descricao": "Comparação do desempenho acadêmico entre diferentes estados (UFs) e regiões geográficas do Brasil. Mostra como a qualidade de ensino varia geograficamente.",
		"x": "uf",
		"y": "media_nota",
		"color": "regiao",
		"metricas": ["qtd_alunos", "media_nota"]
	},
	"Q3": {
		"collection": "res_q3_gap_publico_privado",
		"titulo": "🏫 Gap Público vs Privado",
		"descricao": "Análise da diferença de desempenho entre instituições públicas e privadas por curso. Identifica qual categoria possui melhor desempenho.",
		"x": "curso",
		"y": "media_nota",
		"color": "categoria",
		"metricas": ["qtd", "media_nota"]
	},
	"Q4": {
		"collection": "res_q4_primeira_geracao",
		"titulo": "👨‍👩‍👧‍👦 Primeira Geração vs Escolaridade Parental",
		"descricao": "Comparação do desempenho de alunos de primeira geração versus escolaridade parental. Analisa impacto da origem educacional familiar.",
		"x": "escolaridade_pai",
		"y": "media_nota",
		"color": "primeira_geracao",
		"metricas": ["qtd", "media_nota"]
	},
	"Q5": {
		"collection": "res_q5_jornada_trabalho",
		"titulo": "⏰ Jornada de Trabalho vs Desempenho",
		"descricao": "Análise de como a jornada de trabalho dos alunos impacta seu desempenho acadêmico. Compara alunos que não trabalham, trabalham parcialmente ou em tempo integral.",
		"x": "jornada",
		"y": "media_nota",
		"color": None,
		"metricas": ["qtd", "media_nota", "min_nota", "max_nota"]
	},
	"Q6": {
		"collection": "res_q6_avaliacao_infraestrutura",
		"titulo": "🏢 Avaliação de Infraestrutura",
		"descricao": "Relação entre a avaliação de equipamentos e infraestrutura das instituições com o desempenho dos alunos. Mostra impacto da qualidade das instalações.",
		"x": "avaliacao_equipamentos",
		"y": "media_nota",
		"color": None,
		"metricas": ["qtd", "media_nota"]
	},
	"Q7": {
		"collection": "res_q7_vulnerabilidade",
		"titulo": "💰 Vulnerabilidade Econômica",
		"descricao": "Análise da vulnerabilidade econômica dos alunos por faixa de desempenho. Avalia como renda familiar influencia resultados acadêmicos.",
		"x": "faixa_nota",
		"y": "qtd",
		"color": "renda_familiar",
		"metricas": ["qtd"]
	},
	"Q8": {
		"collection": "res_q8_delta_municipio_uf",
		"titulo": "📍 Delta Município vs Média Estadual",
		"descricao": "Comparação da performance de cada município em relação à média estadual. Identifica municípios com desempenho acima ou abaixo da média estadual.",
		"x": "municipio",
		"y": "delta",
		"color": None,
		"metricas": ["media_nota_municipio", "media_nota_uf", "delta"]
	}
}


@st.cache_data(ttl=300)
def carregar_dados(nome_colecao):
	if not MONGO_URI:
		raise RuntimeError("MONGO_URI não encontrado no .env")
	cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=30000)
	banco = cliente[DB_NAME]
	dados = list(banco[nome_colecao].find({}))
	if not dados:
		return pd.DataFrame()
	frame = pd.DataFrame(dados)
	if "_id" in frame.columns:
		frame = frame.drop(columns=["_id"])
	return frame


def exibir_metricas(frame, metricas):
	if not metricas:
		return
	colunas = st.columns(len(metricas))
	for indice, nome_coluna in enumerate(metricas):
		if nome_coluna not in frame.columns:
			continue
		with colunas[indice]:
			st.metric(nome_coluna.replace("_", " ").title(), frame[nome_coluna].iloc[0])


def criar_grafico_barras(frame, eixo_x, eixo_y, cor=None, titulo=None):
	if frame.empty or eixo_x not in frame.columns or eixo_y not in frame.columns:
		st.info("Não há dados suficientes para montar o gráfico desta consulta.")
		return

	ordenado = frame.sort_values(by=eixo_y, ascending=False).head(20)
	if cor and cor in ordenado.columns:
		figura = px.bar(ordenado, x=eixo_y, y=eixo_x, color=cor, orientation="h", title=titulo)
	else:
		figura = px.bar(ordenado, x=eixo_y, y=eixo_x, orientation="h", title=titulo)

	figura.update_layout(
		height=max(420, 28 * len(ordenado)),
		margin=dict(l=20, r=20, t=60, b=20),
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		font=dict(color="#e5eefc"),
		legend_title_text=cor if cor else None,
	)
	figura.update_yaxes(autorange="reversed")
	st.plotly_chart(figura, use_container_width=True)


def main():
	st.markdown(
		"""
		<div class="intro-panel">
			<div class="intro-kicker">Projeto ENADE + MongoDB</div>
			<div class="intro-title">ENADE Analytics Dashboard</div>
			<div class="intro-text">
				Uma apresentação visual mais limpa para navegar pelos resultados do ENADE. As análises ficam na lateral,
				e o conteúdo principal mostra contexto, métricas resumidas e gráficos sem exagerar nos blocos expostos.
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)

	with st.sidebar:
		st.header("Consultas")
		st.caption("Escolha a análise que deseja explorar")
		consulta = st.selectbox(
			"Escolha a análise",
			list(QUERIES_CONFIG.keys()),
			format_func=lambda chave: f"{chave} - {QUERIES_CONFIG[chave]['titulo']}",
		)
		st.caption("As explicações aparecem abaixo no painel principal.")

	config = QUERIES_CONFIG[consulta]
	st.markdown(f"<div class='small-section-title'>{config['titulo']}</div>", unsafe_allow_html=True)
	st.markdown(f"<div class='intro-text'>{config['descricao']}</div>", unsafe_allow_html=True)

	try:
		frame = carregar_dados(config["collection"])
	except Exception as erro:
		st.error(f"Falha ao carregar a coleção {config['collection']}: {erro}")
		return

	if frame.empty:
		st.warning(f"A coleção {config['collection']} não possui documentos no MongoDB.")
		return

	st.markdown("<div class='compact-metrics'>", unsafe_allow_html=True)
	col1, col2, col3 = st.columns(3)
	with col1:
		st.markdown(
			f"""
			<div class="compact-stat">
				<div class="compact-label">Registros</div>
				<div class="compact-value">{len(frame):,}</div>
				<div class="compact-note">linhas disponíveis na coleção</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
	with col2:
		st.markdown(
			f"""
			<div class="compact-stat">
				<div class="compact-label">Colunas</div>
				<div class="compact-value">{len(frame.columns)}</div>
				<div class="compact-note">campos exibidos na tabela</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
	with col3:
		st.markdown(
			f"""
			<div class="compact-stat">
				<div class="compact-label">Coleção</div>
				<div class="compact-value">{config['collection']}</div>
				<div class="compact-note">origem do conteúdo</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
	st.markdown("</div>", unsafe_allow_html=True)

	metricas = config.get("metricas", [])
	if metricas:
		st.markdown("<div class='small-section-title'>Indicadores rápidos</div>", unsafe_allow_html=True)
		dados_metricas = frame[metricas].head(1).fillna(0)
		exibir_metricas(dados_metricas, metricas)

	st.markdown("<div class='small-section-title'>Visualização principal</div>", unsafe_allow_html=True)
	criar_grafico_barras(frame, config["x"], config["y"], config.get("color"), config["titulo"])

	with st.expander("Ver dados completos"):
		st.dataframe(frame, use_container_width=True)


if __name__ == "__main__":
	main()

