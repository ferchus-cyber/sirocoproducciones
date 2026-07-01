from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
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

class Artist(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    bio: str
    image: str
    order: int = 0

class SiteContent(BaseModel):
    hero: Dict[str, Any]
    about: Dict[str, Any]
    origin: Dict[str, Any]
    services: List[Dict[str, Any]]
    contact: Dict[str, Any]
    ui: Dict[str, Any]
    artists: List[Artist]

# ---------------- Seed content ----------------
DEFAULT_ARTISTS = [
    {"id": str(uuid.uuid4()), "name": "Farruquito", "role": "Baile Flamenco", "bio": "Heredero de la dinastia Farruco, es uno de los grandes referentes del baile flamenco puro, con un poderio y una pureza que emocionan sobre cualquier escenario.", "image": "/media/artists/farruquito.webp", "order": 1},
    {"id": str(uuid.uuid4()), "name": "Duquende", "role": "Cante Flamenco", "bio": "Voz esencial del flamenco contemporaneo. Colaborador de Paco de Lucia, su cante hondo y personal lo ha convertido en una figura imprescindible.", "image": "/media/artists/duquende.jpeg", "order": 2},
    {"id": str(uuid.uuid4()), "name": "Montse Cortes", "role": "Cante Flamenco", "bio": "Cantaora de raza gitana y una de las grandes voces del cante actual, con un recorrido junto a los mas grandes del genero.", "image": "/media/artists/montse-cortes.jpeg", "order": 3},
    {"id": str(uuid.uuid4()), "name": "May Fernandez", "role": "Cante Flamenco", "bio": "Cantaora con arte y pureza, dueña de una gran presencia escenica y de una voz llena de sentimiento.", "image": "/media/artists/may-fernandez.jpg", "order": 4},
    {"id": str(uuid.uuid4()), "name": "La Reina Gitana", "role": "Cante y Baile", "bio": "Artista de cante y baile que derrocha fuerza y duende en cada actuacion, conectando con el publico desde el primer compas.", "image": "/media/artists/la-reina-gitana.jpg", "order": 5},
    {"id": str(uuid.uuid4()), "name": "Rubio de Pruna", "role": "Cante Flamenco", "bio": "Cantaor de hondura y tradicion, con un dominio del compas y una sensibilidad que reflejan la esencia del flamenco.", "image": "/media/artists/rubio-de-pruna.jpeg", "order": 6},
    {"id": str(uuid.uuid4()), "name": "Antonio El Farru", "role": "Baile Flamenco", "bio": "Bailaor de la saga Farruco, combina tecnica y poderio en un estilo personal heredado de una de las mayores dinastias del baile.", "image": "/media/artists/antonio-el-farru.jpg", "order": 7},
    {"id": str(uuid.uuid4()), "name": "Cristian de Moret", "role": "Cante Flamenco", "bio": "Joven cantaor y una de las promesas del flamenco contemporaneo, con una voz fresca y un profundo respeto por la tradicion.", "image": "/media/artists/cristian-de-moret.jpg", "order": 8},
]

DEFAULT_CONTENT = {
    "_id": "site",
    "hero": {
        "tagline": "Produccion artistica y espectaculos musicales",
        "subtitle": "Convertimos cada evento en una experiencia unica. Produccion, organizacion y gestion de conciertos y eventos culturales.",
        "cta_primary": "Solicita informacion",
        "cta_secondary": "Descubre nuestros artistas",
    },
    "about": {
        "title": "Quienes Somos",
        "heading": "Mas de 30 años dedicados a la musica y al espectaculo",
        "paragraphs": [
            "Siroco Producciones nace de una trayectoria de mas de tres decadas vinculada al mundo de la musica, los espectaculos en directo y la gestion artistica.",
            "Durante mas de 30 años hemos trabajado junto a artistas, musicos, tecnicos, promotores y administraciones publicas, participando en la organizacion y desarrollo de eventos de muy diversa naturaleza.",
            "Entendemos que detras de cada evento existe una gran responsabilidad. Por ello, trabajamos con rigor, transparencia y atencion al detalle, garantizando una gestion eficiente desde la planificacion inicial hasta la finalizacion del espectaculo.",
        ],
        "pillars": ["Profesionalidad", "Compromiso", "Seriedad"],
    },
    "origin": {
        "title": "El Nombre Siroco",
        "paragraphs": [
            "El nombre 'Siroco' hace referencia al viento mediterraneo que llega desde el Sahara y atraviesa el Mediterraneo, recorriendo largas distancias y transformando todo aquello que encuentra a su paso. Es un simbolo de fuerza, movimiento, energia y conexion entre culturas.",
            "Precisamente esos valores son los que definen nuestra forma de entender la musica y los espectaculos: la capacidad de emocionar, de unir a las personas y de dejar una huella imborrable en cada escenario y en cada publico.",
            "Pero nuestro nombre tambien encierra un significado muy especial y personal. Siroco es un sentido homenaje al maestro Paco de Lucia y a su obra maestra Siroco, considerada una de las grabaciones mas influyentes y admiradas de la historia de la musica española y del flamenco contemporaneo.",
            "Elegimos este nombre porque refleja nuestra identidad: la fuerza de un viento capaz de recorrer caminos y la inspiracion de un artista que cambio para siempre la historia de la musica.",
        ],
        "album_caption": "Siroco - Paco de Lucia",
    },
    "services": [
        {"title": "Produccion de Conciertos", "description": "Organizacion integral de conciertos musicales para ciclos culturales, festivales, homenajes y eventos especiales.", "items": ["Contratacion artistica", "Coordinacion tecnica", "Produccion ejecutiva", "Gestion de permisos", "Supervision del evento"]},
        {"title": "Programacion Cultural para Ayuntamientos", "description": "Diseñamos programaciones musicales adaptadas a las necesidades de cada municipio.", "items": ["Ferias y fiestas", "Verano cultural", "Navidad", "Carnaval", "Eventos institucionales", "Jornadas culturales"]},
        {"title": "Produccion Tecnica", "description": "Coordinamos todos los recursos tecnicos necesarios para el desarrollo del espectaculo.", "items": ["Sonido profesional", "Iluminacion", "Escenarios", "Pantallas LED", "Generadores electricos", "Personal tecnico especializado"]},
    ],
    "contact": {
        "title": "Contacto",
        "heading": "Solicita informacion sin compromiso",
        "subtitle": "Descubre como podemos dar vida a tu proximo evento.",
        "phone": "+34 679 360 643",
        "email": "Sirocoproducciones@hotmail.com",
        "location": "San Fernando (Cadiz), Andalucia, España",
    },
    "ui": {
        "nav_home": "Inicio",
        "nav_artists": "Artistas",
        "nav_services": "Servicios",
        "nav_about": "Nosotros",
        "nav_origin": "El Nombre",
        "nav_contact": "Contacto",
        "form_name": "Nombre",
        "form_email": "Email",
        "form_subject": "Asunto",
        "form_message": "Mensaje",
        "form_send": "Enviar mensaje",
        "form_success": "Mensaje enviado. Gracias por contactar con Siroco Producciones.",
        "form_error": "Ocurrio un error. Intentalo de nuevo.",
        "artists_title": "Nuestros Artistas",
        "artists_subtitle": "El talento que da vida a cada escenario",
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
    artists = await db.artists.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    doc = dict(doc)
    doc.pop("_id", None)
    doc["artists"] = artists
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
    to_translate = []
    for s in strings:
        h = _cache_key(lang, s)
        cached = await db.translations.find_one({"_id": h})
        if cached:
            mapping[s] = cached["text"]
        else:
            to_translate.append(s)
    to_translate = list(dict.fromkeys(to_translate))
    if to_translate and EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"translate-{lang}",
                           system_message=f"You are a professional translator. Translate the given Spanish strings into {LANG_NAMES.get(lang, lang)}. Keep proper names of artists and 'Siroco Producciones', 'Paco de Lucia' unchanged. Return ONLY a JSON array of translated strings in the exact same order, no extra text.").with_model("gemini", "gemini-3-flash-preview")
            payload = json.dumps(to_translate, ensure_ascii=False)
            resp = await chat.send_message(UserMessage(text=f"Translate these strings (JSON array): {payload}"))
            txt = resp.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1]
                if txt.startswith("json"):
                    txt = txt[4:]
            translated = json.loads(txt)
            for src, tr in zip(to_translate, translated):
                mapping[src] = tr
                h = _cache_key(lang, src)
                await db.translations.update_one({"_id": h}, {"$set": {"text": tr, "lang": lang}}, upsert=True)
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
    payload.pop("artists", None)
    payload.pop("_id", None)
    await db.site_content.update_one({"_id": "site"}, {"$set": payload}, upsert=True)
    await db.translations.delete_many({})
    return await get_site_doc()

@api_router.post("/admin/artists")
async def create_artist(artist: Artist, current=Depends(get_current_user)):
    doc = artist.model_dump()
    await db.artists.insert_one({**doc, "_mongo": True})
    await db.artists.update_one({"id": doc["id"]}, {"$unset": {"_mongo": ""}})
    await db.translations.delete_many({})
    return doc

@api_router.put("/admin/artists/{artist_id}")
async def update_artist(artist_id: str, artist: Artist, current=Depends(get_current_user)):
    doc = artist.model_dump()
    doc["id"] = artist_id
    await db.artists.update_one({"id": artist_id}, {"$set": doc}, upsert=True)
    await db.translations.delete_many({})
    return doc

@api_router.delete("/admin/artists/{artist_id}")
async def delete_artist(artist_id: str, current=Depends(get_current_user)):
    await db.artists.delete_one({"id": artist_id})
    return {"success": True}

@api_router.get("/admin/messages")
async def get_messages(current=Depends(get_current_user)):
    msgs = await db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return msgs

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
    # seed admin
    admin_email = os.environ["ADMIN_EMAIL"].lower()
    admin_password = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({"email": admin_email, "password_hash": hash_password(admin_password),
                                   "name": "Admin", "role": "admin", "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
    # seed content + artists
    if not await db.site_content.find_one({"_id": "site"}):
        await db.site_content.insert_one(DEFAULT_CONTENT)
    if await db.artists.count_documents({}) == 0:
        await db.artists.insert_many([dict(a) for a in DEFAULT_ARTISTS])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
