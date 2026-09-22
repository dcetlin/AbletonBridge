# AbletonBridge / init.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import threading
import time
import traceback
import queue

# Force handler module imports so @command decorators execute and populate the registry.
from .handlers import (
    session, tracks, clips, mixer, devices,
    browser, scenes, arrangement, audio, midi, automation,
)
from .handlers._registry import dispatch, get_modifying_commands, get_readonly_commands

# Constants for socket communication
DEFAULT_PORT = 9877
UDP_REALTIME_PORT = 9882
HOST = "localhost"


def create_instance(c_instance):
    """Create and return the AbletonBridge script instance"""
    return AbletonBridge(c_instance)


class AbletonBridge(ControlSurface):
    """AbletonBridge Remote Script for Ableton Live"""

    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonBridge Remote Script initializing...")

        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.client_sockets = []
        self._client_lock = threading.Lock()  # protects client_threads and client_sockets
        self.server_thread = None
        self.running = False

        # UDP real-time parameter server
        self.udp_sock = None
        self.udp_thread = None
        self.udp_running = False

        # Start the socket servers
        self.start_server()
        self.start_udp_server()

        self.log_message("AbletonBridge initialized")

        # Show a message in Ableton
        self.show_message("AbletonBridge: TCP " + str(DEFAULT_PORT) + " / UDP " + str(UDP_REALTIME_PORT))

    @property
    def _song(self):
        """Always return the current song, even after File > New"""
        return self.song()

    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonBridge disconnecting...")
        self.running = False

        # Close UDP socket FIRST to unblock recvfrom(), THEN clear the flag.
        # The UDP thread's exception handler checks udp_running, so it will
        # exit silently when it sees the flag is False.
        if self.udp_sock:
            try:
                self.udp_sock.close()
            except (OSError, socket.error):
                pass
            self.udp_sock = None
        self.udp_running = False

        if self.udp_thread and self.udp_thread.is_alive():
            self.udp_thread.join(3.0)

        # Close all client sockets so their threads can exit
        with self._client_lock:
            socks_to_close = self.client_sockets[:]
            self.client_sockets = []
        for sock in socks_to_close:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass
            try:
                sock.close()
            except (OSError, socket.error):
                pass

        # Stop the listening server socket (no shutdown needed for listening sockets)
        if self.server:
            try:
                self.server.close()
            except (OSError, socket.error):
                pass

        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(3.0)

        # Wait briefly for client threads to exit
        with self._client_lock:
            threads_to_join = self.client_threads[:]
        for client_thread in threads_to_join:
            if client_thread.is_alive():
                client_thread.join(3.0)

        ControlSurface.disconnect(self)
        self.log_message("AbletonBridge disconnected")

    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(5)

            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonBridge: Error starting server - " + str(e))

    def start_udp_server(self):
        """Start the UDP real-time parameter server in a separate thread."""
        try:
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_sock.bind((HOST, UDP_REALTIME_PORT))
            self.udp_sock.settimeout(1.0)

            self.udp_running = True
            self.udp_thread = threading.Thread(target=self._udp_server_loop)
            self.udp_thread.daemon = True
            self.udp_thread.start()

            self.log_message("UDP real-time server started on port " + str(UDP_REALTIME_PORT))
        except Exception as e:
            self.udp_running = False
            self.log_message("Error starting UDP server: " + str(e))

    def _udp_server_loop(self):
        """UDP server loop - receives fire-and-forget parameter updates."""
        while self.udp_running:
            try:
                data, addr = self.udp_sock.recvfrom(4096)
                if not data:
                    continue

                try:
                    command = json.loads(data.decode("utf-8"))
                except (ValueError, UnicodeDecodeError) as parse_err:
                    self.log_message(
                        "UDP: malformed packet from {0}: {1}".format(addr, parse_err))
                    continue

                self._process_udp_command(command)

            except socket.timeout:
                continue
            except Exception as e:
                if self.udp_running:
                    self.log_message("UDP server error: " + str(e))
                time.sleep(0.1)

    # UDP wire names → registry command names
    _UDP_COMMANDS = {
        "set_device_parameter": "set_device_parameter",
        "batch_set_device_parameters": "set_device_parameters_batch",
    }

    def _process_udp_command(self, command):
        """Process a UDP command via the registry. Fire-and-forget — no response."""
        cmd = command.get("type", "")
        params = command.get("params", {})
        registry_name = self._UDP_COMMANDS.get(cmd)
        if registry_name is None:
            return
        def task():
            try:
                dispatch(registry_name, self._song, params, self)
            except Exception as e:
                self.log_message("UDP {0} error: {1}".format(cmd, e))
        try:
            self.schedule_message(0, task)
        except AssertionError:
            self.log_message("UDP {0}: schedule_message unavailable".format(cmd))

    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            self.server.settimeout(1.0)

            while self.running:
                try:
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))
                    self.show_message("AbletonBridge: Client connected")

                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                    with self._client_lock:
                        self.client_threads.append(client_thread)
                        self.client_sockets.append(client)
                        # Clean up finished client threads
                        self.client_threads = [t for t in self.client_threads if t.is_alive()]

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)

            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))

    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(5.0)
        buffer = ''

        try:
            while self.running:
                try:
                    try:
                        data = client.recv(8192)
                    except socket.timeout:
                        continue

                    if not data:
                        self.log_message("Client disconnected")
                        break

                    # Accumulate data (replace invalid UTF-8 instead of crashing)
                    buffer += data.decode('utf-8', errors='replace')

                    # Process all complete newline-delimited messages
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            command = json.loads(line)
                        except ValueError:
                            self.log_message("Invalid JSON received, skipping: " + line[:100])
                            continue

                        self.log_message("Received command: " + str(command.get("type", "unknown")))

                        response = self._process_command(command)

                        response_str = json.dumps(response) + '\n'
                        try:
                            client.sendall(response_str.encode('utf-8'))
                        except (OSError, socket.error):
                            self.log_message("Client disconnected during response send")
                            break

                        # Small breathing room between consecutive commands to prevent
                        # flooding Ableton's main thread scheduler during rapid bursts.
                        # The MCP server serializes tool calls via asyncio semaphore,
                        # so 1ms is sufficient to yield the thread.
                        time.sleep(0.001)

                    # 1MB safety limit
                    if len(buffer) > 1048576:
                        self.log_message("Buffer overflow (>1MB without newline), disconnecting client")
                        try:
                            err = json.dumps({"status": "error", "message": "Request too large (>1MB)"}) + '\n'
                            client.sendall(err.encode('utf-8'))
                        except Exception:
                            pass
                        break

                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())

                    error_response = self._structured_error(e)
                    try:
                        client.sendall((json.dumps(error_response) + '\n').encode('utf-8'))
                    except Exception:
                        break

                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass
            try:
                client.close()
            except (OSError, socket.error):
                pass
            with self._client_lock:
                try:
                    self.client_sockets.remove(client)
                except ValueError:
                    pass
            self.log_message("Client handler stopped")

    # ------------------------------------------------------------------
    # Error sanitisation
    # ------------------------------------------------------------------

    def _structured_error(self, e, command_type=None, may_have_landed=False):
        """Return a structured error response dict with code and message.

        ValueError/IndexError/TypeError/KeyError messages are preserved.
        Everything else gets a generic message; details stay in the log.
        """
        if isinstance(e, ValueError):
            code = "invalid_input"
            message = str(e)
        elif isinstance(e, IndexError):
            code = "index_out_of_range"
            message = str(e)
        elif isinstance(e, KeyError):
            code = "missing_parameter"
            message = "Missing required parameter: {0}".format(e)
        elif isinstance(e, TypeError):
            code = "type_error"
            message = str(e)
        elif isinstance(e, AttributeError):
            code = "attribute_error"
            message = str(e)
        elif isinstance(e, NotImplementedError):
            code = "not_implemented"
            message = str(e)
        elif isinstance(e, RuntimeError):
            code = "runtime_error"
            message = str(e)
        elif isinstance(e, queue.Empty):
            code = "timeout"
            message = "Operation timed out"
            may_have_landed = True
        else:
            code = "internal_error"
            message = "Internal error - check Ableton log for details"

        result = {
            "status": "error",
            "code": code,
            "message": message,
        }
        if command_type:
            result["command"] = command_type
        if may_have_landed:
            result["may_have_landed"] = True
        return result

    # ------------------------------------------------------------------
    # Command routing
    # ------------------------------------------------------------------

    def _process_command(self, command):
        """Process a command from the client and return a response."""
        command_type = command.get("type", "")
        params = command.get("params", {})
        response = {"status": "success", "result": {}}

        try:
            if command_type in get_modifying_commands():
                response = self._dispatch_on_main_thread(command_type, params)
            elif command_type in get_readonly_commands():
                response = self._dispatch_on_main_thread_readonly(command_type, params)
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response = self._structured_error(e, command_type=command_type)

        return response

    def _dispatch_on_main_thread_impl(self, command_type, params, timeout_msg):
        """Schedule a command on Ableton's main thread and wait for the result."""
        response_queue = queue.Queue()

        def main_thread_task():
            try:
                result = dispatch(command_type, self._song, params, self)
                response_queue.put({"status": "success", "result": result})
            except Exception as e:
                self.log_message("Error in main thread task: " + str(e))
                self.log_message(traceback.format_exc())
                response_queue.put(self._structured_error(e, command_type=command_type))

        try:
            self.schedule_message(0, main_thread_task)
        except AssertionError:
            self.log_message("TCP command: schedule_message unavailable, returning error")
            return {"status": "error", "message": "Ableton scheduling unavailable — try again shortly"}

        try:
            return response_queue.get(timeout=10.0)
        except queue.Empty:
            is_modifying = command_type in get_modifying_commands()
            return self._structured_error(
                queue.Empty(), command_type=command_type,
                may_have_landed=is_modifying
            )

    def _dispatch_on_main_thread(self, command_type, params):
        return self._dispatch_on_main_thread_impl(
            command_type, params,
            "Timeout waiting for operation to complete")

    def _dispatch_on_main_thread_readonly(self, command_type, params):
        return self._dispatch_on_main_thread_impl(
            command_type, params,
            "Timeout waiting for read-only operation to complete")
