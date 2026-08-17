import pandas as pd
import streamlit as st

from core.matcher import calculate_match, classify_match
from core.parser import extract_candidate_name, extract_text_from_pdf
from core.skills import get_skill_catalog


st.set_page_config(
    page_title="RH Talent Matcher",
    page_icon="🎯",
    layout="wide",
)


st.title("🎯 RH Talent Matcher")
st.caption(
    "Sistema de apoio à triagem de currículos por competências."
)

st.info(
    "A ferramenta gera indicadores de aderência para apoio ao recrutador. "
    "A decisão de contratação deve permanecer humana e considerar o contexto completo do candidato."
)


# ============================================================
# CONFIGURAÇÃO DA VAGA
# ============================================================

st.header("1. Configuração da vaga")

job_title = st.text_input(
    "Nome da vaga",
    placeholder="Ex.: Analista de RH Sênior",
)

skill_catalog = get_skill_catalog()

col1, col2 = st.columns(2)

with col1:
    required_skills = st.multiselect(
        "Competências obrigatórias",
        options=skill_catalog,
        help="Competências consideradas essenciais para a vaga.",
    )

with col2:
    desired_skills = st.multiselect(
        "Competências desejáveis",
        options=[
            skill
            for skill in skill_catalog
            if skill not in required_skills
        ],
        help="Competências que agregam valor, mas não são obrigatórias.",
    )


# ============================================================
# PESOS
# ============================================================

st.subheader("Pesos da análise")

required_weight_percent = st.slider(
    "Peso das competências obrigatórias",
    min_value=50,
    max_value=90,
    value=70,
    step=5,
)

desired_weight_percent = 100 - required_weight_percent

st.write(
    f"Obrigatórias: **{required_weight_percent}%** | "
    f"Desejáveis: **{desired_weight_percent}%**"
)

required_weight = required_weight_percent / 100
desired_weight = desired_weight_percent / 100


# ============================================================
# CURRÍCULOS
# ============================================================

st.header("2. Currículos")

uploaded_files = st.file_uploader(
    "Selecione um ou mais currículos em PDF",
    type=["pdf"],
    accept_multiple_files=True,
)


# ============================================================
# PROCESSAMENTO
# ============================================================

if st.button(
    "Analisar currículos",
    type="primary",
    use_container_width=True,
):

    if not job_title.strip():
        st.warning("Informe o nome da vaga.")

    elif not required_skills:
        st.warning(
            "Selecione pelo menos uma competência obrigatória."
        )

    elif not uploaded_files:
        st.warning("Adicione pelo menos um currículo em PDF.")

    else:

        results = []

        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):

            try:
                curriculum_text = extract_text_from_pdf(
                    uploaded_file
                )

                candidate_name = extract_candidate_name(
                    curriculum_text
                )

                analysis = calculate_match(
                    curriculum_text=curriculum_text,
                    required_skills=required_skills,
                    desired_skills=desired_skills,
                    required_weight=required_weight,
                    desired_weight=desired_weight,
                )

                results.append(
                    {
                        "Candidato": candidate_name,
                        "Arquivo": uploaded_file.name,
                        "Aderência": analysis["aderencia"],
                        "Classificação": classify_match(
                            analysis["aderencia"]
                        ),
                        "Obrigatórias": (
                            f'{len(analysis["obrigatorias_encontradas"])}'
                            f'/{len(required_skills)}'
                        ),
                        "Desejáveis": (
                            f'{len(analysis["desejaveis_encontradas"])}'
                            f'/{len(desired_skills)}'
                            if desired_skills
                            else "0/0"
                        ),
                        "Análise": analysis,
                    }
                )

            except Exception as exc:

                st.error(
                    f"Erro ao processar {uploaded_file.name}: {exc}"
                )

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        progress.empty()

        if results:

            results = sorted(
                results,
                key=lambda item: item["Aderência"],
                reverse=True,
            )

            st.success(
                f"{len(results)} currículo(s) analisado(s)."
            )


            # ====================================================
            # DASHBOARD
            # ====================================================

            st.header("3. Ranking de aderência")

            dashboard = pd.DataFrame(
                [
                    {
                        "Candidato": item["Candidato"],
                        "Aderência (%)": item["Aderência"],
                        "Classificação": item["Classificação"],
                        "Obrigatórias": item["Obrigatórias"],
                        "Desejáveis": item["Desejáveis"],
                        "Arquivo": item["Arquivo"],
                    }
                    for item in results
                ]
            )

            st.dataframe(
                dashboard,
                use_container_width=True,
                hide_index=True,
            )


            # ====================================================
            # ANÁLISE INDIVIDUAL
            # ====================================================

            st.header("4. Análise individual")

            for position, result in enumerate(
                results,
                start=1,
            ):

                analysis = result["Análise"]

                with st.expander(
                    f"{position}º - "
                    f"{result['Candidato']} | "
                    f"{result['Aderência']}% | "
                    f"{result['Classificação']}"
                ):

                    col_a, col_b, col_c = st.columns(3)

                    col_a.metric(
                        "Aderência geral",
                        f"{result['Aderência']}%",
                    )

                    col_b.metric(
                        "Obrigatórias",
                        result["Obrigatórias"],
                    )

                    col_c.metric(
                        "Desejáveis",
                        result["Desejáveis"],
                    )

                    st.subheader(
                        "Competências obrigatórias"
                    )

                    if analysis["obrigatorias_encontradas"]:
                        for skill in analysis[
                            "obrigatorias_encontradas"
                        ]:
                            st.write(f"✅ {skill}")

                    if analysis["obrigatorias_ausentes"]:
                        for skill in analysis[
                            "obrigatorias_ausentes"
                        ]:
                            st.write(f"❌ {skill}")


                    st.subheader(
                        "Competências desejáveis"
                    )

                    if desired_skills:

                        if analysis[
                            "desejaveis_encontradas"
                        ]:
                            for skill in analysis[
                                "desejaveis_encontradas"
                            ]:
                                st.write(f"✅ {skill}")

                        if analysis[
                            "desejaveis_ausentes"
                        ]:
                            for skill in analysis[
                                "desejaveis_ausentes"
                            ]:
                                st.write(f"❌ {skill}")

                    else:
                        st.write(
                            "Nenhuma competência desejável configurada."
                        )


                    st.subheader(
                        "Competências identificadas no currículo"
                    )

                    detected = analysis[
                        "competencias_detectadas"
                    ]

                    if detected:
                        st.write(
                            " • ".join(detected)
                        )
                    else:
                        st.write(
                            "Nenhuma competência do catálogo foi identificada."
                        )


                    st.subheader("Evidências encontradas")

                    evidences = analysis["evidencias"]

                    if evidences:

                        for skill, aliases in evidences.items():

                            st.write(
                                f"**{skill}:** "
                                + ", ".join(aliases)
                            )

                    else:
                        st.write(
                            "Nenhuma evidência identificada."
                        )


            # ====================================================
            # EXPORTAÇÃO
            # ====================================================

            st.header("5. Exportação")

            csv_data = dashboard.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Baixar ranking em CSV",
                data=csv_data,
                file_name="ranking_curriculos.csv",
                mime="text/csv",
                use_container_width=True,
            )