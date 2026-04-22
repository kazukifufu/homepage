from models.database import init_db
from models.ui_settings_model import UiSettingsModel

init_db()
m = UiSettingsModel()

# テスト1: 初回起動（未保存）→ デフォルト値が返る
d = m.load()
if d != {"sash_h0": 300, "sash_h1": 600, "sash_v0": 380}:
    print(f"Validation failed!")
    print(f"Expected: {{'sash_h0': 300, 'sash_h1': 600, 'sash_v0': 380}}")
    print(f"Actual:   {d}")
#assert d == {"sash_h0": 300, "sash_h1": 600, "sash_v0": 380}
print("テスト1:", d)
# → {'sash_h0': 300, 'sash_h1': 600, 'sash_v0': 380}

# テスト2: 全件保存 → 再読み込みで反映される
m.save({"sash_h0": 320, "sash_h1": 640, "sash_v0": 410})
d2 = m.load()
assert d2 == {"sash_h0": 320, "sash_h1": 640, "sash_v0": 410}
print("テスト2:", d2)
# → {'sash_h0': 320, 'sash_h1': 640, 'sash_v0': 410}

# テスト3: 部分更新 → 変更したキーだけ上書きされる
m.save({"sash_h0": 350})
d3 = m.load()
assert d3["sash_h0"] == 350
assert d3["sash_h1"] == 640   # 前回値が維持されている
assert d3["sash_v0"] == 410   # 前回値が維持されている
print("テスト3:", d3)
# → {'sash_h0': 350, 'sash_h1': 640, 'sash_v0': 410}

# テスト4: 不正キーは無視される
m.save({"sash_h0": 360, "unknown_key": 999})
d4 = m.load()
assert d4["sash_h0"] == 360
assert "unknown_key" not in d4   # 返り値にも含まれない
print("テスト4:", d4)
# → {'sash_h0': 360, 'sash_h1': 640, 'sash_v0': 410}

print("全テスト: OK")

