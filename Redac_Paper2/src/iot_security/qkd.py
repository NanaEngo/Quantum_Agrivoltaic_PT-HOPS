import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    QKD_MAX_SAMPLE_SIZE,
    QKD_QBER_THRESHOLD,
    QKD_SAMPLE_DIVISOR,
    QKD_SIFTING_OVERHEAD,
)


class Bb84Protocol:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.noise_rate = config.security.qkd.channel_noise_rate
        self.key_length = config.security.qkd.key_length_bits

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
            return {"qber": 1.0, "key": None, "status": "FAILED"}

        sample_size = max(1, min(len(alice_sifted) // QKD_SAMPLE_DIVISOR, QKD_MAX_SAMPLE_SIZE))
        sample_indices = np.random.choice(len(alice_sifted), sample_size, replace=False)
        errors = np.sum(alice_sifted[sample_indices] != bob_sifted[sample_indices])
        qber = errors / sample_size

        if qber > QKD_QBER_THRESHOLD:
            return {"qber": float(qber), "key": None, "status": "FAILED_HI_NOISE_OR_EAVESDROP"}

        remaining_indices = list(set(range(len(alice_sifted))) - set(sample_indices))
        final_key = bob_sifted[remaining_indices][: self.key_length]
        return {"qber": float(qber), "key": "".join(map(str, final_key)), "status": "SUCCESS"}
