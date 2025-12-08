import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import ConversationSimulationPage from "./pages/ConversationSimulationPage";
import EmotionAnalysisPage from "./pages/EmotionAnalysisPage";
import HomePage from "./pages/HomePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/conversation-simulation" element={<ConversationSimulationPage />} />
          <Route path="/emotion-analysis" element={<EmotionAnalysisPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;