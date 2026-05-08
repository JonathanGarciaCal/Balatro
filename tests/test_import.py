def test_import_balatro():
    import importlib

    balatro = importlib.import_module("balatro")
    assert hasattr(balatro, "__version__")
    assert hasattr(balatro, "data")
