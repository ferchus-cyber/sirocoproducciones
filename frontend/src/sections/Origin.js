import { useSite } from "../context/SiteContext";
import { Reveal } from "../components/Reveal";

export const Origin = () => {
  const { content } = useSite();
  const o = content?.origin || {};
  return (
    <section data-testid="origin-section" id="origin" className="relative py-28 overflow-hidden bg-black">
      <div className="absolute inset-0 opacity-20">
        <img src="/media/artists/farruquito.webp" alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-black/80" />
      </div>
      <div className="relative z-10 max-w-4xl mx-auto px-6 lg:px-12">
        <Reveal>
          <p className="section-label mb-4">Siroco</p>
          <h2 className="font-display text-5xl sm:text-6xl tracking-tight mb-12">{o.title}</h2>
        </Reveal>
        <div className="grid md:grid-cols-[1fr_auto] gap-12 items-start">
          <div className="space-y-6">
            {(o.paragraphs || []).map((p, i) => (
              <Reveal key={p.slice(0, 32)} delay={i * 0.08}>
                <p className={`leading-relaxed ${i === 2 ? "text-white border-l-2 border-[#d90429] pl-6 italic font-display text-xl" : "text-white/65"}`}>{p}</p>
              </Reveal>
            ))}
          </div>
          <Reveal delay={0.2}>
            <figure className="text-center">
              <img src="/media/album/siroco-paco-de-lucia.jpg" alt="Siroco - Paco de Lucía"
                className="w-56 h-56 object-cover border border-white/15 shadow-[0_20px_60px_rgba(217,4,41,0.2)]" />
              <figcaption className="mt-4 text-xs uppercase tracking-[0.2em] text-white/50">{o.album_caption}</figcaption>
            </figure>
          </Reveal>
        </div>
      </div>
    </section>
  );
};
