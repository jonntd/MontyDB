
import os
import pytest

from montydb.utils import monty_dump, monty_load, MontyList

from bson import BSON
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
from bson.min_key import MinKey
from bson.max_key import MaxKey
from bson.int64 import Int64
from bson.decimal128 import Decimal128
from bson.binary import Binary
from bson.regex import Regex
from bson.code import Code


DOCUMENTS = [
    {"a": [False, True]},
    {"a": None},
    {"a": "appple"},
    {"a": [{"s": 5.5}]},
    {"a": {"s": [Int64(9)]}},
    {"a": Decimal128("4.5")},
    {"a": Binary(b"0")},
    {"a": Regex("^b")},
    {"a": Code("x", {"m": 0})},
    {"a": MinKey()},
    {"a": MaxKey()},
    {"a": Timestamp(0, 1)},
    {"a": ObjectId(b"000000000000")},
]

SERIALIZED = """
{"a": [false, true]}
{"a": null}
{"a": "appple"}
{"a": [{"s": 5.5}]}
{"a": {"s": [9]}}
{"a": {"$numberDecimal": "4.5"}}
{"a": {"$binary": {"base64": "MA==", "subType": "00"}}}
{"a": {"$regularExpression": {"pattern": "^b", "options": ""}}}
{"a": {"$code": "x", "$scope": {"m": 0}}}
{"a": {"$minKey": 1}}
{"a": {"$maxKey": 1}}
{"a": {"$timestamp": {"t": 0, "i": 1}}}
{"a": {"$oid": "303030303030303030303030"}}
"""


def test_utils_monty_dump(tmp_monty_repo):
    tmp_dump = os.path.join(tmp_monty_repo, "test_mkdirs", "dumped.json")
    monty_dump(tmp_dump, DOCUMENTS)

    with open(tmp_dump, "r") as dump:
        data = dump.read()
        assert data == SERIALIZED.strip()


def test_utils_monty_dump_with_existed_dir(tmp_monty_repo):
    tmp_dump = os.path.join(tmp_monty_repo, "existed_dir", "dumped.json")
    if not os.path.isdir(os.path.dirname(tmp_dump)):
        os.makedirs(os.path.dirname(tmp_dump))
    monty_dump(tmp_dump, DOCUMENTS)

    with open(tmp_dump, "r") as dump:
        data = dump.read()
        assert data == SERIALIZED.strip()


def test_utils_monty_load(tmp_monty_repo):
    tmp_dump = os.path.join(tmp_monty_repo, "dumped.json")
    if not os.path.isdir(tmp_monty_repo):
        os.makedirs(tmp_monty_repo)
    with open(tmp_dump, "w") as dump:
        dump.write(SERIALIZED.strip())

    docs = monty_load(tmp_dump)
    for i, doc in enumerate(docs):
        assert doc == BSON.encode(DOCUMENTS[i]).decode()


def test_utils_monty_dump_err(tmp_monty_repo):
    with pytest.raises(TypeError):
        monty_dump("tmp.file", {"some": "doc"})


def test_MontyList_find():
    mt = MontyList([1, 4, 3, {"a": 5}, {"a": 4}])
    mt_find = mt.find({"a": {"$exists": 1}})
    assert len(mt_find) == 2

    mt = MontyList([1, 4, 3, {"a": 5, "b": 1}, {"a": 4, "b": 0}])
    mt_find = mt.find({"a": {"$exists": 1}}, {"a": 0}, [("a", 1)])
    assert mt_find[0] == {"b": 0}
    assert mt_find[1] == {"b": 1}


def test_MontyList_sort():
    mt = MontyList([1, 4, 3, {"a": 5}, {"a": 4}])
    mt.sort("a", 1)
    assert mt == [1, 4, 3, {"a": 4}, {"a": 5}]


def test_MontyList_iter():
    mt = MontyList([1, 2, 3])
    assert next(mt) == 1
    assert next(mt) == 2
    assert next(mt) == 3
    with pytest.raises(StopIteration):
        next(mt)
    mt.rewind()
    assert next(mt) == 1


def test_MontyList_compare():
    mt = MontyList([1, 2, 3])
    assert mt == [1, 2, 3]
    assert mt != [1, 2, 0]
    assert mt > [1, 2, 0]
    assert mt < [1, 2, {"a": 0}]
    assert mt >= [1, 2, 0]
    assert mt <= [1, 2, {"a": 0}]

    assert mt > {"a": 0}
    assert mt > None
    assert mt > "string type"
    assert mt < True
    assert mt < MontyList([5])


def test_MontyList_getitem_err():
    mt = MontyList([1, 2, 3])
    with pytest.raises(TypeError):
        mt["ind"]
