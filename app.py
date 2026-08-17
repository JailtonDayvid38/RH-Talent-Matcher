import io

import pandas as pd
import streamlit as st

from core.matcher import (
    calculate_match,
    classify_match,
    recommend_candidate,
)
from core.parser import extract_candidate_name, extract_text_from_pdf
from core.skills import detect_skills, get_skill_catalog


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

job_description = st.text_area(
    "Descrição da vaga (opcional)",
    placeholder=(
        "Cole aqui a descrição da vaga. O sistema poderá sugerir competências "
        "já existentes no catálogo."
    ),
    height=160,
)

skill_catalog = get_skill_catalog()

if "critical_skills" not in st.session_state:
    st.session_state["critical_skills"] = []

if "required_skills" not in st.session_state:
    st.session_state["required_skills"] = []

if "desired_skills" not in st.session_state:
    st.session_state["desired_skills"] = []

if st.button("✨ Sugerir competências pela descrição da vaga"):
    if not job_description.strip():
        st.warning("Cole uma descrição de vaga para gerar sugestões.")
    else:
        description_analysis = detect_skills(job_description)
        suggested = description_analysis["competencias"]

        if suggested:
            current_required = list(st.session_state.get("required_skills", []))
            merged = []
            for skill in current_required + suggested:
                if skill not in merged:
                    merged.append(skill)

            st.session_state["required_skills"] = [
                skill
                for skill in merged
                if skill not in st.session_state.get("critical_skills", [])
            ]

            st.success(
                f"{len(suggested)} competência(s) sugerida(s) e adicionada(s) "
                "às obrigatórias. Revise antes de analisar os currículos."
            )
        else:
            st.info(
                "Nenhuma competência do catálogo foi identificada na descrição."
            )


col1, col2, col3 = st.columns(3)

with col1:
    critical_skills = st.multiselect(
        "Competências críticas",
        options=skill_catalog,
        key="critical_skills",
        help=(
            "Competências essenciais de alto impacto. A ausência de uma crítica "
            "limita a recomendação final, mesmo com boa pontuação."
        ),
    )

with col2:
    required_options = [
        skill
        for skill in skill_catalog
        if skill not in critical_skills
    ]

    # remove seleções antigas que passaram a ser críticas
    st.session_state["required_skills"] = [
        skill
        for skill in st.session_state.get("required_skills", [])
        if skill in required_options
    ]

    required_skills = st.multiselect(
        "Competências obrigatórias",
        options=required_options,
        key="required_skills",
        help="Competências necessárias para boa aderência à vaga.",
    )

with col3:
    desired_options = [
        skill
        for skill in skill_catalog
        if skill not in critical_skills
        and skill not in required_skills
    ]

    # remove seleções antigas que passaram a ser críticas/obrigatórias
    st.session_state["desired_skills"] = [
        skill
        for skill in st.session_state.get("desired_skills", [])
        if skill in desired_options
    ]

    desired_skills = st.multiselect(
        "Competências desejáveis",
        options=desired_options,
        key="desired_skills",
        help="Competências que agregam valor, mas não são eliminatórias.",
    )


# ============================================================
# PESOS
# ============================================================

st.subheader("Pesos da análise")

required_weight_percent = st.slider(
    "Peso do bloco essencial (críticas + obrigatórias)",
    min_value=50,
    max_value=90,
    value=70,
    step=5,
)

desired_weight_percent = 100 - required_weight_percent

st.write(
    f"Essenciais: **{required_weight_percent}%** | "
    f"Desejáveis: **{desired_weight_percent}%**"
)

st.caption(
    "Se nenhuma competência desejável for configurada, o peso será automaticamente "
    "redistribuído para o bloco essencial."
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
# FUNÇÕES AUXILIARES DA INTERFACE
# ============================================================

def build_dashboard(results: list) -> pd.DataFrame:
    rows = []

    for item in results:
        analysis = item["Análise"]

        rows.append(
            {
                "Posição": item["Posição"],
                "Candidato": item["Candidato"],
                "Aderência (%)": item["Aderência"],
                "Recomendação": item["Recomendação"],
                "Classificação": item["Classificação"],
                "Críticas": item["Críticas"],
                "Obrigatórias": item["Obrigatórias"],
                "Desejáveis": item["Desejáveis"],
                "Críticas ausentes": ", ".join(
                    analysis["criticas_ausentes"]
                ) or "-",
                "Arquivo": item["Arquivo"],
            }
        )

    return pd.DataFrame(rows)


def build_details_dataframe(results: list) -> pd.DataFrame:
    rows = []

    for item in results:
        analysis = item["Análise"]

        rows.append(
            {
                "Posição": item["Posição"],
                "Candidato": item["Candidato"],
                "Arquivo": item["Arquivo"],
                "Aderência (%)": item["Aderência"],
                "Classificação": item["Classificação"],
                "Recomendação": item["Recomendação"],
                "Críticas encontradas": ", ".join(
                    analysis["criticas_encontradas"]
                ),
                "Críticas ausentes": ", ".join(
                    analysis["criticas_ausentes"]
                ),
                "Obrigatórias encontradas": ", ".join(
                    analysis["obrigatorias_encontradas"]
                ),
                "Obrigatórias ausentes": ", ".join(
                    analysis["obrigatorias_ausentes"]
                ),
                "Desejáveis encontradas": ", ".join(
                    analysis["desejaveis_encontradas"]
                ),
                "Desejáveis ausentes": ", ".join(
                    analysis["desejaveis_ausentes"]
                ),
                "Pontos fortes": ", ".join(
                    analysis["pontos_fortes"]
                ),
                "Lacunas": ", ".join(
                    analysis["lacunas"]
                ),
                "Competências detectadas": ", ".join(
                    analysis["competencias_detectadas"]
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# PROCESSAMENTO
# ============================================================

if st.button(
    "Analisar currículos",
    type="primary",
    use_container_width=True,
):

    essential_skills = list(critical_skills) + list(required_skills)

    if not job_title.strip():
        st.warning("Informe o nome da vaga.")

    elif not essential_skills:
        st.warning(
            "Selecione pelo menos uma competência crítica ou obrigatória."
        )

    elif not uploaded_files:
        st.warning("Adicione pelo menos um currículo em PDF.")

    else:
        results = []
        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):
            try:
                curriculum_text = extract_text_from_pdf(uploaded_file)

                candidate_name = extract_candidate_name(
                    curriculum_text,
                    file_name=uploaded_file.name,
                )

                analysis = calculate_match(
                    curriculum_text=curriculum_text,
                    critical_skills=critical_skills,
                    required_skills=required_skills,
                    desired_skills=desired_skills,
                    required_weight=required_weight,
                    desired_weight=desired_weight,
                )

                recommendation = recommend_candidate(analysis)

                results.append(
                    {
                        "Candidato": candidate_name,
                        "Arquivo": uploaded_file.name,
                        "Aderência": analysis["aderencia"],
                        "Classificação": classify_match(
                            analysis["aderencia"]
                        ),
                        "Recomendação": recommendation,
                        "Críticas": (
                            f'{len(analysis["criticas_encontradas"])}'
                            f'/{len(critical_skills)}'
                            if critical_skills
                            else "0/0"
                        ),
                        "Obrigatórias": (
                            f'{len(analysis["obrigatorias_encontradas"])}'
                            f'/{len(required_skills)}'
                            if required_skills
                            else "0/0"
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
            # Desempate:
            # 1) aderência geral
            # 2) menor número de críticas ausentes
            # 3) percentual do bloco essencial
            # 4) percentual de desejáveis
            # 5) total de competências detectadas
            results = sorted(
                results,
                key=lambda item: (
                    item["Aderência"],
                    -len(item["Análise"]["criticas_ausentes"]),
                    item["Análise"]["percentual_essenciais"],
                    item["Análise"]["percentual_desejaveis"],
                    len(item["Análise"]["competencias_detectadas"]),
                ),
                reverse=True,
            )

            for position, item in enumerate(results, start=1):
                item["Posição"] = position

            st.success(
                f"{len(results)} currículo(s) analisado(s)."
            )

            # ====================================================
            # DASHBOARD
            # ====================================================

            st.header("3. Ranking de aderência")

            dashboard = build_dashboard(results)

            st.dataframe(
                dashboard,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Em caso de empate na aderência, o ranking prioriza: "
                "menos competências críticas ausentes, maior aderência ao bloco "
                "essencial, maior aderência às desejáveis e maior número total "
                "de competências detectadas."
            )

            # ====================================================
            # ANÁLISE INDIVIDUAL
            # ====================================================

            st.header("4. Análise individual")

            for result in results:
                analysis = result["Análise"]

                with st.expander(
                    f"{result['Posição']}º - "
                    f"{result['Candidato']} | "
                    f"{result['Aderência']}% | "
                    f"{result['Recomendação']}"
                ):
                    col_a, col_b, col_c, col_d = st.columns(4)

                    col_a.metric(
                        "Aderência geral",
                        f"{result['Aderência']}%",
                    )

                    col_b.metric(
                        "Críticas",
                        result["Críticas"],
                    )

                    col_c.metric(
                        "Obrigatórias",
                        result["Obrigatórias"],
                    )

                    col_d.metric(
                        "Desejáveis",
                        result["Desejáveis"],
                    )

                    st.subheader("Recomendação")
                    st.write(
                        f"**{result['Recomendação']}** — "
                        f"{result['Classificação']}."
                    )

                    if analysis["criticas_ausentes"]:
                        st.warning(
                            "Competência(s) crítica(s) ausente(s): "
                            + ", ".join(analysis["criticas_ausentes"])
                        )

                    col_left, col_right = st.columns(2)

                    with col_left:
                        st.subheader("💪 Pontos fortes")
                        if analysis["pontos_fortes"]:
                            for skill in analysis["pontos_fortes"]:
                                st.write(f"✅ {skill}")
                        else:
                            st.write("Nenhum ponto forte identificado para a vaga.")

                    with col_right:
                        st.subheader("⚠️ Lacunas")
                        if analysis["lacunas"]:
                            for skill in analysis["lacunas"]:
                                st.write(f"❌ {skill}")
                        else:
                            st.write("Nenhuma lacuna identificada.")

                    st.subheader("Competências críticas")
                    if critical_skills:
                        for skill in analysis["criticas_encontradas"]:
                            st.write(f"✅ {skill}")
                        for skill in analysis["criticas_ausentes"]:
                            st.write(f"❌ {skill}")
                    else:
                        st.write("Nenhuma competência crítica configurada.")

                    st.subheader("Competências obrigatórias")
                    if required_skills:
                        for skill in analysis["obrigatorias_encontradas"]:
                            st.write(f"✅ {skill}")
                        for skill in analysis["obrigatorias_ausentes"]:
                            st.write(f"❌ {skill}")
                    else:
                        st.write("Nenhuma competência obrigatória configurada.")

                    st.subheader("Competências desejáveis")
                    if desired_skills:
                        for skill in analysis["desejaveis_encontradas"]:
                            st.write(f"✅ {skill}")
                        for skill in analysis["desejaveis_ausentes"]:
                            st.write(f"❌ {skill}")
                    else:
                        st.write(
                            "Nenhuma competência desejável configurada."
                        )

                    st.subheader(
                        "Competências identificadas no currículo"
                    )

                    detected = analysis["competencias_detectadas"]

                    if detected:
                        st.write(" • ".join(detected))
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

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                csv_data = dashboard.to_csv(
                    index=False
                ).encode("utf-8-sig")

                st.download_button(
                    "📄 Baixar ranking em CSV",
                    data=csv_data,
                    file_name="ranking_curriculos.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with export_col2:
                try:
                    details = build_details_dataframe(results)

                    excel_buffer = io.BytesIO()

                    with pd.ExcelWriter(
                        excel_buffer,
                        engine="openpyxl",
                    ) as writer:
                        dashboard.to_excel(
                            writer,
                            index=False,
                            sheet_name="Ranking",
                        )

                        details.to_excel(
                            writer,
                            index=False,
                            sheet_name="Analise_Detalhada",
                        )

                    st.download_button(
                        "📊 Baixar análise em Excel",
                        data=excel_buffer.getvalue(),
                        file_name="analise_curriculos.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                        use_container_width=True,
                    )

                except Exception:
                    st.info(
                        "Para exportar Excel, instale a dependência openpyxl."
                    )
