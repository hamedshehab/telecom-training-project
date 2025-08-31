// Copyright (c) 2025, Me and contributors
// For license information, please see license.txt

frappe.ui.form.on("Number Generation Tool", {
	refresh(frm) {
        if (frm.doc.prefix && !frm.doc.docstatus) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Number Generation Tool",
                    fields: ["end_number"],
                    filters: {
                        prefix: frm.doc.prefix,
                        docstatus: 1 // Only consider submitted documents
                    },
                    order_by: "creation desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let latest_end = parseInt(r.message[0].end_number, 10) || 0;
                        let next_start = (latest_end + 1).toString().padStart(7, "0");
                        frm.set_value("start_number", next_start);
                    } else {
                        frm.set_value("start_number", "0000000");
                    }
                }
            });
        }
	},
    prefix: function(frm) {
        if (frm.doc.prefix) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Number Generation Tool",
                    fields: ["end_number"],
                    filters: {
                        prefix: frm.doc.prefix,
                        docstatus: 1 // Only consider submitted documents
                    },
                    order_by: "creation desc",
                    limit_page_length: 1
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let latest_end = parseInt(r.message[0].end_number, 10) || 0;
                        let next_start = (latest_end + 1).toString().padStart(7, "0");
                        frm.set_value("start_number", next_start);
                    } else {
                        frm.set_value("start_number", "0000000");
                    }
                }
            });
        }
    },
    validate: function(frm) {
        let start = frm.doc.start_number;
        let end = frm.doc.end_number;

        // 1. Ensure both are digits
        if (!/^\d+$/.test(start) || !/^\d+$/.test(end)) {
            frappe.msgprint(__('Start Number and End Number must contain only digits.'));
            frappe.validated = false;
            return;
        }

        // 2. Pad to 7 digits if necessary
        if (start.length !== 7) {
            start = start.padStart(7, "0");
            frm.set_value("start_number", start);
        }
        if (end.length !== 7) {
            end = end.padStart(7, "0");
            frm.set_value("end_number", end);
        }

        // 3. Check end_number >= start_number
        if (parseInt(end, 10) < parseInt(start, 10)) {
            frappe.msgprint(__('End Number cannot be less than Start Number.'));
            frappe.validated = false;
        }
    }
});
