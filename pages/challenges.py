import streamlit as st

st.subheader("", divider="blue")
st.markdown(
    """
        Tivemos alguns desafios na construção da solução:

        - Dificuldade em identificar o melhor campo do arquivo applicants.json para comparar
          os requisitos dos candidatos com os das vagas;

        - Arquivos muito grandes para processar em notebooks não muito potentes.

        Além disso, essa solução pode ser aprimorada para trabalhar com uma base de dados na nuvem
        possibilitando o cadastro de novas vagas e a verificação de candidatos aderentes à ela
        independente se o candidato aplicou ou não para a vaga.

    """
)