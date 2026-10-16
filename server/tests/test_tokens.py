import time
from app.security.crypto_tokens import (
    compute_rotating_token,
    get_current_window_index,
    verify_rotating_token,
    pack_ble_payload,
    unpack_ble_payload,
    generate_session_secret
)

def test_rotating_token_determinism():
    secret = generate_session_secret()
    session_id = 42
    window = 1000

    token1 = compute_rotating_token(session_id, secret, window)
    token2 = compute_rotating_token(session_id, secret, window)
    assert token1 == token2
    assert len(token1) == 16

    # Different window produces different token
    token_next = compute_rotating_token(session_id, secret, window + 1)
    assert token1 != token_next

def test_token_verification_windows():
    secret = generate_session_secret()
    session_id = 99
    now = 1700000000.0  # fixed timestamp
    interval = 5

    current_w = get_current_window_index(now, interval)
    current_token = compute_rotating_token(session_id, secret, current_w)
    prev_token = compute_rotating_token(session_id, secret, current_w - 1)
    old_expired_token = compute_rotating_token(session_id, secret, current_w - 5)

    # Current token must verify
    valid, msg = verify_rotating_token(session_id, secret, current_token, server_time=now, interval=interval, grace_windows=1)
    assert valid is True

    # Previous window token must verify under grace window 1
    valid, msg = verify_rotating_token(session_id, secret, prev_token, server_time=now, interval=interval, grace_windows=1)
    assert valid is True

    # Old expired token (5 windows ago = 25 seconds ago) MUST be rejected
    valid, msg = verify_rotating_token(session_id, secret, old_expired_token, server_time=now, interval=interval, grace_windows=1)
    assert valid is False
    assert "expired" in msg.lower() or "invalid" in msg.lower()

def test_ble_payload_packing_and_unpacking():
    session_id = 84920
    token = "a1b2c3d4e5f67890"
    window = 54321

    packed = pack_ble_payload(session_id, token, window)
    assert len(packed) == 26
    # Starts with 0x5050 ("PP")
    assert packed[:2] == b"\x50\x50"

    unpacked = unpack_ble_payload(packed)
    assert unpacked is not None
    assert unpacked["session_id"] == session_id
    assert unpacked["window_index"] == window
    assert unpacked["token"] == token
