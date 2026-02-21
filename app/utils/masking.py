import re

# partículas comuns que você pode querer ignorar nas iniciais
_SKIP_TOKENS = {"da", "de", "do", "das", "dos", "e"}

def mask_name_first_plus_initials(value: str | None, *, uppercase: bool = True) -> str:
    """
    "NATHAN DA CRUZ CARDOSO" -> "NATHAN D. C. C."
    Mantém primeiro token completo e transforma os demais em iniciais.
    Nunca retorna None (bom p/ colunas NOT NULL).
    """
    if not value:
        return ""

    # normaliza espaços
    raw = " ".join(value.strip().split())
    if not raw:
        return ""

    parts = raw.split(" ")
    first = parts[0]
    rest = parts[1:]

    initials = []
    for p in rest:
        token = p.strip().strip(".")
        if not token:
            continue

        # se quiser ignorar "da/de/do/das/dos/e", comente este bloco
        if token.lower() in _SKIP_TOKENS:
            continue

        initials.append(token[0] + ".")

    result = first
    if initials:
        result += " " + " ".join(initials)

    return result.upper() if uppercase else result


def mask_mom_name_keep_first(value: str | None, *, uppercase: bool = True) -> str:
    """
    Nome da mãe: só o primeiro nome (sem apagar, sem NULL).
    Ex: "Maria de Souza" -> "MARIA"
    """
    if not value:
        return ""
    parts = [p for p in value.strip().split() if p]
    if not parts:
        return ""
    res = parts[0]
    return res.upper() if uppercase else res


def mask_phone_last4(value: str | None) -> str:
    """
    "(21) 99876-1234" -> "(**) *****-1234"
    Mantém só os últimos 4 dígitos.
    """
    if not value:
        return ""
    digits = re.sub(r"\D+", "", value)
    if len(digits) < 4:
        return "*" * len(digits)
    return f"(**) *****-{digits[-4:]}"


def mask_email_2first_2last_before_at(value: str | None) -> str:
    """
    "joaosilva@gmail.com" -> "jo**va@gmail.com"
    """
    if not value or "@" not in value:
        return ""
    local, domain = value.split("@", 1)
    local = local.strip()
    domain = domain.strip()
    if not local or not domain:
        return ""

    if len(local) <= 2:
        masked_local = local[:1] + "*"
    elif len(local) == 3:
        masked_local = local[:2] + "*"
    else:
        masked_local = f"{local[:2]}**{local[-2:]}"
    return f"{masked_local}@{domain}"
