# Copyright (c) 2025, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NumberGenerationTool(Document):
	def validate(self):
		# Ensure start_number and end_number are numbers and 7 digits
		if not (str(self.start_number).isdigit() and str(self.end_number).isdigit()):
			frappe.throw("Start number and End number must be valid numbers.")

		# Pad to 7 digits and store as integer (e.g., 0001234 -> 1234, 0012345 -> 12345)
		self.start_number = str(self.start_number).zfill(7)
		self.end_number = str(self.end_number).zfill(7)
		start_number_str = str(self.start_number).zfill(7)
		end_number_str = str(self.end_number).zfill(7)

		if start_number_str > end_number_str:
			frappe.throw(
				f"Start number: ({start_number_str}) cannot be greater than end number: ({end_number_str})."
			)
		existing = frappe.get_all(
			"Number Generation Tool",
			filters={"prefix": self.prefix, "name": ["!=", self.name], "docstatus": 1},
			fields=["name", "end_number"],
		)
		for doc in existing:
			existing_end_number_str = str(doc["end_number"]).zfill(7)
			if start_number_str <= existing_end_number_str:
				frappe.throw(
					f"Start number: ({start_number_str}) cannot be less than or equal to an existing end number: ({existing_end_number_str}) for the same prefix."
				)
			if end_number_str <= existing_end_number_str:
				frappe.throw(
					f"End number: ({end_number_str}) cannot be less than or equal to an existing end number: ({existing_end_number_str}) for the same prefix."
				)
