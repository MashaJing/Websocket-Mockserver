def test_send_rule_messages():
    def parameterize_rule_and_message():
        """rule_type: "oneshot", "schedule"
        message: dict, str, int, None
        """

    def prepare_rule():
        """client.reset_server()
        POST /admin/mapping/{rule_type}
        {"message": message, "timeout": 0.1}
        """

    def receive_message():
        """ws://localhost:3003/ws/{connection_path}
        websocket.recv()
        """

    def verify_message():
        """assert received_message == (
            message if isinstance(message, dict) else str(message)
        )
        """
