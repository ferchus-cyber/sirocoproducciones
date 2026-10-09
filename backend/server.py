from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, UploadFile, File, Response
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import requests
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import json
import bcrypt
import jwt

from emergentintegrations.llm.chat import LlmChat, UserMessage

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# ---------------- Object Storage ----------------
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
APP_NAME = "siroco"
storage_key = None
MIME_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
              "gif": "image/gif", "webp": "image/webp"}

def init_storage(force: bool = False):
    global storage_key
    if storage_key and not force:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_LLM_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                        headers={"X-Storage-Key": key, "Content-Type": content_type},
                        data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple:
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 404:
        init_storage(force=True)
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": storage_key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

app = FastAPI()
api_router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

# ---------------- Auth helpers ----------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email,
               "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"email": payload.get("email")})
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")

# ---------------- Models ----------------
class LoginInput(BaseModel):
    email: EmailStr
    password: str

class ContactInput(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class NotifyInput(BaseModel):
    email: EmailStr

class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = "Admin"

# ---------------- Seed content ----------------
DEFAULT_CONTENT = {
    "_id": "site",
    "hero": {
        "tagline": "Producción artística y espectáculos musicales",
        "subtitle": "Convertimos cada evento en una experiencia única. Producción, organización y gestión de conciertos y eventos culturales.",
        "cta_primary": "Solicita información",
        "cta_secondary": "Descubre nuestros eventos",
    },
    "about": {
        "title": "Quiénes Somos",
        "heading": "Más de 30 años dedicados a la música y al espectáculo",
        "paragraphs": [
            "Siroco Producciones nace de una trayectoria de más de tres décadas vinculada al mundo de la música, los espectáculos en directo y la gestión artística.",
            "Durante más de 30 años hemos trabajado junto a artistas, músicos, técnicos, promotores y administraciones públicas, participando en la organización y desarrollo de eventos de muy diversa naturaleza.",
            "Entendemos que detrás de cada evento existe una gran responsabilidad. Por ello, trabajamos con rigor, transparencia y atención al detalle, garantizando una gestión eficiente desde la planificación inicial hasta la finalización del espectáculo.",
        ],
        "pillars": ["Profesionalidad", "Compromiso", "Seriedad"],
    },
    "origin": {
        "title": "El Nombre Siroco",
        "paragraphs": [
            "El nombre 'Siroco' hace referencia al viento mediterráneo que llega desde el Sahara y atraviesa el Mediterráneo, recorriendo largas distancias y transformando todo aquello que encuentra a su paso. Es un símbolo de fuerza, movimiento, energía y conexión entre culturas.",
            "Precisamente esos valores son los que definen nuestra forma de entender la música y los espectáculos: la capacidad de emocionar, de unir a las personas y de dejar una huella imborrable en cada escenario y en cada público.",
            "Pero nuestro nombre también encierra un significado muy especial y personal. Siroco es un sentido homenaje al maestro Paco de Lucía y a su obra maestra Siroco, considerada una de las grabaciones más influyentes y admiradas de la historia de la música española y del flamenco contemporáneo.",
            "Elegimos este nombre porque refleja nuestra identidad: la fuerza de un viento capaz de recorrer caminos y la inspiración de un artista que cambió para siempre la historia de la música.",
        ],
        "album_caption": "Siroco - Paco de Lucía",
    },
    "services": [
        {"title": "Producción de Conciertos", "description": "Organización integral de conciertos musicales para ciclos culturales, festivales, homenajes y eventos especiales.", "items": ["Contratación artística", "Coordinación técnica", "Producción ejecutiva", "Gestión de permisos", "Supervisión del evento"]},
        {"title": "Programación Cultural para Ayuntamientos", "description": "Diseñamos programaciones musicales adaptadas a las necesidades de cada municipio.", "items": ["Ferias y fiestas", "Verano cultural", "Navidad", "Carnaval", "Eventos institucionales", "Jornadas culturales"]},
        {"title": "Producción Técnica", "description": "Coordinamos todos los recursos técnicos necesarios para el desarrollo del espectáculo.", "items": ["Sonido profesional", "Iluminación", "Escenarios", "Pantallas LED", "Generadores eléctricos", "Personal técnico especializado"]},
    ],
    "contact": {
        "title": "Contacto",
        "heading": "Solicita información sin compromiso",
        "subtitle": "Descubre cómo podemos dar vida a tu próximo evento.",
        "phone": "+34 679 360 643",
        "email": "Sirocoproducciones@hotmail.com",
        "location": "San Fernando (Cádiz), Andalucía, España",
    },
    "ui": {
        "nav_events": "Eventos",
        "nav_services": "Servicios",
        "nav_about": "Quiénes Somos",
        "nav_origin": "Origen",
        "nav_contact": "Contacto",
        "form_name": "Nombre",
        "form_email": "Email",
        "form_subject": "Asunto",
        "form_message": "Mensaje",
        "form_send": "Enviar mensaje",
        "form_success": "Mensaje enviado. Gracias por contactar con Siroco Producciones.",
        "form_error": "Ocurrió un error. Inténtalo de nuevo.",
        "services_title": "Servicios",
        "footer_rights": "Todos los derechos reservados",
    },
}

SUPPORTED_LANGS = {"es", "en", "de", "fr"}
LANG_NAMES = {"en": "English", "de": "German (Deutsch)", "fr": "French (Francais)"}

async def get_site_doc() -> dict:
    doc = await db.site_content.find_one({"_id": "site"})
    if not doc:
        await db.site_content.insert_one(DEFAULT_CONTENT)
        doc = await db.site_content.find_one({"_id": "site"})
    doc = dict(doc)
    doc.pop("_id", None)
    return doc

# ---------------- Translation ----------------
def _cache_key(lang: str, s: str) -> str:
    return hashlib.sha256(f"{lang}:{s}".encode()).hexdigest()

def _collect_strings(obj, acc):
    if isinstance(obj, str):
        if obj.strip():
            acc.append(obj)
    elif isinstance(obj, list):
        for it in obj:
            _collect_strings(it, acc)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("image", "id", "phone", "email"):
                continue
            _collect_strings(v, acc)

def _apply_translations(obj, mapping):
    if isinstance(obj, str):
        return mapping.get(obj, obj)
    if isinstance(obj, list):
        return [_apply_translations(it, mapping) for it in obj]
    if isinstance(obj, dict):
        return {k: (v if k in ("image", "id", "phone", "email") else _apply_translations(v, mapping)) for k, v in obj.items()}
    return obj

async def translate_strings(strings: List[str], lang: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    unique = list(dict.fromkeys([s for s in strings if s and s.strip()]))
    key_to_src = {_cache_key(lang, s): s for s in unique}
    cached = await db.translations.find({"_id": {"$in": list(key_to_src.keys())}}).to_list(len(key_to_src) + 1)
    cached_ids = set()
    for doc in cached:
        mapping[key_to_src[doc["_id"]]] = doc["text"]
        cached_ids.add(doc["_id"])
    to_translate = [key_to_src[k] for k in key_to_src if k not in cached_ids]

    if to_translate and EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"translate-{lang}",
                           system_message=f"You are a professional translator. Translate the given Spanish strings into {LANG_NAMES.get(lang, lang)}. Keep proper names of artists and 'Siroco Producciones', 'Paco de Lucia' unchanged. Return ONLY a JSON array of translated strings in the exact same order and SAME LENGTH as the input, no extra text.").with_model("gemini", "gemini-3-flash-preview")
            payload = json.dumps(to_translate, ensure_ascii=False)
            resp = await chat.send_message(UserMessage(text=f"Translate these strings (JSON array): {payload}"))
            txt = resp.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1]
                if txt.startswith("json"):
                    txt = txt[4:]
            translated = json.loads(txt)
            for src, tr in zip(to_translate, translated):
                if not isinstance(tr, str) or not tr.strip():
                    continue
                mapping[src] = tr
                await db.translations.update_one({"_id": _cache_key(lang, src)}, {"$set": {"text": tr, "lang": lang}}, upsert=True)
            # any string not translated (length mismatch) falls back to original
            for src in to_translate:
                mapping.setdefault(src, src)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            for s in to_translate:
                mapping[s] = s
    else:
        for s in to_translate:
            mapping.setdefault(s, s)
    return mapping

# ---------------- Public endpoints ----------------
@api_router.get("/")
async def root():
    return {"message": "Siroco Producciones API"}

@api_router.get("/site")
async def get_site(lang: str = "es"):
    lang = lang if lang in SUPPORTED_LANGS else "es"
    doc = await get_site_doc()
    if lang == "es":
        return doc
    strings = []
    _collect_strings(doc, strings)
    mapping = await translate_strings(strings, lang)
    return _apply_translations(doc, mapping)

@api_router.post("/contact")
async def create_contact(input: ContactInput):
    doc = input.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["read"] = False
    await db.contact_messages.insert_one(doc)
    return {"success": True, "id": doc["id"]}

@api_router.post("/notify")
async def create_notify(input: NotifyInput):
    email = input.email.lower()
    await db.notify_subscribers.update_one(
        {"email": email},
        {"$set": {"email": email}, "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"success": True}

@api_router.get("/gallery")
async def get_gallery():
    items = await db.event_gallery.find({"is_deleted": False}, {"_id": 0}).sort("order", 1).to_list(200)
    return [{"id": it["id"], "url": f"/api/files/{it['storage_path']}", "caption": it.get("caption", "")} for it in items]

@api_router.get("/files/{path:path}")
async def download_file(path: str):
    record = await db.event_gallery.find_one({"storage_path": path, "is_deleted": False})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    data, content_type = get_object(path)
    return Response(content=data, media_type=record.get("content_type", content_type),
                    headers={"Cache-Control": "public, max-age=86400"})

# ---------------- Auth endpoints ----------------
@api_router.post("/auth/login")
async def login(input: LoginInput):
    user = await db.users.find_one({"email": input.email.lower()})
    if not user or not verify_password(input.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    token = create_access_token(str(user["_id"]), user["email"])
    return {"token": token, "user": {"email": user["email"], "name": user.get("name", "Admin"), "role": user.get("role", "admin")}}

@api_router.get("/auth/me")
async def me(current=Depends(get_current_user)):
    return {"email": current["email"], "name": current.get("name", "Admin"), "role": current.get("role", "admin")}

# ---------------- Admin endpoints ----------------
@api_router.get("/admin/content")
async def admin_content(current=Depends(get_current_user)):
    return await get_site_doc()

@api_router.put("/admin/content")
async def update_content(payload: Dict[str, Any], current=Depends(get_current_user)):
    payload.pop("_id", None)
    await db.site_content.update_one({"_id": "site"}, {"$set": payload}, upsert=True)
    await db.translations.delete_many({})
    return await get_site_doc()

@api_router.get("/admin/messages")
async def get_messages(current=Depends(get_current_user)):
    msgs = await db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return msgs

@api_router.get("/admin/subscribers")
async def get_subscribers(current=Depends(get_current_user)):
    subs = await db.notify_subscribers.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return subs

@api_router.get("/admin/admins")
async def list_admins(current=Depends(get_current_user)):
    users = await db.users.find({}, {"password_hash": 0}).sort("created_at", 1).to_list(100)
    return [{"email": u["email"], "name": u.get("name", "Admin"),
             "is_self": u["email"] == current["email"],
             "created_at": u.get("created_at")} for u in users]

@api_router.post("/admin/admins")
async def create_admin(payload: AdminCreate, current=Depends(get_current_user)):
    email = payload.email.lower().strip()
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Ya existe un administrador con ese email.")
    await db.users.insert_one({
        "email": email, "password_hash": hash_password(payload.password),
        "name": payload.name or "Admin", "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"email": email, "name": payload.name or "Admin"}

@api_router.delete("/admin/admins/{email}")
async def delete_admin(email: str, current=Depends(get_current_user)):
    email = email.lower().strip()
    if email == current["email"].lower():
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta.")
    if await db.users.count_documents({}) <= 1:
        raise HTTPException(status_code=400, detail="Debe existir al menos un administrador.")
    result = await db.users.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Administrador no encontrado.")
    return {"success": True}

@api_router.post("/admin/gallery")
async def upload_gallery(file: UploadFile = File(...), current=Depends(get_current_user)):
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
    content_type = MIME_TYPES.get(ext)
    if not content_type:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa JPG, PNG, WEBP o GIF.")
    gid = str(uuid.uuid4())
    path = f"{APP_NAME}/gallery/{gid}.{ext}"
    data = await file.read()
    result = put_object(path, data, content_type)
    count = await db.event_gallery.count_documents({})
    doc = {"id": gid, "storage_path": result["path"], "original_filename": file.filename,
           "content_type": content_type, "caption": "", "order": count,
           "is_deleted": False, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.event_gallery.insert_one(doc)
    return {"id": gid, "url": f"/api/files/{result['path']}", "caption": ""}

@api_router.get("/admin/gallery")
async def admin_gallery(current=Depends(get_current_user)):
    items = await db.event_gallery.find({"is_deleted": False}, {"_id": 0}).sort("order", 1).to_list(200)
    return [{"id": it["id"], "url": f"/api/files/{it['storage_path']}", "caption": it.get("caption", "")} for it in items]

@api_router.delete("/admin/gallery/{gid}")
async def delete_gallery(gid: str, current=Depends(get_current_user)):
    await db.event_gallery.update_one({"id": gid}, {"$set": {"is_deleted": True}})
    return {"success": True}

@api_router.delete("/admin/messages/{msg_id}")
async def delete_message(msg_id: str, current=Depends(get_current_user)):
    await db.contact_messages.delete_one({"id": msg_id})
    return {"success": True}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@app.on_event("startup")
async def startup():
    try:
        init_storage()
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
    # seed admin
    admin_email = os.environ["ADMIN_EMAIL"].lower()
    admin_password = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({"email": admin_email, "password_hash": hash_password(admin_password),
                                   "name": "Admin", "role": "admin", "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
    # seed content
    if not await db.site_content.find_one({"_id": "site"}):
        await db.site_content.insert_one(DEFAULT_CONTENT)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
