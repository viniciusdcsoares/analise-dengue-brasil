import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

# Função para carregar dados com pandas
@st.cache_data
def carregar_dados_ufs():
    try:
        return pd.read_parquet('data/dados_dengue_ufs.parquet')
    except Exception as e:
        st.error(f"Erro ao carregar dados de UFs: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_municipios():
    try:
        return pd.read_parquet('data/dados_dengue_municipios.parquet')
    except Exception as e:
        st.error(f"Erro ao carregar dados de municípios: {e}")
        return pd.DataFrame()

# Função para carregar estatísticas gerais
@st.cache_data
def carregar_estatisticas_gerais():
    try:
        # Carregar dados de UFs
        df_ufs = carregar_dados_municipios()
        if df_ufs.empty:
            return pd.DataFrame({
                'total_anos': [12],
                'ano_inicio': [2014],
                'ano_fim': [2025],
                'total_casos': [5000000],
                'total_municipios': [5000] # ADICIONADO: Valor padrão para consistência
            })
        
        # Calcular estatísticas
        stats = {
            'total_anos': len(df_ufs['Ano'].unique()),
            'ano_inicio': df_ufs['Ano'].min(),
            'ano_fim': df_ufs['Ano'].max(),
            'total_casos': df_ufs['Casos'].sum(),
            'total_municipios': df_ufs['Municipio'].nunique()
        }
        
        return pd.DataFrame([stats])
        
    except Exception as e:
        st.error(f"Erro ao calcular estatísticas: {e}")
        return pd.DataFrame({
            'total_anos': [12],
            'ano_inicio': [2014],
            'ano_fim': [2025],
            'total_casos': [5000000],
            'total_municipios': [5000] # ADICIONADO: Valor padrão para consistência
        })

# Header principal
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #1f77b4; margin-bottom: 0.5rem;">🦟 Dashboard de Análise de Dengue</h1>
    <h3 style="color: #666; font-weight: normal;">Análise Temporal e Espacial de Casos de Dengue no Brasil</h3>
</div>
""", unsafe_allow_html=True)

# Carregar estatísticas gerais
try:
    stats = carregar_estatisticas_gerais()
    if not stats.empty:
        total_anos = stats['total_anos'].iloc[0]
        ano_inicio = stats['ano_inicio'].iloc[0]
        ano_fim = stats['ano_fim'].iloc[0]
        total_casos = stats['total_casos'].iloc[0]
        total_municipios = stats['total_municipios'].iloc[0]
    else:
        total_anos = 12
        ano_inicio = 2014
        ano_fim = 2025
        total_casos = 5000000
        total_municipios = 5000
except:
    total_anos = 12
    ano_inicio = 2014
    ano_fim = 2025
    total_casos = 5000000
    total_municipios = 5000

# Métricas principais
st.markdown("### Visão Geral dos Dados")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Período de Análise",
        value=f"{ano_inicio} - {ano_fim}",
        delta=f"{total_anos} anos"
    )

with col2:
    st.metric(
        label="Total de Casos",
        value=f"{total_casos:,}".replace(",", "."),
        delta="Registros"
    )

with col3:
    st.metric(
        label="Estados Monitorados",
        value="27",
        delta="Unidades Federativas"
    )

with col4:
    st.metric(
        label="Municípios",
        value=f"{total_municipios:,}".replace(",", "."),
        delta="Cidades Brasileiras"
    )

# Seção de introdução
st.markdown("---")

# Seção de funcionalidades
st.markdown("### Páginas Disponíveis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📈 Análise Temporal
    - Gráficos de linha interativos
    - Múltiplas granularidades: Semanal, Mensal, Anual
    - Filtros por região: Estados e Municípios
    - Casos absolutos e Taxa de incidência
    """)

with col2:
    st.markdown("""
    #### 🗺️ Análise Espacial
    - Mapas interativos por estado e município
    - Visualização geográfica da distribuição de casos
    - Comparação regional de incidência
    """)


# Seção de informações técnicas
st.markdown("---")
st.markdown("### Informações Adicionais")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📊 Fonte dos Dados
    - **DATASUS**
    - **Período**: 2014 a 2025
    - **Cobertura**: Todos os estados brasileiros
    """)

with col2:
    st.markdown("""
    #### 🛠️ Tecnologias Utilizadas
    - **Streamlit**: Interface web interativa
    - **Plotly**: Gráficos e visualizações
    - **Pandas**: Manipulação e processamento de dados
    - **Parquet**: Armazenamento eficiente de dados
    - **GeoJSON**: Dados geográficos
    """)

# Footer
st.markdown("---")



