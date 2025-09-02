import streamlit as st

# Configuração da página principal (SÓ AQUI)
st.set_page_config(
    page_title="Análise Temporal de Dengue",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definição das páginas da aplicação
paginas = {
    "Páginas": [
        st.Page("pages/home_page.py", title="Página Inicial", icon="🏠", default=True),
        st.Page("pages/analise_temporal.py", title="Análise Temporal", icon="📈"),
        st.Page("pages/mapas.py", title="Análise Espacial", icon="🗺️"),
        #st.Page("pages/previsao.py", title="Previsão", icon="📈"),
    ]
    #"Contato": [
    #   st.Page("pages/fale_concosco.py", title="Fale Conosco", icon="📬")
    #],
}

# Executar a navegação
pg = st.navigation(paginas)
pg.run()