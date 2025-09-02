import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

# --- Configurações da Página ---
st.set_page_config(layout="wide")

# --- Funções de Carregamento de Dados ---

@st.cache_data
def carregar_dados_estados():
    """Carrega os dados de dengue por estado e agrupa por ano."""
    caminho_parquet_ufs = 'data/dados_dengue_ufs.parquet'
    try:
        df_estados_raw = pd.read_parquet(caminho_parquet_ufs)
        
        # Agregação anual para garantir um valor por estado/ano
        df_estados_anual = df_estados_raw.groupby(['UF', 'Sigla','Ano']).agg(
            Casos=('Casos', 'sum'),
            Taxa=('Taxa', 'mean') # Usando a média da taxa
        ).reset_index()

        
        return df_estados_anual
    except Exception as e:
        st.error(f"Erro ao carregar ou agregar os dados dos estados: {e}")
        return pd.DataFrame()

# (As outras funções de carregamento permanecem as mesmas)
@st.cache_data
def carregar_dados_municipios_anual():
    caminho_parquet_mun = 'data/dados_dengue_municipios.parquet'
    try:
        df_municipios = pd.read_parquet(caminho_parquet_mun)
        df_anual = df_municipios.groupby(['UF', 'Codigo_Municipio', 'Municipio', 'Ano']).agg(
            Casos=('Casos', 'sum'),
            Taxa=('Taxa', 'mean')
        ).reset_index()
        return df_anual
    except Exception as e:
        st.error(f"Erro ao carregar ou agregar os dados dos municípios: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_geojson_municipios():
    caminho_geojson_mun = 'data/geojs-100-mun.json'
    try:
        with open(caminho_geojson_mun, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar o GeoJSON dos municípios: {e}")
        return None

# --- Carregamento de todos os dados ---
df_estados = carregar_dados_estados()
df_municipios_anual = carregar_dados_municipios_anual()
geojson_municipios = carregar_geojson_municipios()
# Não vamos pré-carregar o geojson dos estados, vamos usar a URL como você pediu.

# --- Layout da Página ---
st.title("🗺️ Análise Espacial da Dengue")
st.markdown("Visualize a distribuição de casos e taxas de dengue no território brasileiro.")
st.markdown("---")

# --- Seção 1: Mapa Nacional por Estados ---
st.header("Mapa da Incidência Nacional")

if not df_estados.empty:
    col1, col2 = st.columns(2)
    with col1:
        anos_disponiveis = sorted(df_estados['Ano'].unique())
        ano_selecionado_estado = st.selectbox(
            "Selecione o Ano:",
            options=anos_disponiveis,
            index=len(anos_disponiveis)-1,
            key='ano_estado'
        )
    with col2:
        metrica_selecionada_estado = st.radio(
            "Selecione a Métrica:",
            options=['Casos', 'Taxa'],
            horizontal=True,
            key='metrica_estado'
        )

    df_mapa_estado = df_estados[df_estados['Ano'] == ano_selecionado_estado]

    # Etapa de Depuração: Visualizar os dados que estão indo para o mapa
    with st.expander("Ver dados da tabela do mapa de estados (após filtro)"):
        st.dataframe(df_mapa_estado)

    # Verifica se há dados para plotar
    if not df_mapa_estado.empty:
        fig_estados = px.choropleth(
            df_mapa_estado,
            geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
            locations='Sigla',
            featureidkey='properties.sigla', # Usando a chave que você indicou como correta
            color=metrica_selecionada_estado,
            color_continuous_scale='Reds',
            range_color=(0, df_mapa_estado[metrica_selecionada_estado].max()),
            scope='south america',
            labels={'Taxa': 'Taxa de incidência', 'Casos': 'Total de Casos'},
            title=f'{metrica_selecionada_estado} de Dengue por Estado - {ano_selecionado_estado}',
        )
        fig_estados.update_geos(fitbounds="locations", visible=False)
        fig_estados.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_estados, use_container_width=True)
    else:
        st.warning("Não há dados para exibir com os filtros selecionados.")

st.markdown("---")

# --- Seção 2: Mapa por Municípios de um Estado (sem alterações) ---
# O código desta seção permanece o mesmo, pois já estava funcionando bem.
st.header("Mapa da Incidência por Estado")
if not df_municipios_anual.empty:
    # (Restante do código para o mapa de municípios)
    col1_mun, col2_mun, col3_mun = st.columns(3)
    with col1_mun:
        uf_selecionada = st.selectbox("Selecione a UF:", options=sorted(df_municipios_anual['UF'].unique()))
    with col2_mun:
        anos_mun_disponiveis = sorted(df_municipios_anual['Ano'].unique())
        ano_selecionado_mun = st.selectbox("Selecione o Ano:", options=anos_mun_disponiveis, index=len(anos_mun_disponiveis)-1, key='ano_municipio')
    with col3_mun:
        metrica_selecionada_mun = st.radio("Selecione a Métrica:", options=['Casos', 'Taxa'], horizontal=True, key='metrica_municipio')

    df_mapa_mun = df_municipios_anual[
        (df_municipios_anual['UF'] == uf_selecionada) &
        (df_municipios_anual['Ano'] == ano_selecionado_mun)
    ].copy()
    
    if not df_mapa_mun.empty and carregar_geojson_municipios() is not None:
        df_mapa_mun['Codigo_Municipio'] = df_mapa_mun['Codigo_Municipio'].astype(str)
        fig_municipios = px.choropleth(
            df_mapa_mun,
            geojson=carregar_geojson_municipios(),
            locations='Codigo_Municipio',
            featureidkey='properties.id',
            color=metrica_selecionada_mun,
            color_continuous_scale="Reds",
            hover_name='Municipio',
            title=f'{metrica_selecionada_mun} Anuais em {uf_selecionada} - {ano_selecionado_mun}'
        )
        fig_municipios.update_geos(fitbounds="locations", visible=False)
        fig_municipios.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_municipios, use_container_width=True)