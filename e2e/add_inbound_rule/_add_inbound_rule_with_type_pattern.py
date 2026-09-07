def test_add_inbound_rule_with_type_pattern():
    def parameterize_type():
        """("^subscribe\\..+$", "subscribe.level2", True)
        ("^subscribe\\..+$", "unsubscribe.level2", False)
        ("^subscribe\\..+$", "subscribe", False)
        """

    def prepare_inbound_rule():
        """client.reset_server()
        POST /admin/mapping/inbound
        {"type_pattern": type_pattern, "response": {"type": "pattern-matched"}}
        """

    def send_message():
        """ws://localhost:3003/ws/{connection_path}
        websocket.send({"type": message_type})
        """

    def verify_response():
        """assert (received_message is not None) is expected"""
