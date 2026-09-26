import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    QKD_MAX_SAMPLE_SIZE,
    QKD_MIN_SAMPLE_SIZE,
    QKD_SAMPLE_DIVISOR,
    QKD_SIFTING_OVERHEAD,
)
from ..logging_config import get_logger

logger = get_logger("qkd")


def wilson_upper_bound(errors: int, n: int, z: float = 1.96) -> float:
    """Wilson score upper confidence bound on a binomial proportion.

    Used for the QBER abort decision (SI S6): the session is rejected when the
    *upper bound* of the sampled QBER exceeds the Shor-Preskill threshold, not
    when the raw point estimate does.
    """
    if n <= 0:
        return 1.0
    p = errors / n
    z2 = z * z
    centre = p + z2 / (2.0 * n)
    margin = z * np.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return float((centre + margin) / (1.0 + z2 / n))


class SecurityThresholdExceeded(RuntimeError):
    """
    V5: Raised when BB84 QBER exceeds the Shor-Preskill unconditional security
    threshold (default 11%). Triggers automatic shutdown of QKD-protected
    irrigation commands to prevent data injection under eavesdropping.
    """


class Bb84Protocol:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.noise_rate = config.security.qkd.channel_noise_rate
        self.key_length = config.security.qkd.key_length_bits
        # V5: Shor-Preskill threshold from config (replaces hardcoded constant)
        self.security_threshold = config.security.qkd.security_threshold
        self.channel_type = config.security.qkd.channel_type

    def simulate_key_exchange(self, seed: int = 42) -> dict:
        np.random.seed(seed)
        n_raw = self.key_length * QKD_SIFTING_OVERHEAD
        alice_bits = np.random.randint(0, 2, n_raw)
        alice_bases = np.random.randint(0, 2, n_raw)
        bob_bases = np.random.randint(0, 2, n_raw)

        bob_bits = []
        for i in range(n_raw):
            received_bit = (
                1 - alice_bits[i] if np.random.rand() < self.noise_rate else alice_bits[i]
            )
            bob_bits.append(
                received_bit if alice_bases[i] == bob_bases[i] else np.random.randint(0, 2)
            )

        matching_indices = np.where(alice_bases == bob_bases)[0]
        alice_sifted = alice_bits[matching_indices]
        bob_sifted = np.array(bob_bits)[matching_indices]

        if len(alice_sifted) == 0:
            return {"qber": 1.0, "qber_wilson_ub": 1.0, "key": None, "status": "FAILED"}

        # SI S6: parameter estimation discloses >= QKD_MIN_SAMPLE_SIZE bits
        # (>= 128 at N = 256, i.e. f_sample >= 0.5), never more than
        # QKD_MAX_SAMPLE_SIZE nor more than the sifted key itself.
        sample_size = max(
            1,
            min(
                max(len(alice_sifted) // QKD_SAMPLE_DIVISOR, QKD_MIN_SAMPLE_SIZE),
                QKD_MAX_SAMPLE_SIZE,
                len(alice_sifted),
            ),
        )
        sample_indices = np.random.choice(len(alice_sifted), sample_size, replace=False)
        errors = int(np.sum(alice_sifted[sample_indices] != bob_sifted[sample_indices]))
        qber = errors / sample_size
        qber_ub = wilson_upper_bound(errors, sample_size)

        if qber_ub > self.security_threshold:
            logger.critical(
                "BB84 QBER=%.4f (Wilson 95%% UB %.4f) exceeds Shor-Preskill threshold "
                "%.4f on %s channel — irrigation HALTED",
                qber,
                qber_ub,
                self.security_threshold,
                self.channel_type,
            )
            raise SecurityThresholdExceeded(
                f"BB84 QBER={qber:.4f} (Wilson 95% upper bound {qber_ub:.4f}) exceeds "
                f"Shor-Preskill threshold {self.security_threshold:.4f} on "
                f"{self.channel_type} channel. Irrigation command relay halted."
            )

        remaining_indices = list(set(range(len(alice_sifted))) - set(sample_indices))
        final_key = bob_sifted[remaining_indices][: self.key_length]
        logger.info(
            "BB84 QKD: QBER=%.4f, key_length=%d, channel=%s, status=SUCCESS",
            qber,
            len(final_key),
            self.channel_type,
        )
        return {
            "qber": float(qber),
            "qber_wilson_ub": float(qber_ub),
            "key": "".join(map(str, final_key)),
            "status": "SUCCESS",
            "channel_type": self.channel_type,
        }
