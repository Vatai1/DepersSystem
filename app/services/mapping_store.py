import uuid
from datetime import datetime, timedelta, timezone


class MappingStore:
    TTL = timedelta(hours=24)

    def __init__(self) -> None:
        self._vaults: dict[str, dict[str, str]] = {}
        self._timestamps: dict[str, datetime] = {}
        self._entity_counts: dict[str, int] = {}

    def _cleanup(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [k for k, ts in self._timestamps.items() if now - ts > self.TTL]
        for k in expired:
            del self._vaults[k]
            del self._timestamps[k]
            del self._entity_counts[k]

    def save(self, reverse_mapping: dict[str, str]) -> str:
        self._cleanup()
        key = uuid.uuid4().hex[:12]
        self._vaults[key] = dict(reverse_mapping)
        self._timestamps[key] = datetime.now(timezone.utc)
        self._entity_counts[key] = len(reverse_mapping)
        return key

    def get(self, key: str) -> dict[str, str] | None:
        self._cleanup()
        ts = self._timestamps.get(key)
        if ts is None:
            return None
        if datetime.now(timezone.utc) - ts > self.TTL:
            self.delete(key)
            return None
        return dict(self._vaults.get(key, {}))

    def delete(self, key: str) -> bool:
        if key in self._vaults:
            del self._vaults[key]
            del self._timestamps[key]
            del self._entity_counts[key]
            return True
        return False

    def list_keys(self) -> list[dict]:
        self._cleanup()
        result = []
        for key in self._vaults:
            result.append(
                {
                    "key": key,
                    "entity_count": self._entity_counts.get(key, 0),
                    "created_at": self._timestamps[key].isoformat(),
                }
            )
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return result

    def repersonalize_text(self, text: str, key: str) -> str | None:
        mapping = self.get(key)
        if mapping is None:
            return None
        for fake in sorted(mapping, key=len, reverse=True):
            original = mapping[fake]
            text = text.replace(fake, original)
        return text


mapping_store = MappingStore()
