import { useSite } from "../context/SiteContext";
import { Reveal } from "../components/Reveal";

const SPANS = [
  "md:col-span-8 md:row-span-2",
  "md:col-span-4 md:row-span-1",
  "md:col-span-4 md:row-span-1",
  "md:col-span-4 md:row-span-2",
  "md:col-span-4 md:row-span-1",
  "md:col-span-4 md:row-span-1",
  "md:col-span-6 md:row-span-1",
  "md:col-span-6 md:row-span-1",
];

export const Artists = () => {
  const { content } = useSite();
  const ui = content?.ui || {};
  const artists = content?.artists || [];

  return (
    <section data-testid="artists-section" id="artists" className="py-32 lg:py-44 bg-[#050505]">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <Reveal>
          <p className="section-label mb-4">{ui.artists_subtitle}</p>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight mb-20">{ui.artists_title}</h2>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-12 auto-rows-[220px] gap-4">
          {artists.map((a, i) => (
            <Reveal key={a.id} delay={i * 0.05} className={SPANS[i % SPANS.length]}>
              <div data-testid={`artist-card-${i}`}
                className="group relative h-full w-full overflow-hidden border border-white/10 cursor-pointer">
                <img src={a.image} alt={a.name}
                  className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-700 group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent group-hover:from-black/95 transition-all duration-500" />
                <div className="absolute bottom-0 left-0 p-6">
                  <span className="section-label">{a.role}</span>
                  <h3 className="font-display text-2xl sm:text-3xl mt-1 text-white">{a.name}</h3>
                  <p className="text-white/60 text-sm mt-2 max-h-0 overflow-hidden group-hover:max-h-40 transition-all duration-500 max-w-md">
                    {a.bio}
                  </p>
                </div>
                <div className="absolute top-0 left-0 w-1 h-0 bg-[#d90429] group-hover:h-full transition-all duration-500" />
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
};
