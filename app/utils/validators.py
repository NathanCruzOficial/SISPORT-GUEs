import re
import unicodedata

'''
VALIDAÇÃO DE CPF E TELEFONE
'''

def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")

def normalize_cpf(value: str) -> str:
    """Retorna CPF apenas com dígitos. Ex: '123.456.789-09' -> '12345678909'."""
    return re.sub(r"\D", "", value or "")

def is_valid_cpf(value: str) -> bool:
    cpf = normalize_cpf(value)

    # Precisa ter 11 dígitos
    if len(cpf) != 11:
        return False

    # Rejeita CPFs com todos os dígitos iguais (000..., 111..., etc.)
    if cpf == cpf[0] * 11:
        return False

    # Cálculo do 1º dígito verificador
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = (sum1 * 10) % 11
    d1 = 0 if d1 == 10 else d1

    # Cálculo do 2º dígito verificador
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = (sum2 * 10) % 11
    d2 = 0 if d2 == 10 else d2

    return cpf[-2:] == f"{d1}{d2}"


'''
VALIDAÇÃO DE EMAIL
'''


_EMAIL_RE = re.compile(
    r"^(?=.{1,254}$)"                    # tamanho total
    r"(?=.{1,64}@)"                      # local-part <= 64
    r"[A-Za-z0-9]"                       # começa com alfanum
    r"(?:[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{0,62}[A-Za-z0-9])?"
    r"@"
    r"(?!-)"                             # domínio não começa com hífen
    r"[A-Za-z0-9-]{1,63}"
    r"(?:\.[A-Za-z0-9-]{1,63})+$"        # exige ao menos um ponto
    r"$"
)

def normalize_email(raw: str) -> str:
    """Normaliza e-mail para validação/armazenamento."""
    if raw is None:
        return ""
    s = str(raw).strip()
    s = unicodedata.normalize("NFKC", s)
    return s.lower()

def is_valid_email(raw: str) -> bool:
    """Validação prática e robusta para e-mails comuns."""
    email = normalize_email(raw)
    if not email:
        return False

    if any(ch.isspace() for ch in email):
        return False
    if ".." in email:
        return False
    if email.startswith(".") or email.endswith("."):
        return False

    if not _EMAIL_RE.match(email):
        return False

    local, domain = email.rsplit("@", 1)
    if domain.startswith(".") or domain.endswith("."):
        return False
    if domain.startswith("-") or domain.endswith("-"):
        return False

    return True

def validate_required_email(raw: str) -> str:
    """
    Campo obrigatório:
    - retorna o e-mail normalizado
    - levanta ValueError com mensagem amigável se vazio/inválido
    """
    email = normalize_email(raw)
    if email == "":
        raise ValueError("E-mail é obrigatório.")
    if not is_valid_email(email):
        raise ValueError("E-mail inválido. Verifique e tente novamente.")
    return email

