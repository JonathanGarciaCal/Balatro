def train_dummy(X, y):
    """Train a tiny baseline model (DummyClassifier) for smoke tests."""
    try:
        from sklearn.dummy import DummyClassifier
    except Exception:  # pragma: no cover - import error in minimal env
        raise

    clf = DummyClassifier(strategy="most_frequent")
    clf.fit(X, y)
    return clf
