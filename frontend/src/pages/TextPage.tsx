import { useState } from "react";
import { Shield, Loader, ArrowRight, ArrowLeft } from "lucide-react";
import toast from "react-hot-toast";
import { depersonalizeText, repersonalizeText } from "../api/client";
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
  const [restoredText, setRestoredText] = useState<string | null>(null);
  const [restoring, setRestoring] = useState(false);
  const [vaultKey, setVaultKey] = useState<string | null>(null);

  async function handleDepersonalize() {
    if (!text.trim()) {
      toast.error("Введите текст");
      return;
    }
    setLoading(true);
    setResult(null);
    setVaultKey(null);
    setRestoredText(null);
    try {
      const res = await depersonalizeText({ text, mode });
      setResult(res);
      if (res.key) {
        setVaultKey(res.key);
      }
      toast.success(`Найдено ${res.stats.total_entities} сущностей`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка сервера";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleRepersonalize() {
    if (!vaultKey || !result) return;
    setRestoring(true);
    setRestoredText(null);
    try {
      const res = await repersonalizeText(result.processed_text, vaultKey);
      setRestoredText(res.original_text);
      toast.success("Текст восстановлен");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка восстановления";
      toast.error(msg);
    } finally {
      setRestoring(false);
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

      <div className="mode-bar">
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

      <div className="text-workspace">
        <div className="text-panel">
          <div className="panel-toolbar">
            <span className="panel-title">Исходный текст</span>
            {text !== SAMPLE && (
              <button className="btn-ghost" onClick={() => setText(SAMPLE)}>
                Сбросить
              </button>
            )}
          </div>
          <textarea
            className="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Введите или вставьте текст..."
          />
        </div>

        <div className="action-column">
          <button
            className="action-btn action-depersonalize"
            onClick={handleDepersonalize}
            disabled={loading || !text.trim()}
            title="Деперсонализировать"
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
            disabled={restoring || !vaultKey || !result}
            title="Персонализировать (восстановить)"
          >
            {restoring ? (
              <Loader size={18} className="spin" />
            ) : (
              <ArrowLeft size={18} />
            )}
            <span>Персонализация</span>
          </button>
        </div>

        <div className="text-panel">
          <div className="panel-toolbar">
            <span className="panel-title">Результат</span>
            {result && (
              <button
                className="btn-ghost"
                onClick={() => {
                  navigator.clipboard.writeText(
                    restoredText ?? result.processed_text,
                  );
                  toast.success("Скопировано");
                }}
              >
                Копировать
              </button>
            )}
          </div>
          <div className="text-output">
            {restoredText !== null
              ? restoredText
              : result
                ? result.processed_text
                : "Результат появится здесь..."}
          </div>
          {vaultKey && (
            <div className="vault-key-badge">
              Ключ: <code>{vaultKey}</code>
            </div>
          )}
        </div>
      </div>

      {result && <EntityList entities={result.entities} />}
    </div>
  );
}
