from app.seed import seed_demo
from app.store import MVPStore


def test_seed_demo_creates_v02_collections(tmp_path):
    store = MVPStore(tmp_path / "demo.sqlite3")
    brief = seed_demo(store)

    assert brief.event_id == "demo-night-tour"
    assert store.get_event_summary("demo-night-tour").title == "福隆新街周末旧区夜游"
    assert len(store.list_route_points()) >= 6
    assert len(store.list_runtime_states()) >= 8
    assert len(store.list_operational_metrics("demo-night-tour")) >= 5
