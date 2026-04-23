import { useState, useEffect } from "react";
import { History as HistoryIcon, Trash2 } from "lucide-react";
import "./HistoryPage.css";

interface HistoryEntry {
  id: string;
  timestamp: string;
  type: "text" | "file";
  filename?: string;
  entities_count: number;
  mode: string;
}

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    const raw = localStorage.getItem("depers-history");
    if (raw) {
      try {
        setEntries(JSON.parse(raw));
      } catch {
        /* ignore */
      }
    }
  }, []);

  function handleClear() {
    localStorage.removeItem("depers-history");
    setEntries([]);
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <HistoryIcon size={28} />
        <div>
          <h1>История обработок</h1>
          <p>Ранее обработанные тексты и файлы</p>
        </div>
        {entries.length > 0 && (
          <button className="btn-clear" onClick={handleClear}>
            <Trash2 size={14} />
            Очистить
          </button>
        )}
      </div>

      {entries.length === 0 ? (
        <div className="history-empty">История пуста</div>
      ) : (
        <div className="history-list">
          {entries.map((entry) => (
            <div key={entry.id} className="history-item">
              <div className="history-item-info">
                <span className="history-type">
                  {entry.type === "file" ? "📄" : "📝"}
                </span>
                <span className="history-name">
                  {entry.filename || "Текст"}
                </span>
                <span className="history-meta">
                  {entry.entities_count} сущностей · {entry.mode}
                </span>
              </div>
              <span className="history-time">
                {new Date(entry.timestamp).toLocaleString("ru-RU")}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
