import hashlib
import time as _time

import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("data_sovereignty")

DIFFERENTIAL_PRIVACY_EPSILON = 2.0
PROVENANCE_LEDGER_MAX_BLOCKS = 10000

local_time = _time


class DataSovereigntyProtocol:
    def __init__(self, config: ConfigModel):
        self.config = config
        self._cooperative_key = hashlib.sha256(b"cooperative_root_key").digest()
        self._ledger: list[dict] = []
        self._consent_granted: set[str] = set()

    def _derive_session_key(self, session_id: str) -> bytes:
        seed = session_id.encode() + self._cooperative_key
        return hashlib.sha256(seed).digest()

    def encrypt_packet(self, data_bytes: bytes, session_id: str) -> bytes:
        key = self._derive_session_key(session_id)
        result = bytearray()
        for i, b in enumerate(data_bytes):
            result.append(b ^ key[i % len(key)])
        return bytes(result)

    def record_provenance(self, data_hash: str, metadata: dict) -> dict:
        previous_hash = self._ledger[-1]["block_hash"] if self._ledger else "0" * 64
        block_content = previous_hash + data_hash + str(metadata) + str(local_time.time())
        block_hash = hashlib.sha256(block_content.encode()).hexdigest()
        block = {
            "index": len(self._ledger),
            "previous_hash": previous_hash,
            "data_hash": data_hash,
            "metadata": metadata,
            "timestamp": local_time.time(),
            "block_hash": block_hash,
        }
        self._ledger.append(block)
        logger.info(
            "Provenance block #%d: data_hash=%s…, metadata=%s",
            block["index"],
            data_hash[:12],
            metadata,
        )
        return block

    @property
    def ledger_size(self) -> int:
        return len(self._ledger)

    def verify_ledger_integrity(self) -> bool:
        for i in range(1, len(self._ledger)):
            expected_prev = self._ledger[i - 1]["block_hash"]
            if self._ledger[i]["previous_hash"] != expected_prev:
                logger.error("Ledger integrity FAILED at block %d", self._ledger[i]["index"])
                return False
        return True

    def add_differential_privacy_noise(self, value: float, sensitivity: float = 1.0) -> float:
        scale = sensitivity / DIFFERENTIAL_PRIVACY_EPSILON
        laplace_noise = np.random.laplace(0.0, scale)
        return value + laplace_noise

    def grant_consent(self, third_party_id: str) -> None:
        self._consent_granted.add(third_party_id)
        logger.info("Consent granted to: %s", third_party_id)

    def revoke_consent(self, third_party_id: str) -> None:
        self._consent_granted.discard(third_party_id)
        logger.info("Consent revoked for: %s", third_party_id)

    def is_authorized(self, third_party_id: str) -> bool:
        return third_party_id in self._consent_granted

    def get_status(self) -> dict:
        return {
            "ledger_size": len(self._ledger),
            "ledger_intact": self.verify_ledger_integrity(),
            "consent_granted_parties": sorted(self._consent_granted),
            "privacy_epsilon": DIFFERENTIAL_PRIVACY_EPSILON,
        }
