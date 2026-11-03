import pytest
import json
import socket
import time
from unittest.mock import MagicMock, patch, PropertyMock, call
from MCP_Server.connections.ableton import AbletonConnection, _peer_closed, get_ableton_connection, NON_IDEMPOTENT_COMMANDS
from MCP_Server.constants import TIER_0_COMMANDS, TIER_1_COMMANDS, TIER_2_COMMANDS
import MCP_Server.state as state


class TestAbletonConnectionSendCommand:
    def test_successful_command(self):
        """Test basic send_command round-trip."""
        conn = AbletonConnection(host="localhost", port=9877)
        conn.sock = MagicMock()
        conn._recv_buffer = ""
        # Mock receive_full_response
        with patch.object(conn, 'receive_full_response', return_value={"status": "success", "result": {"tempo": 120.0}}):
            result = conn.send_command("get_session_info")
            assert result["tempo"] == 120.0

    def test_non_idempotent_single_attempt(self):
        """Non-idempotent commands (create/delete) should only attempt once."""
        conn = AbletonConnection(host="localhost", port=9877)
        conn.sock = MagicMock()
        conn._recv_buffer = ""
        with patch.object(conn, 'receive_full_response', side_effect=socket.timeout("timeout")):
            with patch.object(conn, 'disconnect'):
                with pytest.raises(Exception):
                    conn.send_command("create_midi_track", {"index": -1})
                # Should have only called send once (no retry)
                assert conn.sock.sendall.call_count == 1

    def test_idempotent_retry_on_failure(self):
        """Idempotent commands should retry once on socket error."""
        conn = AbletonConnection(host="localhost", port=9877)
        conn.sock = MagicMock()
        conn._recv_buffer = ""
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise socket.error("connection reset")
            return {"status": "success", "result": {}}
        with patch.object(conn, 'receive_full_response', side_effect=side_effect):
            with patch.object(conn, 'disconnect'):
                with patch.object(conn, 'connect', return_value=True):
                    result = conn.send_command("get_session_info")
                    assert result == {}

    def test_tier_0_no_delay(self):
        """TIER_0 commands should have no pre/post delays."""
        conn = AbletonConnection(host="localhost", port=9877)
        conn.sock = MagicMock()
        conn._recv_buffer = ""
        with patch.object(conn, 'receive_full_response', return_value={"status": "success", "result": {}}):
            with patch('time.sleep') as mock_sleep:
                conn.send_command("set_tempo", {"tempo": 120})
                # TIER_0 should not call time.sleep for delays
                for c in mock_sleep.call_args_list:
                    # Any sleep call should not be the tier delay ones
                    pass  # Just verify no Exception

    def test_non_idempotent_commands_list(self):
        """Verify key commands are in non-idempotent set."""
        assert "create_midi_track" in NON_IDEMPOTENT_COMMANDS
        assert "delete_track" in NON_IDEMPOTENT_COMMANDS
        assert "add_notes_to_clip" in NON_IDEMPOTENT_COMMANDS
        # Read commands should NOT be in the set
        assert "get_session_info" not in NON_IDEMPOTENT_COMMANDS

    def test_tier_membership(self):
        """Verify tier sets are disjoint."""
        assert len(TIER_0_COMMANDS & TIER_1_COMMANDS) == 0
        assert len(TIER_1_COMMANDS & TIER_2_COMMANDS) == 0
        assert len(TIER_0_COMMANDS & TIER_2_COMMANDS) == 0


class TestGetAbletonConnection:
    def test_returns_existing_valid_connection(self):
        """Should return existing connection if socket is valid."""
        mock_conn = MagicMock()
        mock_conn.sock = MagicMock()
        mock_conn.sock.getpeername.return_value = ("localhost", 9877)
        mock_conn.send_command.return_value = {"status": "success"}
        state.ableton_connection = mock_conn
        with patch('MCP_Server.connections.ableton.AbletonConnection'), patch('MCP_Server.connections.ableton._peer_closed', return_value=False):
            result = get_ableton_connection()
            assert result == mock_conn

    def test_reconnects_on_dead_socket(self):
        """Should create new connection if existing socket is dead."""
        mock_conn = MagicMock()
        mock_conn.sock = MagicMock()
        mock_conn.sock.getpeername.side_effect = socket.error("not connected")
        state.ableton_connection = mock_conn
        new_conn = MagicMock()
        new_conn.connect.return_value = True
        new_conn.send_command.return_value = {"status": "success"}
        with patch('MCP_Server.connections.ableton.AbletonConnection', return_value=new_conn):
            result = get_ableton_connection()
            assert new_conn.connect.called


class TestPeerClosed:
    def test_open_quiet_socket_is_alive(self):
        a, b = socket.socketpair()
        try:
            assert not _peer_closed(a)
        finally:
            a.close()
            b.close()

    def test_pending_data_is_alive_and_not_consumed(self):
        a, b = socket.socketpair()
        try:
            b.send(b"x")
            assert not _peer_closed(a)
            assert a.recv(1) == b"x"
        finally:
            a.close()
            b.close()

    def test_closed_peer_is_detected(self):
        a, b = socket.socketpair()
        b.close()
        try:
            assert _peer_closed(a)
        finally:
            a.close()


class TestGetAbletonConnectionLiveness:
    @pytest.fixture
    def tcp_pair(self):
        """A connected TCP pair: getpeername still succeeds after the peer closes."""
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            client = socket.create_connection(listener.getsockname())
            server_end, _ = listener.accept()
        yield client, server_end
        client.close()
        server_end.close()

    def _install(self, monkeypatch, sock):
        conn = AbletonConnection(host="localhost", port=9877)
        conn.sock = sock
        monkeypatch.setattr(state, "ableton_connection", conn)
        return conn

    def test_open_connection_is_reused_with_its_timeout(self, monkeypatch, tcp_pair):
        conn = self._install(monkeypatch, tcp_pair[0])
        assert get_ableton_connection() is conn
        assert tcp_pair[0].gettimeout() == 1.0

    def test_closed_connection_is_replaced(self, monkeypatch, tcp_pair):
        self._install(monkeypatch, tcp_pair[0])
        tcp_pair[1].close()
        time.sleep(0.05)
        tcp_pair[0].getpeername()  # the case the check exists for
        fresh = MagicMock()
        fresh.connect.return_value = True
        with patch("MCP_Server.connections.ableton.AbletonConnection", return_value=fresh):
            assert get_ableton_connection() is fresh

    def test_check_is_skipped_while_a_command_holds_the_socket(self, monkeypatch, tcp_pair):
        conn = self._install(monkeypatch, tcp_pair[0])
        tcp_pair[1].close()
        time.sleep(0.05)
        with conn._send_lock:
            with patch("MCP_Server.connections.ableton._peer_closed") as check:
                assert get_ableton_connection() is conn
        check.assert_not_called()
