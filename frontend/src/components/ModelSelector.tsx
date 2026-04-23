import { useEffect, useState } from "react";
import { listModels, switchModel } from "../api/client";
import type { ModelListItem } from "../api/types";
import { Cpu, Loader2, Check } from "lucide-react";
import "./ModelSelector.css";

export default function ModelSelector() {
  const [models, setModels] = useState<ModelListItem[]>([]);
  const [active, setActive] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadModels();
  }, []);

  async function loadModels() {
    try {
      const res = await listModels();
      setModels(res.models);
      setActive(res.active);
    } catch {
      setError("Не удалось загрузить список моделей");
    }
  }

  async function handleSwitch(modelName: string) {
    if (modelName === active || loading) return;
    setLoading(true);
    setError("");
    try {
      const res = await switchModel(modelName);
      if (res.status === "error") {
        setError(res.status);
      } else {
        setActive(modelName);
        setModels((prev) =>
          prev.map((m) => ({ ...m, is_active: m.model_name === modelName })),
        );
      }
    } catch {
      setError("Ошибка переключения модели");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="model-selector">
      <div className="model-selector-header">
        <Cpu size={16} />
        <span>ML Модель</span>
      </div>
      <div className="model-list">
        {models.map((m) => (
          <button
            key={m.model_name}
            className={`model-item ${m.model_name === active ? "active" : ""}`}
            onClick={() => handleSwitch(m.model_name)}
            disabled={loading}
          >
            <div className="model-item-top">
              <span className="model-name">{m.display_name}</span>
              {m.model_name === active && (
                <Check size={14} className="model-check" />
              )}
              {loading && m.model_name !== active && (
                <Loader2 size={14} className="model-spinner" />
              )}
            </div>
            <span className="model-desc">{m.description}</span>
            <span className="model-size">{m.size}</span>
          </button>
        ))}
      </div>
      {error && <div className="model-error">{error}</div>}
    </div>
  );
}
