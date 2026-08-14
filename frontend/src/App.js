import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import { SiteProvider } from "@/context/SiteContext";
import { WhatsAppButton } from "@/components/WhatsAppButton";
import Home from "@/pages/Home";
import Admin from "@/pages/Admin";

function App() {
  return (
    <div className="App">
      <Toaster theme="dark" position="top-right" richColors />
      <BrowserRouter>
        <SiteProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
          <WhatsAppButton />
        </SiteProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
