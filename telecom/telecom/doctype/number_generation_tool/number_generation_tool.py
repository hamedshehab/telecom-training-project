# Copyright (c) 2025, Me and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.model.document import Document

DIAMOND = re.compile(
	r"^7[78](\d)\1{7}$|^7[78](1234567|2345678|3456789|4567890)$|^7[78](9876543|8765432|7654321|6543210)$|^7[78](\d\d)\1{3}$|^7[78](\d)(\d)(\d)\3\2\1\d*$|^7[78](0{6}|5{6}|9{6})$"
)
PLATINUM = re.compile(
	r"^7[78]\d*(\d)\1{4,}\d*$|^7[78](\d{6})(\1?)$|^7[78](123456|234567|345678|456789|567890)$|^7[78](987654|876543|765432|654321|543210)$|^7[78](\d{3})\1{2}$|^7[78](\d\d)(\1){3}$|^7[78](\d)(\d)\1\2\1\2\1$|^7[78](\d)(\d{7})\1$|^77(?:\d(\d)\1){3,}"
)
GOLDEN = re.compile(
	r"^7[78]\d*(\d)\1{3}\d*$|^7[78]\d*(\d{3})\1\d*$|^7[78](\d)(\d)\2\1\d*$|^7[78]\d*(12345|23456|34567|45678|56789|67890)\d*$|^7[78]\d*(98765|87654|76543|65432|54321|43210)\d*$|^7[78](\d)\d\1\d\1\d$|^77(?=(?:.*(\d)\1){3})"
)
SILVER = re.compile(
	r"^7[78]\d*(\d)\1{2}\d*$|^7[78]\d*(\d{2})\1\d*$|^7[78]\d*(0123|1234|2345|3456|4567|5678|6789)\d*$|^7[78]\d*(3210|4321|5432|6543|7654|8765|9876)\d*$|^7[78]\d*(\d\d)\1{1,2}\d*$|^77(?=(?:.*(\d)\1){2})"
)
NORMAL = re.compile(r"^7[78]\d{7}$")


def classify_number(number: str) -> str:
	if DIAMOND.match(number):
		return "ماسي"
	elif PLATINUM.match(number):
		return "بلاتيني"
	elif GOLDEN.match(number):
		return "ذهبي"
	elif SILVER.match(number):
		return "فضي"
	elif NORMAL.match(number):
		return "عادي"


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

	def on_submit(self):
		# Generate numbers in the range and bulk insert into Test Generated Numbers
		start = int(self.start_number)
		end = int(self.end_number)
		prefix = str(self.prefix)
		records = []
		for num in range(start, end + 1):
			number_str = str(num).zfill(7)
			full_number = f"{prefix}{number_str}"

			number_type = classify_number(full_number)

			records.append(
				{
					"name": full_number,
					"number": full_number,
					"number_generation_tool": self.name,
					"status": "Inactive",
					"type": number_type,
				}
			)
		if records:
			frappe.db.bulk_insert(
				"Test Generated Numbers",
				fields=["name", "number", "number_generation_tool", "status", "type"],
				values=[
					(r["name"], r["number"], r["number_generation_tool"], r["status"], r["type"])
					for r in records
				],
			)
			frappe.db.commit()
