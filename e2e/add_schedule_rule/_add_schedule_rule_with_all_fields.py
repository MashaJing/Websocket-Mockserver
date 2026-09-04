def test_add_schedule_rule_with_all_fields():
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
                "type": "quote",
                "payload": {"instrument": "AAPL", "price": 100},
            },
            "timeout": 0.2,
        }
        """

    def add_and_retrieve_rule():
        """POST /admin/mapping/schedule
        client.get_rules()
        """

    def verify_rule():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["schedule_rules_added"] == 1
        assert rules["schedule rules"] == [rule]
        """
