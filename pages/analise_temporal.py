import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configurações da Página ---
# st.set_page_config(layout="wide") # Já deve estar no app.py

# --- Função de Carregamento de Dados (SIMPLIFICADA) ---

@st.cache_data
def carregar_dados_municipios():
    """Carrega os dados de dengue dos municípios, sem converter datas."""
    caminho_arquivo = 'data/dados_dengue_municipios.parquet'
    try:
        # Apenas lê o arquivo, sem processamento de datas
        df = pd.read_parquet(caminho_arquivo)
        return df
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_ufs():
    """Carrega os dados de dengue das UFs."""
    caminho_arquivo = 'data/dados_dengue_ufs.parquet'
    try:
        df = pd.read_parquet(caminho_arquivo)
        return df
    except FileNotFoundError:
        st.error(f"Arquivo de dados de UFs não encontrado: {caminho_arquivo}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados de UFs: {e}")
        return pd.DataFrame()

# --- Carregamento Inicial ---
df_municipios = carregar_dados_municipios()
df_ufs = carregar_dados_ufs()

# --- Layout da Página ---

st.title("📈 Análise Temporal de Casos de Dengue")
st.markdown("Explore a evolução dos casos ao longo do tempo. Selecione a granularidade (anual, mensal, semanal) e os locais de interesse.")

# --- Barra Lateral de Filtros (Sidebar) ---
st.sidebar.header("Filtros da Análise")

if not df_municipios.empty and not df_ufs.empty:
    # Filtros simplificados conforme solicitado
    granularidade = st.sidebar.radio(
        "Selecione a Granularidade:",
        options=['Ano', 'Mês', 'Semana'],
        horizontal=True
    )
    
    # Período baseado nos dados de municípios (mais completos)
    anos = sorted(df_municipios['Ano'].unique())
    ano_inicio, ano_fim = st.sidebar.select_slider(
        "Selecione o Período:",
        options=anos,
        value=(anos[0], anos[-1])
    )

    tipo_dado = st.sidebar.radio("Selecione a Métrica:", options=['Casos', 'Taxa'], horizontal=True)

    # Seleção de UF
    ufs_disponiveis = sorted(df_ufs['UF'].unique())
    ufs_selecionadas = st.sidebar.multiselect("Selecione UF:", options=ufs_disponiveis)

    # Seleção de municípios
    municipios_disponiveis = sorted(df_municipios['Municipio'].unique())
    municipios_selecionados = st.sidebar.multiselect("Selecione Município:", options=municipios_disponiveis)

    # --- Área Principal da Página ---

    # Verificar se há seleções
    tem_ufs = len(ufs_selecionadas) > 0
    tem_municipios = len(municipios_selecionados) > 0

    if tem_ufs or tem_municipios:
        # Criar gráficos para UFs selecionadas
        if tem_ufs:
            st.subheader("📊 Análise por Estados (UFs)")
            
            df_filtrado_ufs = df_ufs[
                (df_ufs['Ano'] >= ano_inicio) &
                (df_ufs['Ano'] <= ano_fim) &
                (df_ufs['UF'].isin(ufs_selecionadas))
            ]
            
            # Remove valores NA antes do agrupamento
            df_filtrado_ufs = df_filtrado_ufs.dropna(subset=[tipo_dado])
            
            # Define as colunas de agrupamento baseado na granularidade
            if granularidade == 'Ano':
                colunas_grupo = ['Ano', 'UF']
                colunas_ordem = ['Ano']
                coluna_eixo_x = 'Ano'
                titulo_grafico = f'{tipo_dado} Anuais por Estado'
            elif granularidade == 'Mês':
                colunas_grupo = ['Ano', 'Mes', 'UF']
                colunas_ordem = ['Ano', 'Mes']
                coluna_eixo_x = 'Mes'
                titulo_grafico = f'{tipo_dado} Mensais por Estado'
            else: # Semana
                colunas_grupo = ['Ano', 'Mes', 'Semana', 'UF']
                colunas_ordem = ['Ano', 'Mes', 'Semana']
                coluna_eixo_x = 'Semana'
                titulo_grafico = f'{tipo_dado} Semanais por Estado'

            # Agrupa os dados
            df_agrupado_ufs = df_filtrado_ufs.groupby(colunas_grupo)[tipo_dado].sum().reset_index()

            # Ordena o DataFrame para garantir a ordem cronológica no gráfico
            df_agrupado_ufs.sort_values(by=colunas_ordem, inplace=True)

            # Cria o gráfico de linha para UFs
            fig_ufs = px.line(
                df_agrupado_ufs,
                x=coluna_eixo_x,
                y=tipo_dado,
                color='UF',
                title=titulo_grafico,
                labels={
                    coluna_eixo_x: granularidade,
                    tipo_dado: tipo_dado,
                    'UF': 'Estados'
                }
            )
            
            # Remove linha de tendência e melhora a visualização
            fig_ufs.update_traces(mode='lines', line=dict(width=2), connectgaps=False)
            
            # Ajusta ângulo e quantidade de ticks baseado na granularidade
            if granularidade == 'Ano':
                fig_ufs.update_xaxes(tickangle=0, nticks=len(df_agrupado_ufs['Ano'].unique()))
            elif granularidade == 'Mês':
                fig_ufs.update_xaxes(tickangle=45, nticks=50)
            else: # Semana
                fig_ufs.update_xaxes(tickangle=45, nticks=50)
            
            fig_ufs.update_layout(
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis_title=granularidade,
                yaxis_title=f'Número de {tipo_dado}'
            )

            st.plotly_chart(fig_ufs, use_container_width=True)

            # Tabela para UFs
            with st.expander("Visualizar dados dos Estados"):
                # Seleciona apenas as colunas relevantes para a granularidade selecionada
                if granularidade == 'Ano':
                    colunas_tabela = ['Ano', 'UF', tipo_dado]
                elif granularidade == 'Mês':
                    colunas_tabela = ['Mes', 'UF', tipo_dado]
                else: # Semana
                    colunas_tabela = ['Semana', 'UF', tipo_dado]
                
                df_tabela_ufs = df_agrupado_ufs[colunas_tabela].copy()
                st.dataframe(df_tabela_ufs, use_container_width=True)
                
                # Estatísticas resumidas para UFs
                st.subheader("Estatísticas Resumidas - Estados")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total = df_tabela_ufs[tipo_dado].sum()
                    st.metric(f"Total de {tipo_dado}", f"{total:,.0f}" if tipo_dado == "Casos" else f"{total:,.2f}")
                
                with col2:
                    media = df_tabela_ufs[tipo_dado].mean()
                    st.metric(f"Média de {tipo_dado}", f"{media:,.0f}" if tipo_dado == "Casos" else f"{media:,.2f}")
                
                with col3:
                    max_valor = df_tabela_ufs[tipo_dado].max()
                    st.metric(f"Máximo de {tipo_dado}", f"{max_valor:,.0f}" if tipo_dado == "Casos" else f"{max_valor:,.2f}")

        # Criar gráficos para municípios selecionados
        if tem_municipios:
            if tem_ufs:
                st.markdown("---")
            
            st.subheader("🏙️ Análise por Municípios")
            
            df_filtrado_municipios = df_municipios[
                (df_municipios['Ano'] >= ano_inicio) &
                (df_municipios['Ano'] <= ano_fim) &
                (df_municipios['Municipio'].isin(municipios_selecionados))
            ]
            
            # Remove valores NA antes do agrupamento
            df_filtrado_municipios = df_filtrado_municipios.dropna(subset=[tipo_dado])
            
            # Define as colunas de agrupamento baseado na granularidade
            if granularidade == 'Ano':
                colunas_grupo = ['Ano', 'Municipio']
                colunas_ordem = ['Ano']
                coluna_eixo_x = 'Ano'
                titulo_grafico = f'{tipo_dado} Anuais por Município'
            elif granularidade == 'Mês':
                colunas_grupo = ['Ano', 'Mes', 'Municipio']
                colunas_ordem = ['Ano', 'Mes']
                coluna_eixo_x = 'Mes'
                titulo_grafico = f'{tipo_dado} Mensais por Município'
            else: # Semana
                colunas_grupo = ['Ano', 'Mes', 'Semana', 'Municipio']
                colunas_ordem = ['Ano', 'Mes', 'Semana']
                coluna_eixo_x = 'Semana'
                titulo_grafico = f'{tipo_dado} Semanais por Município'

            # Agrupa os dados
            df_agrupado_municipios = df_filtrado_municipios.groupby(colunas_grupo)[tipo_dado].sum().reset_index()

            # Ordena o DataFrame para garantir a ordem cronológica no gráfico
            df_agrupado_municipios.sort_values(by=colunas_ordem, inplace=True)

            # Cria o gráfico de linha para municípios
            fig_municipios = px.line(
                df_agrupado_municipios,
                x=coluna_eixo_x,
                y=tipo_dado,
                color='Municipio',
                title=titulo_grafico,
                labels={
                    coluna_eixo_x: granularidade,
                    tipo_dado: tipo_dado,
                    'Municipio': 'Municípios'
                }
            )
            
            # Remove linha de tendência e melhora a visualização
            fig_municipios.update_traces(mode='lines', line=dict(width=2), connectgaps=False)
            
            # Ajusta ângulo e quantidade de ticks baseado na granularidade
            if granularidade == 'Ano':
                fig_municipios.update_xaxes(tickangle=0, nticks=len(df_agrupado_municipios['Ano'].unique()))
            elif granularidade == 'Mês':
                fig_municipios.update_xaxes(tickangle=45, nticks=50)
            else: # Semana
                fig_municipios.update_xaxes(tickangle=45, nticks=50)
            
            fig_municipios.update_layout(
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis_title=granularidade,
                yaxis_title=f'Número de {tipo_dado}'
            )

            st.plotly_chart(fig_municipios, use_container_width=True)

            # Tabela para municípios
            with st.expander("Visualizar dados dos Municípios"):
                # Seleciona apenas as colunas relevantes para a granularidade selecionada
                if granularidade == 'Ano':
                    colunas_tabela = ['Ano', 'Municipio', tipo_dado]
                elif granularidade == 'Mês':
                    colunas_tabela = ['Mes', 'Municipio', tipo_dado]
                else: # Semana
                    colunas_tabela = ['Semana', 'Municipio', tipo_dado]
                
                df_tabela_municipios = df_agrupado_municipios[colunas_tabela].copy()
                st.dataframe(df_tabela_municipios, use_container_width=True)
                
                # Estatísticas resumidas para municípios
                st.subheader("Estatísticas Resumidas - Municípios")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total = df_tabela_municipios[tipo_dado].sum()
                    st.metric(f"Total de {tipo_dado}", f"{total:,.0f}" if tipo_dado == "Casos" else f"{total:,.2f}")
                
                with col2:
                    media = df_tabela_municipios[tipo_dado].mean()
                    st.metric(f"Média de {tipo_dado}", f"{media:,.0f}" if tipo_dado == "Casos" else f"{media:,.2f}")
                
                with col3:
                    max_valor = df_tabela_municipios[tipo_dado].max()
                    st.metric(f"Máximo de {tipo_dado}", f"{max_valor:,.0f}" if tipo_dado == "Casos" else f"{max_valor:,.2f}")
    else:
        st.info("Por favor, selecione pelo menos uma UF ou município na barra lateral para iniciar a análise.")

else:
    st.warning("Não foi possível carregar os dados. Verifique a configuração dos arquivos de dados.")