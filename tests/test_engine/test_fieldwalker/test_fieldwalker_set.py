from montydb.engine.core import FieldWalker


def test_fieldwalker_value_set_1():
    # single value
    doc = {"a": 1}
    path = "a"
    value = 10

    fieldwalker = FieldWalker(doc)
    with fieldwalker.go(path):
        fieldwalker.set(value)
    assert doc == {"a": 10}


def test_fieldwalker_value_set_2():
    doc = {"a": {"b": 1}}
    path = "a.b"
    value = 10

    fieldwalker = FieldWalker(doc)
    with fieldwalker.go(path):
        fieldwalker.set(value)
    assert doc == {"a": {"b": 10}}


def test_fieldwalker_value_set_3():
    doc = {"a": [1, 2, 3]}
    path = "a.1"
    value = 20

    fieldwalker = FieldWalker(doc)
    with fieldwalker.go(path):
        fieldwalker.set(value)
    assert doc == {"a": [1, 20, 3]}


def test_fieldwalker_value_set_4():
    doc = {"a": [1, 2, 3]}
    path = "a.5"
    value = 9

    fieldwalker = FieldWalker(doc)
    with fieldwalker.go(path):
        fieldwalker.set(value)
        assert doc == {"a": [1, 2, 3]}
    assert doc == {"a": [1, 2, 3, None, None, 9]}


def test_fieldwalker_value_set_5():
    doc = {}

    fieldwalker = FieldWalker(doc)
    with fieldwalker:
        fieldwalker.go("a.b")
        fieldwalker.set(10)
        fieldwalker.go("c")
        fieldwalker.set(99)
        assert doc == {}
    assert doc == {"a": {"b": 10}, "c": 99}


def test_fieldwalker_value_set_6():
    doc = {"a": [1]}
    path = "a.2.b"
    value = 20

    fieldwalker = FieldWalker(doc)
    with fieldwalker.go(path):
        fieldwalker.set(value)
    assert doc == {"a": [1, None, {"b": 20}]}
