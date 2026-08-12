import { useState } from "react";
import { useSite } from "../context/SiteContext";
import { Reveal } from "../components/Reveal";
import { api } from "../lib/api";
import { Phone, Mail, MapPin, Loader2 } from "lucide-react";
import { toast } from "sonner";

export const Contact = () => {
  const { content } = useSite();
  const c = content?.contact || {};
  const ui = content?.ui || {};
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sending, setSending] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post("/contact", form);
      toast.success(ui.form_success || "Mensaje enviado.");
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch (err) {
      toast.error(ui.form_error || "Ocurrió un error.");
    } finally {
      setSending(false);
    }
  };

  const field = "w-full bg-[#111111] border-b border-white/20 focus:border-[#d90429] outline-none text-white px-4 py-3 placeholder:text-white/40 transition-colors";

  return (
    <section data-testid="contact-section" id="contact" className="py-32 lg:py-44 bg-[#0a0a0a] border-t border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 grid lg:grid-cols-2 gap-16">
        <Reveal>
          <p className="section-label mb-4">{c.title}</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight mb-6">{c.heading}</h2>
          <p className="text-white/60 mb-10">{c.subtitle}</p>
          <div className="space-y-5 text-white/70">
            <p className="flex items-center gap-4"><Phone className="text-[#d90429]" size={18} /> {c.phone}</p>
            <p className="flex items-center gap-4"><Mail className="text-[#d90429]" size={18} /> {c.email}</p>
            <p className="flex items-center gap-4"><MapPin className="text-[#d90429]" size={18} /> {c.location}</p>
          </div>
        </Reveal>

        <Reveal delay={0.15}>
          <form data-testid="contact-form" onSubmit={submit} className="space-y-6">
            <input data-testid="contact-name" required placeholder={ui.form_name || "Nombre"} className={field}
              value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input data-testid="contact-email" type="email" required placeholder={ui.form_email || "Email"} className={field}
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input data-testid="contact-subject" required placeholder={ui.form_subject || "Asunto"} className={field}
              value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
            <textarea data-testid="contact-message" required rows={5} placeholder={ui.form_message || "Mensaje"} className={field}
              value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
            <button data-testid="contact-submit" type="submit" disabled={sending} className="btn-siroco flex items-center gap-3 disabled:opacity-60">
              {sending && <Loader2 size={16} className="animate-spin" />} {ui.form_send || "Enviar mensaje"}
            </button>
          </form>
        </Reveal>
      </div>
    </section>
  );
};
