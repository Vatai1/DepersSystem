import { useState } from "react";
import { Upload, Loader, Download } from "lucide-react";
import toast from "react-hot-toast";
import { depersonalizeFile, downloadResult } from "../api/client";
import FileDropzone from "../components/FileDropzone";
import EntityList from "../components/EntityList";
import type { DepersonalizeFileResponse } from "../api/types";
import "./FilePage.css";

type Mode = "fake" | "replace" | "mask" | "redact";

const MODE_LABELS: Record<Mode, string> = {
  fake: "Подмена",
  replace: "Замена",
  mask: "Маскирование",
  redact: "Удаление",
};

export default function FilePage() {
  const [mode, setMode] = useState<Mode>("fake");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DepersonalizeFileResponse | null>(null);
  const [file, setFile] = useState<File | null>(null);

  async function handleProcess() {
    if (!file) {
      toast.error("Выберите файл");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await depersonalizeFile(file, mode);
      setResult(res);
      toast.success(`Обработано. Найдено ${res.stats.total_entities} сущностей`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка сервера";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload() {
    if (!result) return;
    try {
      const blob = await downloadResult(result.download_url);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `depersonalized_${result.filename}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Ошибка скачивания");
    }
  }

  return (
    <div className="file-page">
      <div className="page-header">
        <Upload size={28} />
        <div>
          <h1>Деперсонализация файлов</h1>
          <p>Загрузите документ, изображение или таблицу</p>
        </div>
      </div>

      <div className="file-controls">
        <FileDropzone onFile={setFile} />
        <div className="file-actions">
          <div className="mode-select">
            {(Object.keys(MODE_LABELS) as Mode[]).map((m) => (
              <button
                key={m}
                className={`mode-btn ${mode === m ? "active" : ""}`}
                onClick={() => setMode(m)}
              >
                {MODE_LABELS[m]}
              </button>
            ))}
          </div>
          <button
            className="btn-primary"
            onClick={handleProcess}
            disabled={loading || !file}
          >
            {loading ? (
              <Loader size={16} className="spin" />
            ) : (
              <Upload size={16} />
            )}
            Обработать файл
          </button>
        </div>
      </div>

      {result && (
        <div className="file-result">
          <div className="file-result-header">
            <span>Результат: {result.filename}</span>
            <button className="btn-primary" onClick={handleDownload}>
              <Download size={16} />
              Скачать
            </button>
          </div>
          <EntityList entities={result.entities} />
        </div>
      )}
    </div>
  );
}
