import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extrai texto de um currículo em PDF recebido pelo Streamlit.

    Se o PDF não contiver texto extraível, gera uma mensagem clara
    em vez de retornar uma análise vazia.
    """

    if uploaded_file is None:
        return ""

    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()

        reader = PdfReader(BytesIO(file_bytes))

        pages_text = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages_text.append(text)

        result = "\n".join(pages_text).strip()

        if not result:
            raise ValueError(
                "o PDF não possui texto extraível. "
                "Ele pode ser uma imagem digitalizada."
            )

        return result

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            f"Não foi possível ler o currículo em PDF: {exc}"
        ) from exc


def _name_from_file(file_name: str | None) -> str:
    """
    Usa o nome do arquivo como fallback quando o nome do candidato
    não é identificado no conteúdo.
    """

    if not file_name:
        return "Candidato não identificado"

    stem = Path(file_name).stem

    stem = re.sub(r"^\s*\d+\s*[_\-.\s]*", "", stem)
    stem = re.sub(
        r"\b(curriculo|currículo|cv|resume)\b",
        " ",
        stem,
        flags=re.IGNORECASE,
    )

    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()

    if not stem:
        return "Candidato não identificado"

    return stem.title()[:80]


def extract_candidate_name(
    text: str,
    file_name: str | None = None,
) -> str:
    """
    Tenta identificar o nome do candidato pelas primeiras linhas.

    Evita títulos, contatos, endereços, URLs e linhas com muitos números.
    Se não conseguir, utiliza o nome do arquivo como fallback.
    """

    if not text:
        return _name_from_file(file_name)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return _name_from_file(file_name)

    ignored_terms = {
        "curriculo",
        "currículo",
        "curriculum vitae",
        "curriculum",
        "cv",
        "perfil profissional",
        "resumo profissional",
        "dados pessoais",
        "experiencia profissional",
        "experiência profissional",
        "formacao academica",
        "formação acadêmica",
        "objetivo profissional",
        "competencias",
        "competências",
    }

    blocked_fragments = {
        "linkedin",
        "email",
        "e-mail",
        "telefone",
        "celular",
        "whatsapp",
        "endereco",
        "endereço",
        "nascimento",
        "brasil",
    }

    for line in lines[:15]:
        normalized_line = line.lower().strip()

        if normalized_line in ignored_terms:
            continue

        if any(
            fragment in normalized_line
            for fragment in blocked_fragments
        ):
            continue

        if "@" in line or "http://" in normalized_line or "https://" in normalized_line:
            continue

        if re.search(r"\d{4,}", line):
            continue

        if ":" in line and len(line.split()) <= 6:
            continue

        number_of_words = len(line.split())

        if not (2 <= number_of_words <= 6):
            continue

        if len(line) > 80:
            continue

        # Nomes normalmente não contêm muitos símbolos
        symbol_count = len(
            re.findall(r"[^\wÀ-ÿ\s.'-]", line)
        )

        if symbol_count > 1:
            continue

        return line

    return _name_from_file(file_name)
