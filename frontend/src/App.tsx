import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import TextPage from "./pages/TextPage";
import FilePage from "./pages/FilePage";
import HistoryPage from "./pages/HistoryPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<TextPage />} />
        <Route path="/files" element={<FilePage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}
