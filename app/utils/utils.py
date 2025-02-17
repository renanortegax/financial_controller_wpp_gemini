def check_wpp_message(request_data):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        request_data.get("object")
        and request_data.get("entry")
        and request_data["entry"][0].get("changes")
        and request_data["entry"][0]["changes"][0].get("value")
        and request_data["entry"][0]["changes"][0]["value"].get("messages")
        and request_data["entry"][0]["changes"][0]["value"]["messages"][0]
    )