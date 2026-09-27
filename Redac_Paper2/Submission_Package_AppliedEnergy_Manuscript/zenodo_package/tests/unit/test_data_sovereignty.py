"""Unit tests for DataSovereigntyProtocol module."""

from unittest.mock import MagicMock

from src.iot_security.data_sovereignty import DataSovereigntyProtocol


def _mock_config():
    return MagicMock()


class TestDataSovereigntyProtocol:
    def test_initial_state(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        assert dsp.ledger_size == 0
        assert dsp.verify_ledger_integrity()

    def test_encrypt_decrypt(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        plaintext = b"SERS spectrum data: 0.129, 0.177, 0.004"
        session = "greenhouse_001"
        cipher = dsp.encrypt_packet(plaintext, session)
        assert cipher != plaintext
        assert len(cipher) == len(plaintext)

    def test_provenance_recording(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        block = dsp.record_provenance(data_hash="a1b2c3d4", metadata={"sensor": "NPoM", "plot": 5})
        assert block["index"] == 0
        assert "block_hash" in block
        assert dsp.ledger_size == 1

    def test_ledger_integrity_multiple_blocks(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        dsp.record_provenance("hash1", {"key": "val1"})
        dsp.record_provenance("hash2", {"key": "val2"})
        dsp.record_provenance("hash3", {"key": "val3"})
        assert dsp.ledger_size == 3
        assert dsp.verify_ledger_integrity()

    def test_consent_management(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        assert not dsp.is_authorized("EU_buyer_01")
        dsp.grant_consent("EU_buyer_01")
        assert dsp.is_authorized("EU_buyer_01")
        dsp.revoke_consent("EU_buyer_01")
        assert not dsp.is_authorized("EU_buyer_01")

    def test_differential_privacy(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        original = 42.0
        private = dsp.add_differential_privacy_noise(original)
        assert private != original

    def test_get_status(self):
        dsp = DataSovereigntyProtocol(_mock_config())
        dsp.record_provenance("test_hash", {"test": "data"})
        dsp.grant_consent("researcher_01")
        status = dsp.get_status()
        assert status["ledger_size"] == 1
        assert status["ledger_intact"]
        assert "researcher_01" in status["consent_granted_parties"]
