def test_add_inbound_rule_with_all_fields():
    def parameterize_rule():
        """rule: channels, channels_pattern, url_path, url_pattern, type, type_pattern,
        payload, response
        """

    def prepare_rule():
        """client.reset_server()
        rule = {
            "channels": "quotes,trades",
            "channels_pattern": "^quotes$",
            "url_path": "prices",
            "url_pattern": "^prices$",
            "type": "subscribe",
            "type_pattern": "^sub.*",
            "payload": {"instrument": "AAPL", "depth": 1},
            "response": {
                "type": "subscribed",
                "payload": {"instrument": "AAPL"},
            },
        }
        """

    def add_and_retrieve_rule():
        """POST /admin/mapping/inbound
        client.get_rules()
        """

    def verify_rule():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["inbound_rules_added"] == 1
        assert rules["inbound rules"] == [rule]
        """
