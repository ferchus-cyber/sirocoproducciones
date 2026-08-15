import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Hero } from "../sections/Hero";
import { Events } from "../sections/Events";
import { Services } from "../sections/Services";
import { About } from "../sections/About";
import { Origin } from "../sections/Origin";
import { Contact } from "../sections/Contact";
import { useSite } from "../context/SiteContext";
import { Loader2, AlertTriangle } from "lucide-react";

export default function Home() {
  const { content, loading, error, retry } = useSite();

  return (
    <div className="grain relative">
      <Navbar />
      {loading && !content ? (
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="animate-spin text-[#d90429]" size={40} />
        </div>
      ) : error && !content ? (
        <div data-testid="site-error" className="min-h-screen flex flex-col items-center justify-center text-center px-6">
          <AlertTriangle className="text-[#d90429] mb-6" size={44} />
          <h2 className="font-display text-3xl mb-3">No hemos podido cargar el contenido</h2>
          <p className="text-white/60 mb-8">Comprueba tu conexión e inténtalo de nuevo.</p>
          <button data-testid="site-retry" onClick={retry} className="btn-siroco">Reintentar</button>
        </div>
      ) : (
        <>
          <Hero />
          <Events />
          <Services />
          <About />
          <Origin />
          <Contact />
          <Footer />
        </>
      )}
    </div>
  );
}
