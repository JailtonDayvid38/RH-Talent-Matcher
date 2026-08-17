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
    ],

    "Legislação Trabalhista": [
        "legislacao trabalhista",
        "legislação trabalhista",
        "direito do trabalho",
        "legislacao do trabalho",
        "legislação do trabalho",
    ],

    "Relações Trabalhistas": [
        "relacoes trabalhistas",
        "relações trabalhistas",
        "processos trabalhistas",
        "audiencias trabalhistas",
        "audiências trabalhistas",
        "preposto",
    ],

    "Recrutamento e Seleção": [
        "recrutamento e selecao",
        "recrutamento e seleção",
        "recrutamento",
        "selecao",
        "seleção",
        "r&s",
        "r & s",
    ],

    "Treinamento e Desenvolvimento": [
        "treinamento e desenvolvimento",
        "treinamento",
        "desenvolvimento de pessoas",
        "t&d",
        "t & d",
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
        "automatizacao",
        "automatização",
        "automacao",
        "automação",
    ],

    "Melhoria de Processos": [
        "melhoria de processos",
        "otimizacao de processos",
        "otimização de processos",
        "process improvement",
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
    ],

    "Cargos e Salários": [
        "cargos e salarios",
        "cargos e salários",
        "descricao de cargos",
        "descrição de cargos",
        "plano de cargos",
    ],

    "Compliance Trabalhista": [
        "compliance trabalhista",
        "compliance de rh",
        "compliance em rh",
        "conformidade trabalhista",
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
        char for char in text
        if not unicodedata.combining(char)
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_term(text: str, term: str) -> bool:
    """
    Procura uma expressão no texto tentando evitar
    falsos positivos em palavras muito curtas.
    """

    text_normalized = normalize_text(text)
    term_normalized = normalize_text(term)

    if len(term_normalized) <= 3:
        pattern = rf"(?<!\w){re.escape(term_normalized)}(?!\w)"
        return bool(re.search(pattern, text_normalized))

    return term_normalized in text_normalized


def detect_skills(text: str) -> dict:
    """
    Detecta competências existentes em um texto.

    Retorna:
    {
        "competencias": [...],
        "evidencias": {
            "TOTVS RM": ["rm labore"],
            ...
        }
    }
    """

    detected = []
    evidences = {}

    for skill, aliases in SKILL_ALIASES.items():

        matched_aliases = []

        for alias in aliases:
            if contains_term(text, alias):
                matched_aliases.append(alias)

        if matched_aliases:
            detected.append(skill)
            evidences[skill] = matched_aliases

    return {
        "competencias": detected,
        "evidencias": evidences,
    }


def get_skill_catalog() -> list:
    """
    Retorna lista de competências disponíveis
    para utilização na interface da vaga.
    """

    return sorted(SKILL_ALIASES.keys())