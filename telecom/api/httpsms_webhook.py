import frappe


# Temporarily allow all requests
@frappe.whitelist(allow_guest=True)
def httpsms_webhook():
	payload = frappe.local.form_dict
	frappe.logger().info({"payload": payload})
	return {"status": "ok"}
