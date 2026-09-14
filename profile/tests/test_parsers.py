from __future__ import annotations

from decimal import Decimal

from orderbook_app.connectors.binance import parse_depth_snapshot, parse_depth_update
from orderbook_app.connectors.okx import parse_snapshot, parse_update
from orderbook_app.services.simulated import generate_simulated_update


def test_binance_snapshot_parsing():
    payload = {"bids": [["3000", "1.2"]], "asks": [["3001", "0.8"]]}
    snapshot = parse_depth_snapshot(payload, "ETHUSDT", "binance")
    assert snapshot.bids[0].price == Decimal("3000.0")
    assert snapshot.asks[0].size == Decimal("0.8")


def test_binance_update_parsing():
    payload = {"E": 1700000000000, "b": [["3000", "1.0"]], "a": [["3001", "2.0"]]}
    update = parse_depth_update(payload, "ETHUSDT", "binance")
    assert update.bids[0].price == Decimal("3000.0")
    assert update.asks[0].size == Decimal("2.0")


def test_okx_snapshot_parsing():
    payload = {
        "data": [
            {
                "ts": "1700000000000",
                "bids": [["3000", "1.1"]],
                "asks": [["3001", "0.9"]],
            }
        ]
    }
    snapshot = parse_snapshot(payload, "ETH-USDT")
    assert snapshot.bids[0].price == Decimal("3000.0")
    assert snapshot.asks[0].size == Decimal("0.9")


def test_okx_update_parsing():
    payload = {
        "data": [
            {
                "ts": "1700000000000",
                "bids": [["2999", "1.3"]],
                "asks": [["3002", "0.7"]],
            }
        ]
    }
    update = parse_update(payload, "ETH-USDT")
    assert update.bids[0].price == Decimal("2999.0")
    assert update.asks[0].size == Decimal("0.7")


def test_simulated_update():
    update = generate_simulated_update("sim", "ETH/USDT")
    assert update.venue == "sim"
    assert update.symbol == "ETH/USDT"
    assert update.bids
    assert update.asks



def test_decimal_precision_and_zero_size_updates_are_preserved():
    payload = {"bids": [["3000.1234567890123456789", "0"]], "asks": [["3001", "0.1234567890123456789"]]}
    snapshot = parse_depth_snapshot(payload, "ETHUSDT", "binance")
    assert snapshot.bids[0].price == Decimal("3000.1234567890123456789")
    assert snapshot.bids[0].size == 0
    assert snapshot.model_dump(mode="json")["asks"][0]["size"] == "0.1234567890123456789"


def test_malformed_or_nonfinite_levels_are_rejected():
    import pytest
    from orderbook_app.models import parse_levels
    for levels in ([["3000"]], [["NaN", "1"]], [["3000", "Infinity"]], [["3000", "-1"]]):
        with pytest.raises(ValueError):
            parse_levels(levels)
