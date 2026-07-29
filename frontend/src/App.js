import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { Layout } from "./components/Layout";
import Landing from "./pages/Landing";
import ConceptPaper from "./pages/ConceptPaper";
import Sandbox from "./pages/Sandbox";
import Compliance from "./pages/Compliance";
import TrustPipeline from "./pages/TrustPipeline";
import Federation from "./pages/Federation";
import DeveloperHub from "./pages/DeveloperHub";
import "./i18n";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: "#0a0f19",
            color: "#e5e7eb",
            border: "1px solid rgba(245,158,11,0.3)",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "12px",
          },
        }}
      />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/paper" element={<ConceptPaper />} />
          <Route path="/paper/:slug" element={<ConceptPaper />} />
          <Route path="/sandbox" element={<Sandbox />} />
          <Route path="/compliance" element={<Compliance />} />
          <Route path="/trust" element={<TrustPipeline />} />
          <Route path="/federation" element={<Federation />} />
          <Route path="/hub" element={<DeveloperHub />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
