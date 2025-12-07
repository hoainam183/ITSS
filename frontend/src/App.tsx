import { BrowserRouter, Routes, Route } from "react-router-dom";
import EmotionAnalysisPage from "./pages/EmotionAnalysisPage";
import CommunityBoardPage from "./pages/CommunityBoardPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Trang mặc định */}
        <Route path="/" element={<EmotionAnalysisPage />} />

        {/* Trang phân tích cảm xúc */}
        <Route
          path="/message-analysis"
          element={<EmotionAnalysisPage />}
        />

        {/* Trang cộng đồng */}
        <Route
          path="/community"
          element={<CommunityBoardPage />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
