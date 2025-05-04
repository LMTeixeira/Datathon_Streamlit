import streamlit as st
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Carregar o modelo de linguagem do spaCy
nlp = spacy.load("pt_core_news_lg")

# Funções auxiliares
def nivel_idioma_to_int(nivel):
    mapa = {"nenhum": 0, "básico": 1, "intermediário": 2, "avançado": 3, "fluente": 4}
    return mapa.get(nivel.lower(), 0)

def nivel_academico_to_int(nivel):
    mapa = {
        "ensino fundamental": 1,
        "ensino médio": 2,
        "ensino técnico completo": 3,
        "ensino superior incompleto": 4,
        "ensino superior cursando": 5,
        "ensino superior completo": 6,
        "pós-graduação": 7,
        "mba": 8,
        "mestrado": 9,
        "doutorado": 10
    }
    return mapa.get(nivel.lower(), 0)

def comparar_idiomas(nivel_requerido, nivel_candidato):
    return nivel_idioma_to_int(nivel_candidato) >= nivel_idioma_to_int(nivel_requerido)

def analisar_curriculo_com_spacy(cv_texto):
    """
    Realiza a análise do currículo utilizando spaCy.

    Args:
        cv_texto (str): O texto do currículo.

    Returns:
        dict: Um dicionário contendo os resultados da análise.
    """

    doc = nlp(cv_texto)

    # Extrair informações básicas (simplificado para este exemplo)
    habilidades = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "ADJ"]]
    experiencia = [ent.text.lower() for ent in doc.ents if ent.label_ == "ORG"]
    formacao = [ent.text.lower() for ent in doc.ents if ent.label_ == "EDU"]

    return {
        "habilidades": habilidades,
        "experiencia": experiencia,
        "formacao": formacao
    }

def comparar_cv_com_vaga(cv_analise, requisitos_vaga):
    """
    Compara as informações do currículo com os requisitos da vaga.

    Args:
        cv_analise (dict): O resultado da análise do currículo.
        requisitos_vaga (str): Os requisitos da vaga.

    Returns:
        float: A pontuação de compatibilidade.
    """

    pontuacao = 0

    # Converter requisitos da vaga para um documento spaCy para análise
    doc_requisitos = nlp(requisitos_vaga.lower())
    tokens_requisitos = [token.text for token in doc_requisitos if token.pos_ in ["NOUN", "ADJ"]]
    entidades_requisitos = {ent.text.lower(): ent.label_ for ent in doc_requisitos.ents}

    # Comparar habilidades
    habilidades_encontradas = set(cv_analise["habilidades"]) & set(tokens_requisitos)
    pontuacao += len(habilidades_encontradas) * 2

    # Comparar experiência
    experiencia_encontrada = set(cv_analise["experiencia"]) & set(entidades_requisitos.keys())
    pontuacao += len(experiencia_encontrada) * 1.5

    # Comparar formação
    formacao_encontrada = set(cv_analise["formacao"]) & set(entidades_requisitos.keys())
    pontuacao += len(formacao_encontrada) * 1

    return pontuacao

def agente_top_candidatos(vaga, candidatos_ids, applicants, top_k=5):
    requisitos_tecnicos = vaga.get("perfil_vaga", {}).get("competencia_tecnicas_e_comportamentais", "") + " " + vaga.get("perfil_vaga", {}).get("principais_atividades", "")
    idioma_ingles_req = vaga.get("perfil_vaga", {}).get("nivel_ingles", "básico")
    idioma_espanhol_req = vaga.get("perfil_vaga", {}).get("nivel_espanhol", "básico")

    docs_tecnicos = []
    candidatos_info = []

    for cid in candidatos_ids:
        candidato = applicants.get(str(cid))
        if not candidato:
            continue

        formacao = candidato.get("formacao_e_idiomas", {})

        conhecimentos = " ".join(
            candidato.get("informacoes_profissionais", {}).get("conhecimentos_tecnicos", "").split(";")
        )
        docs_tecnicos.append(conhecimentos)

        ingles_ok = comparar_idiomas(idioma_ingles_req, formacao.get("nivel_ingles", "nenhum"))
        espanhol_ok = comparar_idiomas(idioma_espanhol_req, formacao.get("nivel_espanhol", "nenhum"))

        cv_texto = candidato.get("cv_pt", "")
        cv_analise = analisar_curriculo_com_spacy(cv_texto)
        cv_score = comparar_cv_com_vaga(cv_analise, requisitos_tecnicos)

        candidatos_info.append({
            "id": cid,
            "nome": candidato["informacoes_pessoais"]["nome"],
            "conhecimentos": conhecimentos,
            "ingles_ok": ingles_ok,
            "espanhol_ok": espanhol_ok,
            "cv_score": cv_score
        })

    if not docs_tecnicos:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([requisitos_tecnicos] + docs_tecnicos)
    vaga_vector = tfidf_matrix[0]
    candidatos_vectors = tfidf_matrix[1:]
    similaridades = cosine_similarity(vaga_vector, candidatos_vectors).flatten()

    resultados = []
    for i, cand in enumerate(candidatos_info):
        match_idiomas = cand["ingles_ok"] and cand["espanhol_ok"]
        score = similaridades[i] + (0.2 if match_idiomas else 0) + (cand["cv_score"] * 0.1) # Ajuste o peso do CV (0.1)
        resultados.append((cand["nome"], cand["id"], round(score, 4)))

    return sorted(resultados, key=lambda x: x[2], reverse=True)[:top_k]

# Streamlit App
st.subheader("📂 Envie os arquivos JSON")
file_applicants = st.file_uploader("Applicants.json", type="json")
file_jobs = st.file_uploader("Vagas.json", type="json")
file_prospects = st.file_uploader("Prospects.json", type="json")

if file_applicants and file_jobs and file_prospects:
    applicants = json.load(file_applicants)
    jobs = json.load(file_jobs)
    prospects = json.load(file_prospects)

    st.success("Arquivos carregados com sucesso!")

    # Mapeia os nomes das vagas (título da vaga vindo de vagas.json)
    nome_para_codigo = {
        vaga["informacoes_basicas"].get("titulo_vaga", f"Sem título ({codigo})"): codigo
        for codigo, vaga in jobs.items()
    }

    nome_selecionado = st.selectbox("Selecione a vaga", list(nome_para_codigo.keys()))
    vaga_codigo = nome_para_codigo[nome_selecionado]
    vaga = jobs[vaga_codigo]

    # Extrai os códigos dos candidatos da estrutura correta do prospects.json
    candidatos_ids = [
        c["codigo"] for c in prospects.get(vaga_codigo, {}).get("prospects", [])
        if "codigo" in c
    ]

    st.markdown(f"**👔 Cliente:** {vaga['informacoes_basicas'].get('cliente', 'Não informado')}")
    st.markdown(f"**🛠 Competências Técnicas:** {vaga['perfil_vaga'].get('competencia_tecnicas_e_comportamentais', 'Não informado')}")
    st.markdown(f"**🌍 Idiomas exigidos:** Inglês - {vaga['perfil_vaga'].get('nivel_ingles', 'Básico')} | Espanhol - {vaga['perfil_vaga'].get('nivel_espanhol', 'Básico')}")

    if st.button("🔎 Encontrar Top 5 Candidatos"):
        top_candidatos = agente_top_candidatos(vaga, candidatos_ids, applicants)

        if top_candidatos:
            st.subheader("🏆 Top 5 Candidatos")
            for nome, cid, score in top_candidatos:
                st.markdown(f"**{nome}** (ID {cid}) — Score: `{score}`")
        else:
            st.warning("Nenhum candidato atende aos critérios da vaga.")