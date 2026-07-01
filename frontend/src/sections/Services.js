import { useSite } from "../context/SiteContext";
import { Reveal } from "../components/Reveal";
import { Music, Building2, Settings, Check } from "lucide-react";

const ICONS = [Music, Building2, Settings];

export const Services = () => {
  const { content } = useSite();
  const ui = content?.ui || {};
  const services = content?.services || [];

  return (
    <section data-testid="services-section" id="services" className="py-24 bg-[#0a0a0a] border-y border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <Reveal>
          <p className="section-label mb-4">Siroco Producciones</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight mb-16">{ui.services_title}</h2>
        </Reveal>
        <div className="grid md:grid-cols-3 gap-6">
          {services.map((s, i) => {
            const Icon = ICONS[i % ICONS.length];
            return (
              <Reveal key={s.title} delay={i * 0.1}>
                <div data-testid={`service-card-${i}`}
                  className="group h-full bg-[#050505] border border-white/10 p-8 hover:border-[#d90429]/60 hover:-translate-y-1 transition-all duration-500">
                  <Icon className="text-[#d90429] mb-6" size={34} strokeWidth={1.2} />
                  <h3 className="font-display text-2xl mb-4">{s.title}</h3>
                  <p className="text-white/60 text-sm leading-relaxed mb-6">{s.description}</p>
                  <ul className="space-y-2">
                    {(s.items || []).map((it, j) => (
                      <li key={it} className="flex items-center gap-3 text-sm text-white/70">
                        <Check size={14} className="text-[#d90429] shrink-0" /> {it}
                      </li>
                    ))}
                  </ul>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
};
