from core.skills import detect_skills


def calculate_match(
    curriculum_text: str,
    critical_skills: list | None = None,
    required_skills: list | None = None,
    desired_skills: list | None = None,
    required_weight: float = 0.70,
    desired_weight: float = 0.30,
) -> dict:
    """
    Calcula a aderência de um currículo a uma vaga.

    Regras principais:
    - competências críticas e obrigatórias formam o bloco essencial;
    - as competências críticas também influenciam a recomendação;
    - competências desejáveis complementam a nota;
    - se não houver competências desejáveis, o peso é
      redistribuído integralmente para o bloco essencial.
    """

    analysis = detect_skills(curriculum_text)

    detected_skills = set(analysis["competencias"])

    critical_skills = list(critical_skills or [])
    required_skills = list(required_skills or [])
    desired_skills = list(desired_skills or [])

    # ============================================================
    # EVITA DUPLICIDADE ENTRE OS GRUPOS
    # ============================================================

    required_skills = [
        skill
        for skill in required_skills
        if skill not in critical_skills
    ]

    desired_skills = [
        skill
        for skill in desired_skills
        if skill not in critical_skills
        and skill not in required_skills
    ]

    essential_skills = critical_skills + required_skills

    # ============================================================
    # COMPETÊNCIAS CRÍTICAS
    # ============================================================

    found_critical = [
        skill
        for skill in critical_skills
        if skill in detected_skills
    ]

    missing_critical = [
        skill
        for skill in critical_skills
        if skill not in detected_skills
    ]

    # ============================================================
    # COMPETÊNCIAS OBRIGATÓRIAS
    # ============================================================

    found_required = [
        skill
        for skill in required_skills
        if skill in detected_skills
    ]

    missing_required = [
        skill
        for skill in required_skills
        if skill not in detected_skills
    ]

    # ============================================================
    # COMPETÊNCIAS DESEJÁVEIS
    # ============================================================

    found_desired = [
        skill
        for skill in desired_skills
        if skill in detected_skills
    ]

    missing_desired = [
        skill
        for skill in desired_skills
        if skill not in detected_skills
    ]

    # ============================================================
    # BLOCO ESSENCIAL
    # Críticas + obrigatórias
    # ============================================================

    found_essential = (
        found_critical
        + found_required
    )

    missing_essential = (
        missing_critical
        + missing_required
    )

    if essential_skills:
        essential_score = (
            len(found_essential)
            / len(essential_skills)
        )
    else:
        essential_score = 0.0

    # ============================================================
    # BLOCO DESEJÁVEL
    # ============================================================

    if desired_skills:
        desired_score = (
            len(found_desired)
            / len(desired_skills)
        )
    else:
        desired_score = 0.0

    # ============================================================
    # NOTA FINAL
    # ============================================================

    # Se houver competências desejáveis:
    # aplica os pesos configurados.
    #
    # Se não houver desejáveis:
    # o bloco essencial passa a valer 100%.
    if desired_skills:
        total_score = (
            essential_score * required_weight
            + desired_score * desired_weight
        ) * 100

    else:
        total_score = (
            essential_score * 100
        )

    # ============================================================
    # PONTOS FORTES
    # Competências da vaga encontradas no currículo
    # ============================================================

    points_strong = (
        found_critical
        + found_required
        + found_desired
    )

    # ============================================================
    # LACUNAS
    # Competências da vaga não identificadas no currículo
    # ============================================================

    gaps = (
        missing_critical
        + missing_required
        + missing_desired
    )

    # ============================================================
    # RESULTADO
    # ============================================================

    return {
        "aderencia": round(
            total_score,
            1,
        ),

        "percentual_essenciais": round(
            essential_score * 100,
            1,
        ),

        "percentual_obrigatorias": round(
            (
                len(found_required)
                / len(required_skills)
                * 100
                if required_skills
                else 0
            ),
            1,
        ),

        "percentual_criticas": round(
            (
                len(found_critical)
                / len(critical_skills)
                * 100
                if critical_skills
                else 0
            ),
            1,
        ),

        "percentual_desejaveis": round(
            desired_score * 100,
            1,
        ),

        "criticas_encontradas":
            found_critical,

        "criticas_ausentes":
            missing_critical,

        "obrigatorias_encontradas":
            found_required,

        "obrigatorias_ausentes":
            missing_required,

        "desejaveis_encontradas":
            found_desired,

        "desejaveis_ausentes":
            missing_desired,

        "essenciais_encontradas":
            found_essential,

        "essenciais_ausentes":
            missing_essential,

        "pontos_fortes":
            points_strong,

        "lacunas":
            gaps,

        "competencias_detectadas":
            analysis["competencias"],

        "evidencias":
            analysis["evidencias"],
    }


def classify_match(score: float) -> str:
    """
    Classifica tecnicamente o nível de aderência
    do currículo à vaga.
    """

    if score >= 85:
        return "Alta aderência"

    if score >= 70:
        return "Boa aderência"

    if score >= 50:
        return "Aderência moderada"

    return "Baixa aderência"


def recommend_candidate(
    analysis: dict,
) -> str:
    """
    Gera uma recomendação de apoio à triagem.

    A classificação representa a aderência técnica.

    A recomendação representa uma sugestão de ação
    para o recrutador.

    Regras:
    - competência crítica ausente impede recomendação direta;
    - alta cobertura do bloco essencial favorece entrevista;
    - perfis intermediários devem ser avaliados;
    - baixa aderência gera recomendação de não priorização;
    - a decisão final continua sendo humana.
    """

    score = float(
        analysis.get(
            "aderencia",
            0,
        )
    )

    essential_percent = float(
        analysis.get(
            "percentual_essenciais",
            0,
        )
    )

    missing_critical = analysis.get(
        "criticas_ausentes",
        [],
    )

    # ============================================================
    # EXISTE COMPETÊNCIA CRÍTICA AUSENTE
    # ============================================================

    if missing_critical:

        if score >= 60:
            return "Avaliar com atenção"

        return "Não priorizar neste processo"

    # ============================================================
    # TODAS AS CRÍTICAS ATENDIDAS
    # E ALTA COBERTURA DO BLOCO ESSENCIAL
    # ============================================================

    if (
        score >= 80
        and essential_percent >= 80
    ):
        return "Recomendado para entrevista"

    # ============================================================
    # PERFIL INTERMEDIÁRIO
    # ============================================================

    if score >= 60:
        return "Avaliar com atenção"

    # ============================================================
    # BAIXA PRIORIDADE PARA ESTA VAGA
    # ============================================================

    return "Não priorizar neste processo"