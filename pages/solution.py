import streamlit as st

st.subheader("", divider="blue")
st.markdown(
    """
        Selecionar os 5 candidatos mais aderentes a uma vaga, com base em:

        - Conhecimentos técnicos requeridos (vaga)

        - Nível de inglês e espanhol (vaga vs candidato)

        Lógica do Agente

        1. Input
        Código da vaga (ex: 10976)

        Acesso aos três arquivos: Jobs.json, Prospects.json, Applicants.json

        2. Extração da Vaga

        Lista de competências técnicas (competencias, conhecimentos técnicos, etc.)

        Nível exigido de inglês e espanhol

        3. Filtrar candidatos da vaga

        Pegar todos os códigos de candidatos do Prospects.json[codigo_vaga]

        4. Comparar cada candidato

        Conhecimentos técnicos (aplicando vetorização e similaridade com os da vaga)

        Se atende o nível de idiomas exigido

        Calcular um score combinado:

            score = similaridade_tecnica * peso + match_idiomas * outro_peso

        5. Retornar top 5 candidatos com maior score
    """

)