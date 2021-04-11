from typing import List


class FingerprintStatusInterface:
    @classmethod
    def on_error(cls) -> None:
        pass

    @classmethod
    def on_quality(cls, accepted: bool, need: int, got: int) -> None:
        pass

    @classmethod
    def on_classification(cls, accepted: bool, classification: str, confidence_need: float, confidence_got: float) -> None:
        pass

    @classmethod
    def on_scoring(cls, accepted: bool, need: int, got: int) -> None:
        pass

    @classmethod
    def on_scoring_self(cls, accepted: bool, need: int, got: int) -> None:
        pass

    @classmethod
    def on_enrollment_result(cls, success: bool, bozorth3_averages: List[float]) -> None:
        pass

    @classmethod
    def on_verification_result(cls, verified: bool) -> None:
        pass

    @classmethod
    def on_identification_result(cls, match: bool, username: str = None) -> None:
        pass
