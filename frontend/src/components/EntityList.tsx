import { useState } from "react";
import type { PiiEntity } from "../api/types";
import { ChevronDown, ChevronRight } from "lucide-react";
import "./EntityList.css";

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
  IP: "#636e72",
};

const LABEL_NAMES: Record<string, string> = {
  PER: "ФИО",
  PERSON: "ФИО",
  LOC: "Локация",
  LOCATION: "Локация",
  ORG: "Организация",
  ORGANIZATION: "Организация",
  DATE: "Дата",
  PHONE: "Телефон",
  EMAIL: "Email",
  ADDRESS: "Адрес",
  INN: "ИНН",
  SNILS: "СНИЛС",
  PASSPORT: "Паспорт",
  CARD: "Карта",
  IP: "IP-адрес",
};

interface Props {
  entities: PiiEntity[];
  onRemove?: (index: number) => void;
}

function groupByLabel(entities: PiiEntity[]): Map<string, PiiEntity[]> {
  const map = new Map<string, PiiEntity[]>();
  for (const e of entities) {
    const list = map.get(e.label) || [];
    list.push(e);
    map.set(e.label, list);
  }
  return map;
}

export default function EntityList({ entities, onRemove }: Props) {
  const [openGroups, setOpenGroups] = useState<Set<string>>(new Set());

  if (entities.length === 0) {
    return (
      <div className="entity-list-empty">
        Персональные данные не обнаружены
      </div>
    );
  }

  const groups = groupByLabel(entities);

  function toggle(label: string) {
    setOpenGroups((prev) => {
      const next = new Set(prev);
      if (next.has(label)) {
        next.delete(label);
      } else {
        next.add(label);
      }
      return next;
    });
  }

  return (
    <div className="entity-list">
      <div className="entity-list-header">
        <span>Найдено: {entities.length}</span>
      </div>
      <div className="entity-groups">
        {[...groups.entries()].map(([label, items]) => {
          const color = LABEL_COLORS[label] || "#636e72";
          const name = LABEL_NAMES[label] || label;
          const isOpen = openGroups.has(label);
          return (
            <div key={label} className="entity-group">
              <button
                className="entity-group-header"
                onClick={() => toggle(label)}
              >
                {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                <span className="entity-group-label" style={{ background: color }}>
                  {name}
                </span>
                <span className="entity-group-count">{items.length}</span>
              </button>
              {isOpen && (
                <div className="entity-group-items">
                  {items.map((ent, i) => (
                    <div key={i} className="entity-item">
                      <span className="entity-text" style={{ borderColor: color }}>
                        {ent.text}
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
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
