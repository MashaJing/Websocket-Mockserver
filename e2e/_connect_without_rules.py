def test_connect_without_rules():
    def parameterize_connection():
        """connection_path: "prices", "orders", "nested/path"
        channels: None, "quotes", "quotes,trades"
        """

    def reset_rules():
        """client.reset_server()"""

    def connect_and_wait():
        """ws://localhost:3003/ws/{connection_path}
        websocket.handshake()
        websocket.recv(timeout=0.5)
        """

    def verify_connection():
        """assert websocket.open
        assert received_messages == []
        """
