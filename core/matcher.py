from core.skills import detect_skills


def calculate_match(
    curriculum_text: str,
    required_skills: list,
    desired_skills: list,
    required_weight: float = 0.70,
    desired_weight: float = 0.30,
) -> dict:
    """
    Calcula a aderência de um currículo a uma vaga com base
    em competências obrigatórias e desejáveis.
    """

    analysis = detect_skills(curriculum_text)

    detected_skills = set(analysis["competencias"])

    required_skills = list(required_skills or [])
    desired_skills = list(desired_skills or [])

    # Competências obrigatórias
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

    # Competências desejáveis
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

    # Percentuais
    if required_skills:
        required_score = len(found_required) / len(required_skills)
    else:
        required_score = 1.0

    if desired_skills:
        desired_score = len(found_desired) / len(desired_skills)
    else:
        desired_score = 1.0

    # Nota final
    total_score = (
        required_score * required_weight
        + desired_score * desired_weight
    ) * 100

    return {
        "aderencia": round(total_score, 1),
        "percentual_obrigatorias": round(required_score * 100, 1),
        "percentual_desejaveis": round(desired_score * 100, 1),

        "obrigatorias_encontradas": found_required,
        "obrigatorias_ausentes": missing_required,

        "desejaveis_encontradas": found_desired,
        "desejaveis_ausentes": missing_desired,

        "competencias_detectadas": analysis["competencias"],
        "evidencias": analysis["evidencias"],
    }


def classify_match(score: float) -> str:
    """
    Classifica o nível de aderência do currículo à vaga.
    """

    if score >= 85:
        return "Alta aderência"

    if score >= 70:
        return "Boa aderência"

    if score >= 50:
        return "Aderência moderada"

    return "Baixa aderência"