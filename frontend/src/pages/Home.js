import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { Hero } from "../sections/Hero";
import { Events } from "../sections/Events";
import { Services } from "../sections/Services";
import { About } from "../sections/About";
import { Origin } from "../sections/Origin";
import { Contact } from "../sections/Contact";
import { useSite } from "../context/SiteContext";
import { Loader2 } from "lucide-react";

export default function Home() {
  const { content, loading } = useSite();

  return (
    <div className="grain relative">
      <Navbar />
      {loading && !content ? (
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="animate-spin text-[#d90429]" size={40} />
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
