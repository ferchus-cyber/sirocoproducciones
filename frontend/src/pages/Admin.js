import { useState, useEffect } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";
import { Loader2, LogOut, Trash2, Plus, Save, Mail } from "lucide-react";

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

const emptyArtist = { name: "", role: "", bio: "", image: "/media/artists/", order: 99 };

export default function Admin() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [tab, setTab] = useState("artists");
  const [content, setContent] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newArtist, setNewArtist] = useState(emptyArtist);

  useEffect(() => {
    const token = localStorage.getItem("siroco_token");
    if (!token) { setChecking(false); return; }
    api.get("/auth/me").then(({ data }) => setUser(data)).catch(() => localStorage.removeItem("siroco_token")).finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    api.get("/admin/content").then(({ data }) => setContent(data));
    api.get("/admin/messages").then(({ data }) => setMessages(data));
  }, [user]);

  const logout = () => { localStorage.removeItem("siroco_token"); setUser(null); };

  const saveContent = async () => {
    const { artists, ...rest } = content;
    try { await api.put("/admin/content", rest); toast.success("Contenido guardado. Traducciones regeneradas."); }
    catch { toast.error("Error al guardar"); }
  };

  const saveArtist = async (a) => {
    try { await api.put(`/admin/artists/${a.id}`, a); toast.success("Artista actualizado"); }
    catch { toast.error("Error"); }
  };
  const addArtist = async () => {
    try {
      const { data } = await api.post("/admin/artists", { ...newArtist, id: crypto.randomUUID() });
      setContent({ ...content, artists: [...content.artists, data] });
      setNewArtist(emptyArtist);
      toast.success("Artista añadido");
    } catch { toast.error("Error"); }
  };
  const delArtist = async (id) => {
    await api.delete(`/admin/artists/${id}`);
    setContent({ ...content, artists: content.artists.filter((x) => x.id !== id) });
    toast.success("Eliminado");
  };
  const delMsg = async (id) => {
    await api.delete(`/admin/messages/${id}`);
    setMessages(messages.filter((m) => m.id !== id));
  };

  if (checking) return <div className="min-h-screen flex items-center justify-center bg-[#050505]"><Loader2 className="animate-spin text-[#d90429]" size={36} /></div>;
  if (!user) return <Login onLogin={setUser} />;
  if (!content) return <div className="min-h-screen flex items-center justify-center bg-[#050505]"><Loader2 className="animate-spin text-[#d90429]" size={36} /></div>;

  const setField = (section, key, value) => setContent({ ...content, [section]: { ...content[section], [key]: value } });
  const setArtistField = (id, key, value) => setContent({ ...content, artists: content.artists.map((a) => a.id === id ? { ...a, [key]: value } : a) });

  const tabs = [["artists", "Artistas"], ["texts", "Textos"], ["messages", `Mensajes (${messages.length})`]];

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <header className="border-b border-white/10 sticky top-0 bg-black/90 backdrop-blur z-40">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-display text-xl tracking-[0.25em]">SIROCO<span className="text-[#d90429]">.</span> <span className="text-white/40 text-sm font-sans">Admin</span></div>
          <button data-testid="admin-logout" onClick={logout} className="flex items-center gap-2 text-sm text-white/60 hover:text-white"><LogOut size={16} /> Salir</button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex gap-2 mb-8 border-b border-white/10">
          {tabs.map(([id, lbl]) => (
            <button key={id} data-testid={`tab-${id}`} onClick={() => setTab(id)}
              className={`px-5 py-3 text-sm uppercase tracking-[0.15em] border-b-2 -mb-px transition-colors ${tab === id ? "border-[#d90429] text-white" : "border-transparent text-white/50 hover:text-white"}`}>{lbl}</button>
          ))}
        </div>

        {tab === "artists" && (
          <div className="space-y-4" data-testid="admin-artists">
            {content.artists.map((a) => (
              <div key={a.id} className="border border-white/10 bg-[#0a0a0a] p-5 grid md:grid-cols-[100px_1fr_auto] gap-5 items-start">
                <img src={a.image} alt={a.name} className="w-24 h-24 object-cover object-top border border-white/10" />
                <div className="grid sm:grid-cols-2 gap-3 w-full">
                  <div><label className={label}>Nombre</label><input className={field} value={a.name} onChange={(e) => setArtistField(a.id, "name", e.target.value)} /></div>
                  <div><label className={label}>Rol</label><input className={field} value={a.role} onChange={(e) => setArtistField(a.id, "role", e.target.value)} /></div>
                  <div className="sm:col-span-2"><label className={label}>Bio</label><textarea rows={2} className={field} value={a.bio} onChange={(e) => setArtistField(a.id, "bio", e.target.value)} /></div>
                  <div><label className={label}>Imagen (URL)</label><input className={field} value={a.image} onChange={(e) => setArtistField(a.id, "image", e.target.value)} /></div>
                  <div><label className={label}>Orden</label><input type="number" className={field} value={a.order} onChange={(e) => setArtistField(a.id, "order", parseInt(e.target.value || "0"))} /></div>
                </div>
                <div className="flex md:flex-col gap-2">
                  <button data-testid={`save-artist-${a.id}`} onClick={() => saveArtist(a)} className="btn-siroco !px-4 !py-2 flex items-center gap-2"><Save size={14} /></button>
                  <button data-testid={`delete-artist-${a.id}`} onClick={() => delArtist(a.id)} className="btn-outline-siroco !px-4 !py-2 flex items-center gap-2"><Trash2 size={14} /></button>
                </div>
              </div>
            ))}
            <div className="border border-dashed border-white/20 bg-[#0a0a0a] p-5">
              <p className="section-label mb-4">Añadir artista</p>
              <div className="grid sm:grid-cols-2 gap-3">
                <input className={field} placeholder="Nombre" value={newArtist.name} onChange={(e) => setNewArtist({ ...newArtist, name: e.target.value })} />
                <input className={field} placeholder="Rol" value={newArtist.role} onChange={(e) => setNewArtist({ ...newArtist, role: e.target.value })} />
                <textarea className={`${field} sm:col-span-2`} placeholder="Bio" value={newArtist.bio} onChange={(e) => setNewArtist({ ...newArtist, bio: e.target.value })} />
                <input className={field} placeholder="/media/artists/..." value={newArtist.image} onChange={(e) => setNewArtist({ ...newArtist, image: e.target.value })} />
                <input type="number" className={field} placeholder="Orden" value={newArtist.order} onChange={(e) => setNewArtist({ ...newArtist, order: parseInt(e.target.value || "0") })} />
              </div>
              <button data-testid="add-artist" onClick={addArtist} className="btn-siroco mt-4 flex items-center gap-2"><Plus size={16} /> Añadir</button>
            </div>
          </div>
        )}

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
