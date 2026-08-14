import { useState, useEffect } from "react";
import { Instagram, Youtube, Menu, X, Globe, Check } from "lucide-react";
import { useSite, LANGS } from "../context/SiteContext";

const INSTAGRAM = "https://www.instagram.com/sirocoproducciones?igsh=Y3FxM2phMHByaTd0&utm_source=qr";
const YOUTUBE = "https://www.youtube.com/channel/UCAi-cO-560wUoA8S10tKLpg";

export const Navbar = () => {
  const { content, lang, changeLang } = useSite();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [langOpen, setLangOpen] = useState(false);
  const ui = content?.ui || {};

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const links = [
    { id: "events", label: ui.nav_events || "Eventos" },
    { id: "services", label: ui.nav_services || "Servicios" },
    { id: "about", label: ui.nav_about || "Quienes Somos" },
    { id: "origin", label: ui.nav_origin || "Origen" },
    { id: "contact", label: ui.nav_contact || "Contacto" },
  ];

  const scrollTo = (id) => {
    setOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav
      data-testid="navbar"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "bg-black/90 backdrop-blur-md border-b border-white/10" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-12 flex items-center justify-between h-20">
        <button data-testid="nav-logo" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="flex items-center">
          <img src="/media/siroco-logo.png" alt="Siroco Producciones" className="h-10 w-auto" />
        </button>

        <div className="hidden lg:flex items-center gap-10">
          {links.map((l) => (
            <button key={l.id} data-testid={`nav-${l.id}`} onClick={() => scrollTo(l.id)}
              className="text-sm uppercase tracking-[0.18em] text-white/70 hover:text-white transition-colors">
              {l.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <button data-testid="lang-toggle" onClick={() => setLangOpen((v) => !v)}
              className="flex items-center gap-2 text-sm uppercase tracking-[0.18em] text-white/80 hover:text-white transition-colors border border-white/20 px-3 py-2">
              <Globe size={15} /> {lang}
            </button>
            {langOpen && (
              <div data-testid="lang-menu" className="absolute right-0 mt-2 w-40 bg-[#0a0a0a] border border-white/15">
                {LANGS.map((l) => (
                  <button key={l.code} data-testid={`lang-option-${l.code}`}
                    onClick={() => { changeLang(l.code); setLangOpen(false); }}
                    className="w-full flex items-center justify-between px-4 py-3 text-sm text-white/80 hover:bg-[#d90429] hover:text-white transition-colors">
                    <span>{l.name}</span>
                    {lang === l.code && <Check size={14} />}
                  </button>
                ))}
              </div>
            )}
          </div>

          <a data-testid="nav-instagram" href={INSTAGRAM} target="_blank" rel="noopener noreferrer"
            className="text-white/80 hover:text-[#d90429] transition-colors">
            <Instagram size={20} />
          </a>

          <a data-testid="nav-youtube" href={YOUTUBE} target="_blank" rel="noopener noreferrer"
            className="text-white/80 hover:text-[#d90429] transition-colors">
            <Youtube size={22} />
          </a>

          <button data-testid="mobile-menu-toggle" className="lg:hidden text-white" onClick={() => setOpen((v) => !v)}>
            {open ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {open && (
        <div data-testid="mobile-menu" className="lg:hidden bg-black/95 border-t border-white/10 px-6 py-6 flex flex-col gap-5">
          {links.map((l) => (
            <button key={l.id} onClick={() => scrollTo(l.id)}
              className="text-left text-sm uppercase tracking-[0.18em] text-white/80">
              {l.label}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
};
