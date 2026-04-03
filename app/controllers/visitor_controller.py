# =====================================================================
# visitor_controller.py
# Controller de Visitantes — SISPORT V1.1
# Gerencia wizard (3 etapas), busca por CPF, foto, check-in/check-out.
# =====================================================================

# ─────────────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────────────
from datetime import datetime
from flask import session
from ..extensions import db
from ..models.visitor import Visitor, Visit
from ..services.photo_service import save_or_replace_profile_photo
from ..utils.validators import normalize_cpf, is_valid_cpf, validate_required_email
from sqlalchemy import or_


# ── Categorias válidas ───────────────────────────────────────────────
VALID_CATEGORIES = ("civil", "militar", "ex-militar")


# =====================================================================
# Funções — Busca de Visitante
# =====================================================================

def find_visitor_by_cpf(cpf: str):
    """
    Busca visitante cadastrado pelo CPF.

    :param cpf: (str) CPF do visitante (com ou sem formatação).
    :return: Instância de Visitor se encontrado, ou None.
    """
    cpf = (cpf or "").strip()
    return db.session.query(Visitor).filter(Visitor.cpf == cpf).one_or_none()


# =====================================================================
# Funções — Wizard de Cadastro (Etapas 1, 2 e finalização)
# =====================================================================

def wizard_start_for_new_visitor(cpf: str = ""):
    """
    Inicializa a sessão do wizard para um novo cadastro de visitante.
    Define os campos padrão e posiciona na etapa 1.

    :param cpf: (str) CPF pré-preenchido (opcional).
    :return: None — os dados são gravados em session["wizard"].
    """
    session["wizard"] = {
        "mode": "new",
        "step": 1,
        "name": "",
        "cpf": (cpf or "").strip(),
        "phone": "",
        "email": None,
        "empresa": "",
        "father_name": "",
        "mom_name": "",
        "category": "civil",          # ← NOVO
        "photo_rel_path": "",
    }


def _check_duplicate_fields(name: str, father_name: str, mom_name: str,
                            cpf: str, phone: str, email: str | None,
                            exclude_id: int | None = None):
    """
    Verifica se algum dos campos informados já pertence a um visitante
    cadastrado no banco de dados. Se encontrar duplicidade, levanta
    ValueError com a lista detalhada de conflitos.

    :param name:        (str) Nome completo.
    :param father_name: (str) Nome do pai.
    :param mom_name:    (str) Nome da mãe.
    :param cpf:         (str) CPF normalizado.
    :param phone:       (str) Telefone.
    :param email:       (str | None) E-mail (pode ser None).
    :param exclude_id:  (int | None) ID do visitante a ignorar (para edição).
    :raises ValueError: Se qualquer campo já estiver em uso por outro visitante.
    """
    filters = [
        Visitor.cpf == cpf,
        Visitor.name == name,
        Visitor.mom_name == mom_name,
        Visitor.phone == phone,
    ]

    if father_name:
        filters.append(Visitor.father_name == father_name)

    if email:
        filters.append(Visitor.email == email)

    query = db.session.query(Visitor).filter(or_(*filters))

    if exclude_id is not None:
        query = query.filter(Visitor.id != exclude_id)

    matches = query.all()

    if not matches:
        return

    conflicts = []

    for visitor in matches:
        visitor_label = f"{visitor.name} (CPF: {visitor.cpf})"

        if visitor.cpf == cpf:
            conflicts.append(f"• CPF já cadastrado por: {visitor_label}")
        if visitor.name == name:
            conflicts.append(f"• Nome completo já cadastrado por: {visitor_label}")
        if visitor.mom_name == mom_name:
            conflicts.append(f"• Nome da mãe já cadastrado por: {visitor_label}")
        if visitor.phone == phone:
            conflicts.append(f"• Telefone já cadastrado por: {visitor_label}")
        if father_name and visitor.father_name == father_name:
            conflicts.append(f"• Nome do pai já cadastrado por: {visitor_label}")
        if email and visitor.email == email:
            conflicts.append(f"• E-mail já cadastrado por: {visitor_label}")

    detail = "\n".join(conflicts)
    raise ValueError(
        f"Dados já em uso por visitante(s) cadastrado(s):\n{detail}\n"
        f"Utilize a busca por CPF para localizar o registro existente."
    )


def wizard_step1_submit(name: str, father_name: str, mom_name: str,
                        cpf: str, phone: str, email: str, empresa: str,
                        category: str = "civil"):
    """
    Processa e valida os dados da Etapa 1 do wizard (dados pessoais).
    Normaliza campos, valida CPF, verifica duplicidade e avança para etapa 2.

    :param name:        (str) Nome completo do visitante.
    :param father_name: (str) Nome do pai (opcional).
    :param mom_name:    (str) Nome da mãe (obrigatório).
    :param cpf:         (str) CPF do visitante.
    :param phone:       (str) Telefone/celular (obrigatório).
    :param email:       (str) E-mail (opcional).
    :param empresa:     (str) Empresa do visitante (opcional).
    :param category:    (str) Categoria: civil, militar ou ex-militar.
    :return: None — atualiza session["wizard"] e avança step para 2.
    :raises ValueError: Se dados forem inválidos ou já existirem no banco.
    """
    w = session.get("wizard") or {}

    # ── Normalização ──────────────────────────────────────────────
    name = (name or "").strip().upper()
    father_name = (father_name or "").strip().upper()
    mom_name = (mom_name or "").strip().upper()
    empresa = (empresa or "").strip().upper()
    category = (category or "civil").strip().lower()

    cpf = normalize_cpf(cpf or "")
    if not is_valid_cpf(cpf):
        raise ValueError("CPF inválido. Verifique e tente novamente.")

    phone = (phone or "").strip()
    if not phone:
        raise ValueError("Telefone/Celular é obrigatório.")

    email = (email or "").strip()
    if email:
        email = validate_required_email(email).lower()
    else:
        email = None

    if not name:
        raise ValueError("Nome completo é obrigatório.")
    if not mom_name:
        raise ValueError("Nome da mãe é obrigatório.")

    # ── Validar categoria ─────────────────────────────────────────
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Categoria inválida: '{category}'. Use: {', '.join(VALID_CATEGORIES)}.")

    # ── Verificação de duplicidade no banco ───────────────────────
    _check_duplicate_fields(
        name=name,
        father_name=father_name,
        mom_name=mom_name,
        cpf=cpf,
        phone=phone,
        email=email,
    )

    # ── Atualiza sessão e avança para etapa 2 ────────────────────
    w.update({
        "name": name,
        "father_name": father_name,
        "mom_name": mom_name,
        "cpf": cpf,
        "phone": phone,
        "email": email,
        "empresa": empresa,
        "category": category,          # ← NOVO
        "step": 2,
    })
    session["wizard"] = w


def wizard_step2_submit(photo_data_url: str | None):
    """
    Processa a Etapa 2 do wizard: salva a foto de perfil (opcional)
    e avança para a etapa 3.

    :param photo_data_url: (str | None) Foto em formato data URL (base64).
    :return: None — atualiza session["wizard"] com photo_rel_path e avança step para 3.
    :raises ValueError: Se o CPF não estiver presente na sessão do wizard.
    """
    w = session.get("wizard") or {}
    cpf = (w.get("cpf") or "").strip()
    if not cpf:
        raise ValueError("CPF não informado. Volte à etapa 1.")

    photo_data_url = (photo_data_url or "").strip()
    photo_rel_path = None
    if photo_data_url:
        photo_rel_path = save_or_replace_profile_photo(photo_data_url, cpf)

    w.update({"photo_rel_path": photo_rel_path, "step": 3})
    session["wizard"] = w


def create_visitor_if_not_exists_from_wizard() -> Visitor:
    """
    Finaliza o wizard: cria o visitante no banco de dados a partir dos
    dados armazenados na sessão. Se já existir um visitante com o mesmo
    CPF, retorna o registro existente sem duplicar.

    :return: (Visitor) Instância do visitante criado ou já existente.
    :raises ValueError: Se dados obrigatórios estiverem ausentes na sessão.
    """
    w = session.get("wizard") or {}
    name = (w.get("name") or "").strip()
    father_name = (w.get("father_name") or "").strip()
    mom_name = (w.get("mom_name") or "").strip()
    cpf = (w.get("cpf") or "").strip()
    phone = (w.get("phone") or "").strip()
    email = w.get("email") or None
    empresa = (w.get("empresa") or "").strip()
    category = (w.get("category") or "civil").strip()    # ← NOVO
    photo_rel_path = w.get("photo_rel_path") or None

    if not name or not cpf or not phone or not mom_name:
        raise ValueError("Cadastro incompleto (nome, cpf, telefone e nome da mãe).")

    existing = find_visitor_by_cpf(cpf)
    if existing:
        return existing

    visitor = Visitor(
        name=name,
        cpf=cpf,
        phone=phone,
        photo_rel_path=photo_rel_path,
        email=email,
        empresa=empresa,
        father_name=father_name,
        mom_name=mom_name,
        category=category,                                # ← NOVO
    )
    db.session.add(visitor)
    db.session.commit()
    return visitor


# =====================================================================
# Funções — Foto de Visitante
# =====================================================================

def visitor_photo_update(visitor: Visitor, photo_data_url: str):
    """
    Atualiza a foto de perfil de um visitante já cadastrado.

    :param visitor:        (Visitor) Instância do visitante a ser atualizado.
    :param photo_data_url: (str) Foto em formato data URL (base64).
    :return: None — atualiza visitor.photo_rel_path e persiste no banco.
    :raises ValueError: Se o visitante não possuir CPF vinculado.
    """
    if not visitor.cpf:
        raise ValueError("Visitante sem CPF não pode ter foto vinculada.")
    photo_rel_path = save_or_replace_profile_photo(photo_data_url, visitor.cpf)
    visitor.photo_rel_path = photo_rel_path
    db.session.commit()


# =====================================================================
# Funções — Check-in / Check-out de Visitas
# =====================================================================

def register_checkin(visitor: Visitor, destination: str) -> int:
    """
    Registra uma nova entrada (check-in) para um visitante já cadastrado.

    :param visitor:     (Visitor) Instância do visitante.
    :param destination: (str) Local/destino da visita (obrigatório).
    :return: (int) ID da visita recém-criada.
    :raises ValueError: Se o destino não for informado.
    """
    destination = (destination or "").strip()
    if not destination:
        raise ValueError("Informe o local/destino da visita.")

    visit = Visit(visitor_id=visitor.id, destination=destination, check_in=datetime.now())
    db.session.add(visit)
    db.session.commit()
    return visit.id


def checkout_visit(visit_id: int):
    """
    Registra a saída (check-out) de uma visita em aberto.

    :param visit_id: (int) ID da visita a ser encerrada.
    :return: (Visit) Instância da visita atualizada.
    :raises ValueError: Se a visita não for encontrada no banco.
    """
    visit = db.session.get(Visit, visit_id)
    if not visit:
        raise ValueError("Visita não encontrada.")
    if visit.check_out is None:
        visit.check_out = datetime.now()
        visit.visitor.last_checkout_at = visit.check_out
        db.session.commit()
    return visit
