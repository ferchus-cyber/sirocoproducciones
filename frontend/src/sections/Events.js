import { useState, useEffect } from "react";
import { Reveal } from "../components/Reveal";
import { api } from "../lib/api";
import { toast } from "sonner";
import { Calendar, MapPin, Users, CheckCircle2, Loader2, Bell } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const EVENT = {
  title: "75 Aniversario Camarón",
  subtitle: "Concierto en la Plaza del Rey",
  date: "Viernes 3 de Julio · San Fernando (Cádiz)",
  poster: "/media/events/camaron-75.jpg",
  lineup: ["Duquende", "El Farru", "May Fernández", "Rubio de Pruna", "Rosario Montoya «La Reina Gitana»"],
  fallbackGallery: [
    { url: "/media/artists/duquende.jpeg", caption: "Duquende" },
    { url: "/media/artists/antonio-el-farru.jpg", caption: "El Farru" },
    { url: "/media/artists/may-fernandez.jpg", caption: "May Fernández" },
    { url: "/media/artists/rubio-de-pruna.jpeg", caption: "Rubio de Pruna" },
    { url: "/media/artists/la-reina-gitana.jpg", caption: "La Reina Gitana" },
    { url: "/media/artists/montse-cortes.jpeg", caption: "En directo" },
  ],
};

export const Events = () => {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [gallery, setGallery] = useState([]);

  useEffect(() => {
    api.get("/gallery")
      .then(({ data }) => setGallery(data.map((g) => ({ ...g, url: `${BACKEND_URL}${g.url}` }))))
      .catch(() => setGallery([]));
  }, []);

  const photos = gallery.length > 0 ? gallery : EVENT.fallbackGallery;

  const subscribe = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post("/notify", { email });
      toast.success("¡Listo! Te avisaremos del próximo evento.");
      setEmail("");
    } catch {
      toast.error("No se pudo registrar tu email. Inténtalo de nuevo.");
    } finally {
      setSending(false);
    }
  };

  return (
    <section data-testid="events-section" id="events" className="py-32 lg:py-44 bg-[#0a0a0a] border-y border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <Reveal>
          <p className="section-label mb-4">Recuerdos</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight mb-6">Eventos Recientes</h2>
          <p className="text-white/60 max-w-2xl mb-20">Repasamos algunos de nuestros últimos espectáculos. Momentos que quedan para el recuerdo.</p>
        </Reveal>

        {/* Featured past event */}
        <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center mb-24">
          <Reveal>
            <div className="relative group overflow-hidden border border-white/10">
              <img data-testid="event-poster" src={EVENT.poster} alt={EVENT.title}
                className="w-full h-auto object-contain transition-transform duration-700 group-hover:scale-[1.02]" />
              <span className="absolute top-4 left-4 bg-[#d90429] text-white text-xs uppercase tracking-[0.2em] px-4 py-2">Celebrado</span>
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <div className="border border-white/10 bg-[#050505] p-8 lg:p-10">
              <div className="flex items-center gap-3 text-[#d90429] mb-6">
                <CheckCircle2 size={22} />
                <span className="uppercase tracking-[0.2em] text-sm">Un éxito rotundo</span>
              </div>
              <span className="section-label">{EVENT.subtitle}</span>
              <h3 className="font-display text-3xl sm:text-4xl mt-2 mb-6">{EVENT.title}</h3>
              <p className="text-white/70 leading-relaxed mb-8">
                La Plaza del Rey se llenó para rendir homenaje a Camarón en su 75 aniversario. Una noche
                inolvidable de cante y baile que reunió a algunos de los grandes nombres del flamenco actual
                ante un público entregado.
              </p>

              <div className="space-y-4 text-white/75">
                <p className="flex items-center gap-4"><Calendar size={18} className="text-[#d90429] shrink-0" /> {EVENT.date}</p>
                <p className="flex items-center gap-4"><MapPin size={18} className="text-[#d90429] shrink-0" /> Plaza del Rey · Lleno absoluto</p>
                <p className="flex items-start gap-4"><Users size={18} className="text-[#d90429] shrink-0 mt-1" /> <span>{EVENT.lineup.join(" · ")}</span></p>
              </div>
            </div>
          </Reveal>
        </div>

        {/* Photo gallery */}
        <Reveal>
          <p className="section-label mb-8">Galería de fotos</p>
        </Reveal>
        <div data-testid="event-gallery" className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-24">
          {photos.map((img, i) => (
            <Reveal key={img.url} delay={i * 0.05}>
              <div className="group relative aspect-[4/3] overflow-hidden border border-white/10">
                <img src={img.url} alt={img.caption || "Evento"}
                  className="absolute inset-0 w-full h-full object-cover object-top grayscale group-hover:grayscale-0 transition-all duration-700 group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                {img.caption && <span className="absolute bottom-4 left-4 text-sm text-white/90 uppercase tracking-[0.15em]">{img.caption}</span>}
              </div>
            </Reveal>
          ))}
        </div>

        {/* Notify form */}
        <Reveal>
          <div className="border border-white/10 bg-[#050505] p-8 lg:p-12 text-center max-w-3xl mx-auto">
            <Bell className="text-[#d90429] mx-auto mb-6" size={30} strokeWidth={1.4} />
            <h3 className="font-display text-3xl sm:text-4xl mb-3">Avísame para el próximo evento</h3>
            <p className="text-white/60 mb-8">Déjanos tu email y serás el primero en enterarte de nuestros próximos espectáculos.</p>
            <form data-testid="notify-form" onSubmit={subscribe} className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
              <input data-testid="notify-email" type="email" required placeholder="tucorreo@email.com"
                value={email} onChange={(e) => setEmail(e.target.value)}
                className="flex-1 bg-[#111111] border-b border-white/20 focus:border-[#d90429] outline-none text-white px-4 py-3 placeholder:text-white/40 transition-colors" />
              <button data-testid="notify-submit" type="submit" disabled={sending} className="btn-siroco flex items-center justify-center gap-2 disabled:opacity-60 whitespace-nowrap">
                {sending && <Loader2 size={16} className="animate-spin" />} Avísame
              </button>
            </form>
          </div>
        </Reveal>
      </div>
    </section>
  );
};
