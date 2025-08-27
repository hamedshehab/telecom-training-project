# File: telecom/api/httpsms_webhook.py
import frappe
import json

@frappe.whitelist(allow_guest=True)
def httpsms_webhook():
    """
    Receives webhook POST from httpSMS and logs the payload.
    No authentication required.
    """
    try:
        # Get the JSON payload from httpSMS
        payload = json.loads(frappe.request.get_data(as_text=True))
    except Exception:
        payload = frappe.local.form_dict or {}

    # Log the payload to Frappe's error log
    frappe.log_error(message=json.dumps(payload), title="Incoming SMS")

    # Optional: print to console (useful for bench logs)
    print("Incoming SMS payload:", payload)

    # Return OK so httpSMS knows it was received
    return {"status": "ok", "payload_logged": True}
