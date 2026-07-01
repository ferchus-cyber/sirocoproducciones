import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "../lib/api";

const SiteContext = createContext(null);
export const useSite = () => useContext(SiteContext);

export const LANGS = [
  { code: "es", label: "ES", name: "Español" },
  { code: "en", label: "EN", name: "English" },
  { code: "de", label: "DE", name: "Deutsch" },
  { code: "fr", label: "FR", name: "Français" },
];

export const SiteProvider = ({ children }) => {
  const [lang, setLang] = useState(localStorage.getItem("siroco_lang") || "es");
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchContent = useCallback(async (l) => {
    setLoading(true);
    try {
      const { data } = await api.get(`/site`, { params: { lang: l } });
      setContent(data);
    } catch (e) {
      console.error("site fetch error", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchContent(lang); }, [lang, fetchContent]);

  const changeLang = (l) => {
    localStorage.setItem("siroco_lang", l);
    setLang(l);
  };

  return (
    <SiteContext.Provider value={{ lang, changeLang, content, loading }}>
      {children}
    </SiteContext.Provider>
  );
};
