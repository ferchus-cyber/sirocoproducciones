import { motion } from "framer-motion";
import { useSite } from "../context/SiteContext";

export const Hero = () => {
  const { content } = useSite();
  const h = content?.hero || {};
  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });

  return (
    <section data-testid="hero-section" id="home" className="relative min-h-screen flex items-center overflow-hidden">
      <div className="absolute inset-0">
        <img src="/media/hero-bg.jpg" alt="" className="w-full h-full object-cover opacity-40" />
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/70 to-black/30" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/60" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-12 w-full">
        <motion.img
          data-testid="hero-logo"
          src="/media/siroco-logo.png"
          alt="Siroco Producciones"
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-2xl mb-8"
        />
        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.4 }}
          className="section-label mb-6">
          {h.tagline}
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.6 }}
          className="max-w-xl text-white/70 text-lg leading-relaxed mb-10">
          {h.subtitle}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.8 }}
          className="flex flex-wrap gap-4">
          <button data-testid="hero-cta-contact" className="btn-siroco" onClick={() => scrollTo("contact")}>
            {h.cta_primary}
          </button>
          <button data-testid="hero-cta-artists" className="btn-outline-siroco" onClick={() => scrollTo("artists")}>
            {h.cta_secondary}
          </button>
        </motion.div>
      </div>
    </section>
  );
};
