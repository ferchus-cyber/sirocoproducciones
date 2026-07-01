import { useSite } from "../context/SiteContext";
import { Reveal } from "../components/Reveal";

export const About = () => {
  const { content } = useSite();
  const a = content?.about || {};
  return (
    <section data-testid="about-section" id="about" className="py-24 bg-[#050505]">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 grid lg:grid-cols-2 gap-16 items-center">
        <Reveal>
          <p className="section-label mb-4">{a.title}</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight leading-tight mb-8">{a.heading}</h2>
          <div className="space-y-5">
            {(a.paragraphs || []).map((p, i) => (
              <p key={i} className="text-white/65 leading-relaxed">{p}</p>
            ))}
          </div>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="grid grid-cols-1 gap-4">
            {(a.pillars || []).map((p, i) => (
              <div key={i} data-testid={`pillar-${i}`}
                className="flex items-center gap-6 border border-white/10 bg-[#0a0a0a] p-8 hover:border-[#d90429]/60 transition-colors">
                <span className="font-display text-5xl text-[#d90429]">0{i + 1}</span>
                <span className="text-xl uppercase tracking-[0.2em] text-white/90">{p}</span>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
};
