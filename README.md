# checker
This tool will check the content of the target webpage and provide notification if the content is changed

For the tool to work make sure to have the "checker.json" file in the following format:

[
    {"url": "https://web-page1.com", "div_class": "main-content", "slack_webhook_url": "https://hooks.slack.com/services/enter_your_slack_web_hook"},
    {"url": "https://web-page2.com", "div_class": "main-content", "slack_webhook_url": "https://hooks.slack.com/services/enter_your_slack_web_hook"},
    {"url": "https://web-page3.com", "div_class": "main-content", "slack_webhook_url": "https://hooks.slack.com/services/enter_your_slack_web_hook"}
]