from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extrai o texto de um currículo em PDF recebido
    através do Streamlit.
    """

    if uploaded_file is None:
        return ""

    try:
        # Garante que a leitura comece do início
        uploaded_file.seek(0)

        file_bytes = uploaded_file.read()

        reader = PdfReader(BytesIO(file_bytes))

        pages_text = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages_text.append(text)

        return "\n".join(pages_text).strip()

    except Exception as exc:
        raise ValueError(
            f"Não foi possível ler o currículo em PDF: {exc}"
        ) from exc


def extract_candidate_name(text: str) -> str:
    """
    Tenta identificar o nome do candidato pelas primeiras
    linhas do currículo.
    """

    if not text:
        return "Candidato não identificado"

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "Candidato não identificado"

    ignored_terms = {
        "curriculo",
        "currículo",
        "curriculum vitae",
        "curriculum",
        "cv",
        "perfil profissional",
        "resumo profissional",
        "dados pessoais",
    }

    for line in lines[:10]:

        normalized_line = line.lower().strip()

        if normalized_line in ignored_terms:
            continue

        number_of_words = len(line.split())

        # Um nome costuma ter entre 2 e 6 palavras
        if 2 <= number_of_words <= 6 and len(line) <= 80:
            return line

    return lines[0][:80]