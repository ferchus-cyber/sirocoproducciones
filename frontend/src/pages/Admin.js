import { useState, useEffect } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";
import { Loader2, LogOut, Trash2, Plus, Save, Mail, Upload, Shield } from "lucide-react";

const field = "w-full bg-[#111] border border-white/15 focus:border-[#d90429] outline-none text-white px-3 py-2 text-sm transition-colors";
const label = "block text-xs uppercase tracking-[0.15em] text-white/50 mb-2";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setErr("");
    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("siroco_token", data.token);
      onLogin(data.user);
    } catch (e2) {
      setErr(e2.response?.data?.detail || "Error de acceso");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050505] px-6">
      <form data-testid="admin-login" onSubmit={submit} className="w-full max-w-md border border-white/10 bg-[#0a0a0a] p-10">
        <div className="font-display text-3xl tracking-[0.25em] mb-2">SIROCO<span className="text-[#d90429]">.</span></div>
        <p className="text-white/50 text-sm mb-8 uppercase tracking-[0.2em]">Panel de administración</p>
        <label className={label}>Email</label>
        <input data-testid="admin-email" className={`${field} mb-4`} value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label className={label}>Contraseña</label>
        <input data-testid="admin-password" type="password" className={`${field} mb-6`} value={password} onChange={(e) => setPassword(e.target.value)} required />
        {err && <p data-testid="admin-error" className="text-[#d90429] text-sm mb-4">{err}</p>}
        <button data-testid="admin-login-submit" className="btn-siroco w-full flex items-center justify-center gap-2" disabled={loading}>
          {loading && <Loader2 size={16} className="animate-spin" />} Acceder
        </button>
      </form>
    </div>
  );
}

export default function Admin() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [tab, setTab] = useState("gallery");
  const [content, setContent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [gallery, setGallery] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [admins, setAdmins] = useState([]);
  const [newAdmin, setNewAdmin] = useState({ email: "", name: "", password: "" });

  useEffect(() => {
    const token = localStorage.getItem("siroco_token");
    if (!token) { setChecking(false); return; }
    api.get("/auth/me").then(({ data }) => setUser(data)).catch(() => localStorage.removeItem("siroco_token")).finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    api.get("/admin/content").then(({ data }) => setContent(data)).catch(() => toast.error("Error al cargar el contenido"));
    api.get("/admin/messages").then(({ data }) => setMessages(data)).catch(() => {});
    api.get("/admin/gallery").then(({ data }) => setGallery(data.map((g) => ({ ...g, url: `${process.env.REACT_APP_BACKEND_URL}${g.url}` })))).catch(() => {});
    api.get("/admin/admins").then(({ data }) => setAdmins(data)).catch(() => {});
  }, [user]);

  const logout = () => { localStorage.removeItem("siroco_token"); setUser(null); };

  const saveContent = async () => {
    try { await api.put("/admin/content", content); toast.success("Contenido guardado. Traducciones regeneradas."); }
    catch { toast.error("Error al guardar"); }
  };

  const delMsg = async (id) => {
    try {
      await api.delete(`/admin/messages/${id}`);
      setMessages(messages.filter((m) => m.id !== id));
    } catch { toast.error("No se pudo eliminar el mensaje"); }
  };

  const uploadPhotos = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    const uploaded = [];
    for (const file of Array.from(files)) {
      const fd = new FormData();
      fd.append("file", file);
      try {
        const { data } = await api.post("/admin/gallery", fd, { headers: { "Content-Type": "multipart/form-data" } });
        uploaded.push({ ...data, url: `${process.env.REACT_APP_BACKEND_URL}${data.url}` });
      } catch (e) {
        toast.error(`Error al subir ${file.name}`);
      }
    }
    if (uploaded.length) {
      setGallery([...gallery, ...uploaded]);
      toast.success(`${uploaded.length} foto(s) subida(s)`);
    }
    setUploading(false);
  };

  const delPhoto = async (id) => {
    try {
      await api.delete(`/admin/gallery/${id}`);
      setGallery(gallery.filter((g) => g.id !== id));
      toast.success("Foto eliminada");
    } catch { toast.error("No se pudo eliminar la foto"); }
  };

  const createAdmin = async () => {
    try {
      await api.post("/admin/admins", newAdmin);
      const { data } = await api.get("/admin/admins");
      setAdmins(data);
      setNewAdmin({ email: "", name: "", password: "" });
      toast.success("Administrador creado");
    } catch (e) { toast.error(e.response?.data?.detail || "No se pudo crear el administrador"); }
  };

  const delAdmin = async (email) => {
    try {
      await api.delete(`/admin/admins/${encodeURIComponent(email)}`);
      setAdmins(admins.filter((a) => a.email !== email));
      toast.success("Administrador eliminado");
    } catch (e) { toast.error(e.response?.data?.detail || "No se pudo eliminar"); }
  };

  if (checking) return <div className="min-h-screen flex items-center justify-center bg-[#050505]"><Loader2 className="animate-spin text-[#d90429]" size={36} /></div>;
  if (!user) return <Login onLogin={setUser} />;
  if (!content) return <div className="min-h-screen flex items-center justify-center bg-[#050505]"><Loader2 className="animate-spin text-[#d90429]" size={36} /></div>;

  const setField = (section, key, value) => setContent({ ...content, [section]: { ...content[section], [key]: value } });

  const tabs = [["gallery", `Galería (${gallery.length})`], ["texts", "Textos"], ["messages", `Mensajes (${messages.length})`], ["admins", `Administradores (${admins.length})`]];

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <header className="border-b border-white/10 sticky top-0 bg-black/90 backdrop-blur z-40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-display text-xl tracking-[0.25em]">SIROCO<span className="text-[#d90429]">.</span> <span className="text-white/40 text-sm font-sans">Admin</span></div>
          <button data-testid="admin-logout" onClick={logout} className="flex items-center gap-2 text-sm text-white/60 hover:text-white"><LogOut size={16} /> Salir</button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex flex-wrap gap-2 mb-8 border-b border-white/10">
          {tabs.map(([id, lbl]) => (
            <button key={id} data-testid={`tab-${id}`} onClick={() => setTab(id)}
              className={`px-4 sm:px-5 py-3 text-xs sm:text-sm uppercase tracking-[0.15em] border-b-2 -mb-px transition-colors whitespace-nowrap ${tab === id ? "border-[#d90429] text-white" : "border-transparent text-white/50 hover:text-white"}`}>{lbl}</button>
          ))}
        </div>

        {tab === "texts" && (
          <div className="space-y-8 max-w-3xl" data-testid="admin-texts">
            <Section title="Hero">
              <Field l="Tagline" v={content.hero.tagline} on={(v) => setField("hero", "tagline", v)} />
              <Field l="Subtítulo" area v={content.hero.subtitle} on={(v) => setField("hero", "subtitle", v)} />
            </Section>
            <Section title="Nosotros">
              <Field l="Encabezado" v={content.about.heading} on={(v) => setField("about", "heading", v)} />
              <Field l="Párrafos (uno por línea)" area rows={5} v={(content.about.paragraphs || []).join("\n")} on={(v) => setField("about", "paragraphs", v.split("\n"))} />
            </Section>
            <Section title="El Nombre Siroco">
              <Field l="Párrafos (uno por línea)" area rows={6} v={(content.origin.paragraphs || []).join("\n")} on={(v) => setField("origin", "paragraphs", v.split("\n"))} />
            </Section>
            <Section title="Contacto">
              <Field l="Teléfono" v={content.contact.phone} on={(v) => setField("contact", "phone", v)} />
              <Field l="Email" v={content.contact.email} on={(v) => setField("contact", "email", v)} />
              <Field l="Ubicación" v={content.contact.location} on={(v) => setField("contact", "location", v)} />
            </Section>
            <button data-testid="save-content" onClick={saveContent} className="btn-siroco flex items-center gap-2"><Save size={16} /> Guardar contenido</button>
          </div>
        )}

        {tab === "messages" && (
          <div className="space-y-4" data-testid="admin-messages">
            {messages.length === 0 && <p className="text-white/50">No hay mensajes.</p>}
            {messages.map((m) => (
              <div key={m.id} className="border border-white/10 bg-[#0a0a0a] p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-display text-xl">{m.subject}</p>
                    <p className="text-sm text-white/60 flex items-center gap-2 mt-1"><Mail size={13} className="text-[#d90429]" /> {m.name} · {m.email}</p>
                  </div>
                  <button onClick={() => delMsg(m.id)} className="text-white/40 hover:text-[#d90429]"><Trash2 size={16} /></button>
                </div>
                <p className="text-white/70 text-sm mt-4 leading-relaxed">{m.message}</p>
                <p className="text-xs text-white/30 mt-3">{new Date(m.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}

        {tab === "gallery" && (
          <div data-testid="admin-gallery">
            <div className="border border-dashed border-white/20 bg-[#0a0a0a] p-8 text-center mb-8">
              <Upload className="text-[#d90429] mx-auto mb-4" size={30} strokeWidth={1.4} />
              <p className="section-label mb-2">Galería de Eventos Recientes</p>
              <p className="text-white/50 text-sm mb-6">Sube fotos del evento desde tu ordenador (JPG, PNG, WEBP).</p>
              <label className="btn-siroco inline-flex items-center gap-2 cursor-pointer">
                {uploading ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />} Subir fotos
                <input data-testid="gallery-upload" type="file" accept="image/*" multiple className="hidden"
                  disabled={uploading} onChange={(e) => uploadPhotos(e.target.files)} />
              </label>
            </div>
            {gallery.length === 0 ? (
              <p className="text-white/50">Aún no hay fotos. Se mostrarán unas imágenes por defecto hasta que subas las tuyas.</p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {gallery.map((g) => (
                  <div key={g.id} className="relative group aspect-[4/3] overflow-hidden border border-white/10">
                    <img src={g.url} alt="" className="w-full h-full object-cover" />
                    <button data-testid={`delete-photo-${g.id}`} onClick={() => delPhoto(g.id)}
                      className="absolute top-2 right-2 bg-black/70 text-white/80 hover:text-[#d90429] p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Trash2 size={15} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "admins" && (
          <div data-testid="admin-admins" className="max-w-3xl">
            <div className="border border-dashed border-white/20 bg-[#0a0a0a] p-8 mb-8">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="text-[#d90429]" size={24} />
                <p className="section-label !mb-0">Añadir administrador</p>
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <div><label className={label}>Email</label><input data-testid="new-admin-email" type="email" className={field} value={newAdmin.email} onChange={(e) => setNewAdmin({ ...newAdmin, email: e.target.value })} /></div>
                <div><label className={label}>Nombre</label><input data-testid="new-admin-name" className={field} value={newAdmin.name} onChange={(e) => setNewAdmin({ ...newAdmin, name: e.target.value })} /></div>
                <div className="sm:col-span-2"><label className={label}>Contraseña (mín. 8 caracteres)</label><input data-testid="new-admin-password" type="password" className={field} value={newAdmin.password} onChange={(e) => setNewAdmin({ ...newAdmin, password: e.target.value })} /></div>
              </div>
              <button data-testid="create-admin" onClick={createAdmin} className="btn-siroco mt-5 flex items-center gap-2"><Plus size={16} /> Crear administrador</button>
            </div>
            <div className="space-y-3">
              {admins.map((a) => (
                <div key={a.email} className="flex items-center justify-between border border-white/10 bg-[#0a0a0a] p-5">
                  <div>
                    <p className="text-white flex items-center gap-2">{a.name} {a.is_self && <span className="text-xs text-[#d90429] uppercase tracking-[0.15em]">(tú)</span>}</p>
                    <p className="text-sm text-white/50">{a.email}</p>
                  </div>
                  {!a.is_self && (
                    <button data-testid={`delete-admin-${a.email}`} onClick={() => delAdmin(a.email)}
                      className="text-white/40 hover:text-[#d90429] transition-colors"><Trash2 size={16} /></button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const Section = ({ title, children }) => (
  <div className="border border-white/10 bg-[#0a0a0a] p-6">
    <p className="section-label mb-5">{title}</p>
    <div className="space-y-4">{children}</div>
  </div>
);
const Field = ({ l, v, on, area, rows = 3 }) => (
  <div>
    <label className={label}>{l}</label>
    {area ? <textarea rows={rows} className={field} value={v} onChange={(e) => on(e.target.value)} />
      : <input className={field} value={v} onChange={(e) => on(e.target.value)} />}
  </div>
);
