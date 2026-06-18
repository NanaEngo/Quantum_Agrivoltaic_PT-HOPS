import numpy as np
from ..config_loader import ConfigModel

# BB84 protocol constants
QBER_THRESHOLD = 0.11  # Maximum tolerable Quantum Bit Error Rate (BB84 standard)
# Above this threshold, key generation is aborted to prevent eavesdropping


class Bb84Protocol:
    """
    Simulates a lightweight BB84 Quantum Key Distribution (QKD) protocol
    to secure telemetry channels between agricultural IoT nodes and the cloud server.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.noise_rate = config.security.qkd.channel_noise_rate
        self.key_length = config.security.qkd.key_length_bits

    def simulate_key_exchange(self, seed: int = 42) -> dict:
        """
        Simulates the polarization state preparation, transmission over noisy channel,
        sifting, and QBER estimation phases of BB84.
        Returns the QBER rate and the generated symmetric key (if QBER <= 11%).
        """
        np.random.seed(seed)

        # 1. Alice prepares random bits and bases (+ or x)
        alice_bits = np.random.randint(
            0, 2, self.key_length * 4
        )  # Oversample to ensure enough bits after sifting
        alice_bases = np.random.randint(
            0, 2, self.key_length * 4
        )  # 0 for rectilinear (+), 1 for diagonal (x)

        # 2. Transmission through channel with noise
        bob_bases = np.random.randint(0, 2, self.key_length * 4)
        bob_bits = []

        for i in range(len(alice_bits)):
            # Noise can flip polarization with noise_rate probability
            if np.random.rand() < self.noise_rate:
                received_bit = 1 - alice_bits[i]
            else:
                received_bit = alice_bits[i]

            # If bases match, Bob measures correctly
            if alice_bases[i] == bob_bases[i]:
                bob_bits.append(received_bit)
            else:
                # Disagreement yields random bit measurement
                bob_bits.append(np.random.randint(0, 2))

        # 3. Sifting: keep bits where bases matched
        matching_indices = np.where(alice_bases == bob_bases)[0]
        alice_sifted = alice_bits[matching_indices]
        bob_sifted = np.array(bob_bits)[matching_indices]

        if len(alice_sifted) == 0:
            return {"qber": 1.0, "key": None, "status": "FAILED"}

        # 4. Estimate Quantum Bit Error Rate (QBER) on sample fraction
        # Guard against division by zero when too few sifted bits remain
        sample_size = max(1, min(len(alice_sifted) // 4, 50))
        sample_indices = np.random.choice(len(alice_sifted), sample_size, replace=False)

        errors = np.sum(alice_sifted[sample_indices] != bob_sifted[sample_indices])
        qber = errors / sample_size if sample_size > 0 else 0.0

        # BB84 threshold: if QBER > 11%, abort key due to potential eavesdropping/noise
        if qber > QBER_THRESHOLD:
            return {
                "qber": float(qber),
                "key": None,
                "status": "FAILED_HI_NOISE_OR_EAVESDROP",  # qber exceeds limit
            }

        # Standard key extraction (taking first key_length bits of remaining sifted bits)
        remaining_indices = list(set(range(len(alice_sifted))) - set(sample_indices))
        final_key = bob_sifted[remaining_indices][: self.key_length]

        key_str = "".join(map(str, final_key))

        return {"qber": float(qber), "key": key_str, "status": "SUCCESS"}
