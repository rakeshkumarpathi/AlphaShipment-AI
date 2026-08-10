import pandas as pd

from exception_detection import detect_exception


def analyze_shipments(df):
    results = df.apply(
        detect_exception,
        axis=1,
        result_type="expand"
    )

    results.columns = [
        "exception",
        "exception_type",
        "severity"
    ]

    analyzed_df = pd.concat(
        [df, results],
        axis=1
    )

    return analyzed_df