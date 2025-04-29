import streamlit as st
from st_pages import get_nav_from_toml, add_page_title

if not st.session_state.get("page_config_done"):
    st.set_page_config(page_title="Datathon Phase 5 | FIAP", layout="wide", initial_sidebar_state="expanded")
    st.session_state["page_config_done"] = True

nav = get_nav_from_toml("Streamlit_Fase5/streamlit/pages.toml")
pg = st.navigation(nav)
add_page_title(pg)

with st.sidebar:
    st.subheader("Componentes do Grupo 6")
    st.write("Daniel Bispo dos Santos - rm356863")
    st.write("Lucia Maria Fraga Teixeira - rm357817")
    st.write("Yury Jorge Luiz Phelippe Antony Barros - rm357915")
    st.subheader("Turma")
    st.write("6DTAT")
pg.run()
