import { Instagram, Phone, Mail, MapPin } from "lucide-react";
import { useSite } from "../context/SiteContext";

const INSTAGRAM = "https://www.instagram.com/sirocoproducciones?igsh=Y3FxM2phMHByaTd0&utm_source=qr";

export const Footer = () => {
  const { content } = useSite();
  const c = content?.contact || {};
  const ui = content?.ui || {};
  return (
    <footer data-testid="footer" className="border-t border-white/10 bg-black py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 grid md:grid-cols-3 gap-12">
        <div>
          <img src="/media/siroco-logo.png" alt="Siroco Producciones" className="h-14 w-auto mb-4" />
          <p className="text-white/50 text-sm leading-relaxed">Producción artística y espectáculos musicales.</p>
          <a data-testid="footer-instagram" href={INSTAGRAM} target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-6 text-white/70 hover:text-[#d90429] transition-colors text-sm">
            <Instagram size={18} /> @sirocoproducciones
          </a>
        </div>
        <div className="space-y-3 text-sm text-white/60">
          <div className="section-label mb-4">{c.title || "Contacto"}</div>
          <p className="flex items-center gap-3"><Phone size={15} className="text-[#d90429]" /> {c.phone}</p>
          <p className="flex items-center gap-3"><Mail size={15} className="text-[#d90429]" /> {c.email}</p>
          <p className="flex items-center gap-3"><MapPin size={15} className="text-[#d90429]" /> {c.location}</p>
        </div>
        <div className="flex md:justify-end items-start">
          <img src="/media/album/siroco-paco-de-lucia.jpg" alt="Siroco - Paco de Lucía"
            className="w-28 h-28 object-cover border border-white/10" />
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-6 lg:px-12 mt-16 pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between gap-4 text-xs text-white/40 uppercase tracking-[0.15em]">
        <span>© {new Date().getFullYear()} Siroco Producciones. {ui.footer_rights || "Todos los derechos reservados"}.</span>
        <a href="/admin" data-testid="footer-admin-link" className="hover:text-white/70 transition-colors">Admin</a>
      </div>
    </footer>
  );
};
