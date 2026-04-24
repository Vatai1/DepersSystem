import { useState } from "react";
import { Upload, Loader, Download, ArrowRight, ArrowLeft } from "lucide-react";
import toast from "react-hot-toast";
import { depersonalizeFile, downloadResult, repersonalizeFile } from "../api/client";
import FileDropzone from "../components/FileDropzone";
import EntityList from "../components/EntityList";
import type { DepersonalizeFileResponse, RepersonalizeFileResponse } from "../api/types";
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
  const [vaultKey, setVaultKey] = useState<string | null>(null);
  const [restoring, setRestoring] = useState(false);
  const [restoredDownloadUrl, setRestoredDownloadUrl] = useState<string | null>(null);
  const [restoredFilename, setRestoredFilename] = useState<string | null>(null);

  async function handleDepersonalize() {
    if (!file) {
      toast.error("Выберите файл");
      return;
    }
    setLoading(true);
    setResult(null);
    setVaultKey(null);
    setRestoredDownloadUrl(null);
    try {
      const res = await depersonalizeFile(file, mode);
      setResult(res);
      if (res.key) {
        setVaultKey(res.key);
      }
      toast.success(`Обработано. Найдено ${res.stats.total_entities} сущностей`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка сервера";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleRepersonalize() {
    if (!vaultKey || !file) return;
    setRestoring(true);
    setRestoredDownloadUrl(null);
    setRestoredFilename(null);
    try {
      const res: RepersonalizeFileResponse = await repersonalizeFile(file, vaultKey);
      if (res.download_url) {
        setRestoredDownloadUrl(res.download_url);
        setRestoredFilename(res.download_url.split("/").pop() || null);
      }
      toast.success("Файл восстановлен");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка восстановления";
      toast.error(msg);
    } finally {
      setRestoring(false);
    }
  }

  async function handleDownload() {
    if (!result) return;
    try {
      const url = restoredDownloadUrl || result.download_url;
      const blob = await downloadResult(url);
      const objUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objUrl;
      a.download = restoredDownloadUrl
        ? restoredFilename || `restored_${result.filename}`
        : `depersonalized_${result.filename}`;
      a.click();
      URL.revokeObjectURL(objUrl);
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

      <div className="file-mode-bar">
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
      </div>

      <div className="file-workspace">
        <div className="file-panel">
          <div className="panel-toolbar">
            <span className="panel-title">Файл</span>
          </div>
          <div className="file-dropzone-area">
            <FileDropzone onFile={setFile} />
          </div>
        </div>

        <div className="action-column">
          <button
            className="action-btn action-depersonalize"
            onClick={handleDepersonalize}
            disabled={loading || !file}
            title="Деперсонализировать файл"
          >
            {loading ? (
              <Loader size={18} className="spin" />
            ) : (
              <ArrowRight size={18} />
            )}
            <span>Деперсонализация</span>
          </button>
          <button
            className="action-btn action-repersonalize"
            onClick={handleRepersonalize}
            disabled={restoring || !vaultKey || !file}
            title="Персонализировать файл (восстановить)"
          >
            {restoring ? (
              <Loader size={18} className="spin" />
            ) : (
              <ArrowLeft size={18} />
            )}
            <span>Персонализация</span>
          </button>
        </div>

        <div className="file-panel">
          <div className="panel-toolbar">
            <span className="panel-title">
              {restoredDownloadUrl ? "Восстановленный" : "Результат"}
            </span>
            {result && (
              <button className="btn-ghost" onClick={handleDownload}>
                <Download size={14} /> Скачать
              </button>
            )}
          </div>
          <div className="file-result-content">
            {result ? (
              <>
                {vaultKey && (
                  <div className="vault-key-badge">
                    Ключ: <code>{vaultKey}</code>
                  </div>
                )}
                <EntityList entities={result.entities} />
              </>
            ) : (
              <div className="file-empty">Загрузите файл и нажмите «Деперсонализация»</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
