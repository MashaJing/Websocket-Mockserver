def test_add_oneshot_rule_with_all_fields():
    def parameterize_rule():
        """rule: channels, channels_pattern, url_path, url_pattern, message, timeout"""

    def prepare_rule():
        """client.reset_server()
        rule = {
            "channels": "quotes,trades",
            "channels_pattern": "^quotes$",
            "url_path": "prices",
            "url_pattern": "^prices$",
            "message": {
                "type": "snapshot",
                "payload": {"instrument": "AAPL"},
            },
            "timeout": 0.2,
        }
        """

    def add_and_retrieve_rule():
        """POST /admin/mapping/oneshot
        client.get_rules()
        """

    def verify_rule():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["oneshot_rules_added"] == 1
        assert rules["oneshot rules"] == [rule]
        """
