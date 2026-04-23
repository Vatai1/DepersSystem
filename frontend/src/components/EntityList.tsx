import type { PiiEntity } from "../api/types";

const LABEL_COLORS: Record<string, string> = {
  PER: "#e17055",
  PERSON: "#e17055",
  LOC: "#00cec9",
  LOCATION: "#00cec9",
  ORG: "#6c5ce7",
  ORGANIZATION: "#6c5ce7",
  DATE: "#fdcb6e",
  PHONE: "#fd79a8",
  EMAIL: "#00b894",
  ADDRESS: "#0984e3",
  INN: "#e84393",
  SNILS: "#e84393",
  PASSPORT: "#e84393",
  CARD: "#e84393",
};

interface Props {
  entities: PiiEntity[];
  onRemove?: (index: number) => void;
}

export default function EntityList({ entities, onRemove }: Props) {
  if (entities.length === 0) {
    return (
      <div className="entity-list-empty">
        Персональные данные не обнаружены
      </div>
    );
  }

  return (
    <div className="entity-list">
      <div className="entity-list-header">
        <span>Найдено: {entities.length}</span>
      </div>
      <div className="entity-items">
        {entities.map((ent, i) => {
          const color = LABEL_COLORS[ent.label] || "#636e72";
          return (
            <div key={i} className="entity-item">
              <span className="entity-text" style={{ borderColor: color }}>
                {ent.text}
              </span>
              <span className="entity-label" style={{ background: color }}>
                {ent.label}
              </span>
              <span className="entity-score">
                {Math.round(ent.score * 100)}%
              </span>
              {onRemove && (
                <button
                  className="entity-remove"
                  onClick={() => onRemove(i)}
                  title="Удалить"
                >
                  ×
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
