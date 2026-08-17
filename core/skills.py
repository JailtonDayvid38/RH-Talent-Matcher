import re
import unicodedata


# ============================================================
# CATÁLOGO DE COMPETÊNCIAS
# Cada competência possui formas alternativas de identificação.
# ============================================================

SKILL_ALIASES = {
    "Departamento Pessoal": [
        "departamento pessoal",
        "dp",
        "administracao de pessoal",
        "administração de pessoal",
        "rotinas de pessoal",
        "setor pessoal",
    ],

    "Folha de Pagamento": [
        "folha de pagamento",
        "folha salarial",
        "processamento de folha",
        "fechamento de folha",
        "calculo de folha",
        "cálculo de folha",
    ],

    "TOTVS RM": [
        "totvs rm",
        "rm labore",
        "rm chronus",
        "rm vitae",
        "sistema rm",
        "sistemas rm",
    ],

    "RM Labore": [
        "rm labore",
        "labore",
    ],

    "RM Chronus": [
        "rm chronus",
        "chronus",
    ],

    "RM Vitae": [
        "rm vitae",
        "vitae",
    ],

    "eSocial": [
        "esocial",
        "e-social",
        "eventos esocial",
        "eventos do esocial",
    ],

    "Legislação Trabalhista": [
        "legislacao trabalhista",
        "legislação trabalhista",
        "direito do trabalho",
        "legislacao do trabalho",
        "legislação do trabalho",
        "clt",
    ],

    "Relações Trabalhistas": [
        "relacoes trabalhistas",
        "relações trabalhistas",
        "processos trabalhistas",
        "audiencias trabalhistas",
        "audiências trabalhistas",
        "preposto",
        "sindicatos",
        "negociacao sindical",
        "negociação sindical",
    ],

    "Recrutamento e Seleção": [
        "recrutamento e selecao",
        "recrutamento e seleção",
        "recrutamento",
        "selecao",
        "seleção",
        "r&s",
        "r & s",
        "sourcing",
    ],

    "Treinamento e Desenvolvimento": [
        "treinamento e desenvolvimento",
        "treinamento",
        "desenvolvimento de pessoas",
        "t&d",
        "t & d",
        "capacitacao",
        "capacitação",
    ],

    "Gestão de Pessoas": [
        "gestao de pessoas",
        "gestão de pessoas",
        "gestao de rh",
        "gestão de rh",
        "people management",
    ],

    "Benefícios": [
        "beneficios",
        "benefícios",
        "gestao de beneficios",
        "gestão de benefícios",
    ],

    "Controle de Ponto": [
        "controle de ponto",
        "ponto eletronico",
        "ponto eletrônico",
        "tratamento de ponto",
        "jornada de trabalho",
        "apontamento",
    ],

    "Rescisão": [
        "rescisao",
        "rescisão",
        "desligamento",
        "desligamentos",
        "verbas rescisorias",
        "verbas rescisórias",
    ],

    "Férias": [
        "ferias",
        "férias",
        "calculo de ferias",
        "cálculo de férias",
        "programacao de ferias",
        "programação de férias",
    ],

    "Admissão": [
        "admissao",
        "admissão",
        "admissoes",
        "admissões",
        "processo admissional",
    ],

    "People Analytics": [
        "people analytics",
        "hr analytics",
        "analytics de rh",
        "indicadores de rh",
        "indicadores de recursos humanos",
    ],

    "Análise de Dados": [
        "analise de dados",
        "análise de dados",
        "data analysis",
        "tratamento de dados",
    ],

    "Microsoft Excel": [
        "excel",
        "microsoft excel",
        "planilhas excel",
        "planilha excel",
    ],

    "VBA": [
        "vba",
        "visual basic for applications",
        "macro excel",
        "macros excel",
    ],

    "Python": [
        "python",
    ],

    "Pandas": [
        "pandas",
    ],

    "Streamlit": [
        "streamlit",
    ],

    "SQL": [
        "sql",
        "mysql",
        "sql server",
        "postgresql",
        "oracle sql",
    ],

    "Banco de Dados": [
        "banco de dados",
        "database",
        "bases de dados",
    ],

    "Power BI": [
        "power bi",
        "powerbi",
    ],

    "Automação de Processos": [
        "automacao de processos",
        "automação de processos",
        "automatizacao de processos",
        "automatização de processos",
        "automacao de rotinas",
        "automação de rotinas",
        "automatizacao de rotinas",
        "automatização de rotinas",
        "processos automatizados",
        "scripts de automacao",
        "scripts de automação",
    ],

    "Melhoria de Processos": [
        "melhoria de processos",
        "otimizacao de processos",
        "otimização de processos",
        "process improvement",
        "melhoria continua",
        "melhoria contínua",
    ],

    "Pesquisa de Clima": [
        "pesquisa de clima",
        "clima organizacional",
        "organizational climate",
    ],

    "Avaliação de Desempenho": [
        "avaliacao de desempenho",
        "avaliação de desempenho",
        "performance evaluation",
        "gestao de desempenho",
        "gestão de desempenho",
    ],

    "Cargos e Salários": [
        "cargos e salarios",
        "cargos e salários",
        "descricao de cargos",
        "descrição de cargos",
        "plano de cargos",
        "estrutura salarial",
    ],

    "Compliance Trabalhista": [
        "compliance trabalhista",
        "compliance de rh",
        "compliance em rh",
        "conformidade trabalhista",
        "auditoria trabalhista",
        "auditorias trabalhistas",
        "riscos trabalhistas",
        "passivo trabalhista",
    ],

    "Sistemas de RH": [
        "sistemas de rh",
        "sistema de rh",
        "hris",
        "sistemas de recursos humanos",
    ],

    "Tech Recruiting": [
        "tech recruiting",
        "recrutamento de ti",
        "recrutamento em tecnologia",
        "recrutamento tecnico",
        "recrutamento técnico",
    ],
}


# ============================================================
# REGRAS DE COMPETÊNCIAS RELACIONADAS
# Só usamos relações com significado forte e rastreável.
# ============================================================

RELATED_SKILL_RULES = {
    "Compliance Trabalhista": {
        "all_of": [
            "Legislação Trabalhista",
            "Relações Trabalhistas",
        ]
    },

    "Sistemas de RH": {
        "any_of": [
            "TOTVS RM",
            "RM Labore",
            "RM Chronus",
            "RM Vitae",
        ]
    },
}


def normalize_text(text: str) -> str:
    """
    Normaliza texto para facilitar comparação:
    - converte para minúsculas
    - remove acentos
    - normaliza espaços
    """

    if not text:
        return ""

    text = str(text).lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_term(
    normalized_text: str,
    term: str,
) -> bool:
    """
    Procura uma expressão já normalizada no texto.

    Para termos curtos, usa limites de palavra.
    Para expressões maiores, também usa limites nas extremidades,
    reduzindo falsos positivos por trecho interno de palavra.
    """

    term_normalized = normalize_text(term)

    if not term_normalized:
        return False

    pattern = (
        rf"(?<!\w)"
        rf"{re.escape(term_normalized)}"
        rf"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            normalized_text,
        )
    )


def detect_skills(text: str) -> dict:
    """
    Detecta competências existentes em um texto.

    Retorna competências, evidências diretas e inferências
    de competências relacionadas.
    """

    normalized_text = normalize_text(text)

    detected = []
    evidences = {}

    # 1. Evidências diretas
    for skill, aliases in SKILL_ALIASES.items():
        matched_aliases = []

        for alias in aliases:
            if contains_term(normalized_text, alias):
                alias_normalized = normalize_text(alias)

                if alias_normalized not in matched_aliases:
                    matched_aliases.append(alias_normalized)

        if matched_aliases:
            detected.append(skill)
            evidences[skill] = matched_aliases

    # 2. Inferências relacionadas controladas
    detected_set = set(detected)

    for related_skill, rule in RELATED_SKILL_RULES.items():
        if related_skill in detected_set:
            continue

        all_of = rule.get("all_of", [])
        any_of = rule.get("any_of", [])

        all_condition = (
            bool(all_of)
            and all(skill in detected_set for skill in all_of)
        )

        any_condition = (
            bool(any_of)
            and any(skill in detected_set for skill in any_of)
        )

        if all_condition or any_condition:
            detected.append(related_skill)
            detected_set.add(related_skill)

            source_skills = (
                all_of
                if all_condition
                else [
                    skill
                    for skill in any_of
                    if skill in detected_set
                ]
            )

            evidences[related_skill] = [
                "inferida a partir de: "
                + ", ".join(source_skills)
            ]

    return {
        "competencias": detected,
        "evidencias": evidences,
    }


def get_skill_catalog() -> list:
    """
    Retorna a lista de competências disponíveis na interface.
    """

    return sorted(SKILL_ALIASES.keys())
