import { Reveal } from "../components/Reveal";
import { Calendar, Clock, MapPin, Mic2 } from "lucide-react";

const EVENT = {
  title: "75 Aniversario Camarón",
  subtitle: "Concierto en la Plaza del Rey",
  date: "Viernes 3 de Julio",
  time: "22:30 h",
  venue: "Plaza del Rey · San Fernando (Cádiz)",
  host: "Presenta: Juan Garrido",
  lineup: ["Duquende", "El Farru", "May Fernández", "Rubio de Pruna", "Rosario Montoya «La Reina Gitana»"],
  poster: "/media/events/camaron-75.jpg",
};

export const Events = () => {
  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  return (
    <section data-testid="events-section" id="events" className="py-32 lg:py-44 bg-[#0a0a0a] border-y border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <Reveal>
          <p className="section-label mb-4">Agenda</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight mb-20">Próximos Eventos</h2>
        </Reveal>

        <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
          <Reveal>
            <div className="relative group overflow-hidden border border-white/10">
              <img data-testid="event-poster" src={EVENT.poster} alt={EVENT.title}
                className="w-full h-auto object-contain transition-transform duration-700 group-hover:scale-[1.02]" />
              <div className="absolute top-0 left-0 w-1 h-0 bg-[#d90429] group-hover:h-full transition-all duration-500" />
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <div className="border border-white/10 bg-[#050505] p-8 lg:p-10">
              <span className="section-label">{EVENT.subtitle}</span>
              <h3 className="font-display text-3xl sm:text-4xl mt-2 mb-8">{EVENT.title}</h3>

              <div className="space-y-4 text-white/75">
                <p className="flex items-center gap-4"><Calendar size={18} className="text-[#d90429] shrink-0" /> {EVENT.date}</p>
                <p className="flex items-center gap-4"><Clock size={18} className="text-[#d90429] shrink-0" /> {EVENT.time}</p>
                <p className="flex items-center gap-4"><MapPin size={18} className="text-[#d90429] shrink-0" /> {EVENT.venue}</p>
                <p className="flex items-center gap-4"><Mic2 size={18} className="text-[#d90429] shrink-0" /> {EVENT.host}</p>
              </div>

              <div className="mt-8 pt-8 border-t border-white/10">
                <p className="section-label mb-4">Cartel</p>
                <div className="flex flex-wrap gap-2">
                  {EVENT.lineup.map((artist) => (
                    <span key={artist} className="border border-white/15 px-4 py-2 text-sm text-white/80">{artist}</span>
                  ))}
                </div>
              </div>

              <button data-testid="event-cta" className="btn-siroco mt-10" onClick={() => scrollTo("contact")}>
                Más información
              </button>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
};
