# tests/test_file_utils.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import pytest
from utilities.file_utils import save_json, load_json, backup_file, recover_from_backup

def test_basic_save_and_load(tmp_path):
    test_file = tmp_path / "test.json"
    data = {"key": "value"}
    assert save_json(str(test_file), data)
    loaded = load_json(str(test_file))
    assert loaded == data

def test_backup_and_recover(tmp_path):
    test_file = tmp_path / "test.json"
    data = {"foo": "bar"}
    save_json(str(test_file), data)
    backup = backup_file(str(test_file))
    assert backup is not None
    # Boz
    with open(test_file, "w") as f:
        f.write("invalid{json")
    # Recover et
    recovered = recover_from_backup(str(test_file))
    assert recovered == data
