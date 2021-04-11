from fingerprint_status_interface import FingerprintStatusInterface
from typing import List


class FingerprintStatus(FingerprintStatusInterface):
    @classmethod
    def on_quality(cls, accepted: bool, need: int, got: int) -> None:
        if accepted:
            print("Quality %d is %d or better" % (got, need))
        else:
            print("Quality %d must be %d or better" % (got, need))

    @classmethod
    def on_classification(cls, accepted: bool, classification: str, confidence_need: float, confidence_got: float) -> None:
        if accepted:
            print("Classification %s with confidence %d%% is %d%% or better" %
                  (classification, int(confidence_got * 100), int(confidence_need * 100)))
        else:
            print("Classification %s with confidence %d%% is lower than %d%%" %
                  (classification, int(confidence_got * 100), int(confidence_need * 100)))

    @classmethod
    def on_scoring(cls, accepted: bool, need: int, got: int) -> None:
        if accepted:
            print("Bozorth3 score %d is %d or better" % (got, need))
        else:
            print("Bozorth3 score %d is lower than %d" % (got, need))

    @classmethod
    def on_scoring_self(cls, accepted: bool, need: int, got: int) -> None:
        if accepted:
            print("Bozorth3 self-score %d is %d or better" % (got, need))
        else:
            print("Bozorth3 self-score %d is lower than %d" % (got, need))

    @classmethod
    def on_enrollment_update(cls, current: int, required: int):
        print("Obtained %d/%d enrollment template candidates" % (current, required))

    @classmethod
    def on_verification_result(cls, verified: bool) -> None:
        if verified:
            print("User verified!")
        else:
            print("User not verified!")

    @classmethod
    def on_identification_result(cls, match: bool, username: str = None) -> None:
        if match:
            print("User identified: %s" % username)
        else:
            print("User not verified!")

    @classmethod
    def on_enrollment_result(cls, success: bool, bozorth3_averages: List[float]) -> None:
        if success:
            print("User successfully enrolled. Average round-robin bozorth3 scores:")
            print(bozorth3_averages)
        else:
            print("This should never happen")
