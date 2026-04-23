import { useState } from "react";
import { Shield, Loader } from "lucide-react";
import toast from "react-hot-toast";
import { depersonalizeText } from "../api/client";
import EntityList from "../components/EntityList";
import type { DepersonalizeTextResponse } from "../api/types";
import "./TextPage.css";

const SAMPLE =
  "Пациент Иванов Иван Иванович, born 15.03.1985, проживает по адресу г. Москва, ул. Ленина, д. 10, кв. 5. Телефон: +7 (999) 123-45-67, email: ivanov@mail.ru. Паспорт: 4510 123456, ИНН: 7712345678, СНИЛС: 123-456-789 01.";

type Mode = "fake" | "replace" | "mask" | "redact";

const MODE_LABELS: Record<Mode, string> = {
  fake: "Подмена",
  replace: "Замена",
  mask: "Маскирование",
  redact: "Удаление",
};

export default function TextPage() {
  const [text, setText] = useState(SAMPLE);
  const [mode, setMode] = useState<Mode>("fake");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DepersonalizeTextResponse | null>(null);

  async function handleProcess() {
    if (!text.trim()) {
      toast.error("Введите текст");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await depersonalizeText({ text, mode });
      setResult(res);
      toast.success(`Найдено ${res.stats.total_entities} сущностей`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка сервера";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="text-page">
      <div className="page-header">
        <Shield size={28} />
        <div>
          <h1>Деперсонализация текста</h1>
          <p>Вставьте текст — ИИ найдёт и заменит персональные данные</p>
        </div>
      </div>

      <div className="text-grid">
        <div className="text-panel">
          <div className="panel-toolbar">
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
              disabled={loading}
            >
              {loading ? (
                <Loader size={16} className="spin" />
              ) : (
                <Shield size={16} />
              )}
              Обработать
            </button>
          </div>
          <textarea
            className="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Введите или вставьте текст..."
          />
        </div>

        <div className="text-panel">
          <div className="panel-toolbar">
            <span className="panel-title">Результат</span>
            {result && (
              <button
                className="btn-secondary"
                onClick={() => {
                  navigator.clipboard.writeText(result.processed_text);
                  toast.success("Скопировано");
                }}
              >
                Копировать
              </button>
            )}
          </div>
          <div className="text-output">
            {result ? result.processed_text : "Результат появится здесь..."}
          </div>
        </div>
      </div>

      {result && <EntityList entities={result.entities} />}
    </div>
  );
}
