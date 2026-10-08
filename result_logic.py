def predict_result(internal_marks, attendance):
    """Return PASS only when marks are at least 40 and attendance is at least 75%."""
    if internal_marks >= 40 and attendance >= 75:
        return "PASS"
    return "FAIL"


if __name__ == "__main__":
    print(predict_result(70, 85))
