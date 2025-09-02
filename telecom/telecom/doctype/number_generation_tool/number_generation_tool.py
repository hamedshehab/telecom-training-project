# # Copyright (c) 2025, Me and contributors
# # For license information, please see license.txt

# import re

# import frappe
# from frappe.model.document import Document

# # Cache the number type patterns so they are fetched and compiled only once
# _number_type_patterns = None

# def get_number_type_patterns():
# 	global _number_type_patterns
# 	if _number_type_patterns is None:
# 		number_types = frappe.get_all(
# 			"Number Type",
# 			fields=["name", "criteria", "priority", "price"],
# 			order_by="priority asc"
# 		)
# 		patterns = []
# 		for nt in number_types:
# 			if nt.criteria:
# 				try:
# 					patterns.append((nt.name, re.compile(nt.criteria), nt.price))
# 				except re.error:
# 					frappe.throw(f"Invalid regex in Number Type '{nt.name}': {nt.criteria}")
# 		_number_type_patterns = patterns
# 	return _number_type_patterns

# def classify_number(number: str):
# 	global _number_type_patterns
# 	if _number_type_patterns is None:
# 		get_number_type_patterns()
# 	for name, pattern, price in _number_type_patterns:
# 		if pattern.match(number):
# 			return name, price
# 	return "عادي", None


# class NumberGenerationTool(Document):
# 	def validate(self):
# 		# Ensure start_number and end_number are numbers and 7 digits
# 		if not (str(self.start_number).isdigit() and str(self.end_number).isdigit()):
# 			frappe.throw("Start number and End number must be valid numbers.")

# 		# Pad to 7 digits and store as integer (e.g., 0001234 -> 1234, 0012345 -> 12345)
# 		self.start_number = str(self.start_number).zfill(7)
# 		self.end_number = str(self.end_number).zfill(7)
# 		start_number_str = str(self.start_number).zfill(7)
# 		end_number_str = str(self.end_number).zfill(7)

# 		if start_number_str > end_number_str:
# 			frappe.throw(
# 				f"Start number: ({start_number_str}) cannot be greater than end number: ({end_number_str})."
# 			)
# 		existing = frappe.get_all(
# 			"Number Generation Tool",
# 			filters={"prefix": self.prefix, "name": ["!=", self.name], "docstatus": 1},
# 			fields=["name", "end_number"],
# 		)
# 		for doc in existing:
# 			existing_end_number_str = str(doc["end_number"]).zfill(7)
# 			if start_number_str <= existing_end_number_str:
# 				frappe.throw(
# 					f"Start number: ({start_number_str}) cannot be less than or equal to an existing end number: ({existing_end_number_str}) for the same prefix."
# 				)
# 			if end_number_str <= existing_end_number_str:
# 				frappe.throw(
# 					f"End number: ({end_number_str}) cannot be less than or equal to an existing end number: ({existing_end_number_str}) for the same prefix."
# 				)

# 	def on_submit(self):
# 		# Generate numbers in the range and bulk insert into Test Generated Numbers
# 		start = int(self.start_number)
# 		end = int(self.end_number)
# 		prefix = str(self.prefix)
# 		records = []
# 		for num in range(start, end + 1):
# 			number_str = str(num).zfill(7)
# 			full_number = f"{prefix}{number_str}"

# 			number_type, price = classify_number(full_number)

# 			records.append(
# 				{
# 					"name": full_number,
# 					"number": full_number,
# 					"number_generation_tool": self.name,
# 					"status": "Inactive",
# 					"type": number_type,
# 					"price": price
# 				}
# 			)
# 		if records:
# 			frappe.db.bulk_insert(
# 				"Number",
# 				fields=["name", "number", "number_generation_tool", "status", "type", "price"],
# 				values=[
# 					(r["name"], r["number"], r["number_generation_tool"], r["status"], r["type"], r["price"])
# 					for r in records
# 				],
# 			)
# 			frappe.db.commit()


# Copyright (c) 2025, Me and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document

# Cache the number type patterns so they are fetched and compiled only once
_number_type_patterns = None


def get_number_type_patterns():
    """Fetch and compile regex patterns for Number Types (cached)."""
    global _number_type_patterns
    if _number_type_patterns is None:
        number_types = frappe.get_all(
            "Number Type",
            fields=["name", "criteria", "priority", "price"],
            order_by="priority asc",
        )
        patterns = []
        for nt in number_types:
            if nt.criteria:
                try:
                    # use fullmatch so entire number must match
                    patterns.append((nt.name, re.compile(nt.criteria), nt.price))
                except re.error:
                    frappe.throw(f"Invalid regex in Number Type '{nt.name}': {nt.criteria}")
        _number_type_patterns = patterns
    return _number_type_patterns


def classify_number(number: str):
    """Classify a number based on Number Type regex patterns."""
    global _number_type_patterns
    if _number_type_patterns is None:
        get_number_type_patterns()
    for name, pattern, price in _number_type_patterns:
        if pattern.fullmatch(number):
            return name, price
    return "عادي", None


class NumberGenerationTool(Document):
    def validate(self):
        # Ensure start_number and end_number are valid numbers
        if not (str(self.start_number).isdigit() and str(self.end_number).isdigit()):
            frappe.throw("Start number and End number must be valid numbers.")

        # Pad to 7 digits for comparison
        self.start_number = str(self.start_number).zfill(7)
        self.end_number = str(self.end_number).zfill(7)
        start_number_str = self.start_number
        end_number_str = self.end_number

        if start_number_str > end_number_str:
            frappe.throw(
                f"Start number: ({start_number_str}) cannot be greater than end number: ({end_number_str})."
            )

        # Check overlaps with other submitted tools for the same prefix
        existing = frappe.get_all(
            "Number Generation Tool",
            filters={"prefix": self.prefix, "name": ["!=", self.name], "docstatus": 1},
            fields=["name", "start_number", "end_number"],
        )
        for doc in existing:
            existing_start = str(doc["start_number"]).zfill(7)
            existing_end = str(doc["end_number"]).zfill(7)

            # overlap check: ranges intersect if not fully apart
            if not (end_number_str < existing_start or start_number_str > existing_end):
                frappe.throw(
                    f"Range {start_number_str}–{end_number_str} overlaps with existing range "
                    f"{existing_start}–{existing_end} for the same prefix."
                )

    def on_submit(self):
        # Enqueue background job for number generation
        frappe.enqueue(
	        "telecom.telecom.doctype.number_generation_tool.number_generation_tool.generate_numbers",
            start=int(self.start_number),
            end=int(self.end_number),
            prefix=str(self.prefix),
            tool_name=self.name,
            job_name=f"Generate Numbers for {self.name}",
        )


def generate_numbers(start, end, prefix, tool_name, batch_size=10000):
    """Background job: generate numbers in batches and bulk insert them."""
    records = []
    fields = ["name", "number", "number_generation_tool", "status", "type", "price"]

    for num in range(start, end + 1):
        number_str = str(num).zfill(7)
        full_number = f"{prefix}{number_str}"

        number_type, price = classify_number(full_number)

        records.append((full_number, full_number, tool_name, "Inactive", number_type, price))

        # Insert in batches
        if len(records) >= batch_size:
            frappe.db.bulk_insert("Number", fields=fields, values=records)
            frappe.db.commit()
            records = []

    # Insert any leftovers
    if records:
        frappe.db.bulk_insert("Number", fields=fields, values=records)
        frappe.db.commit()


# (Optional) hook to clear regex cache if Number Type is updated
def clear_number_type_cache(doc, method):
    global _number_type_patterns
    _number_type_patterns = None
