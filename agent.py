"""
Claude-powered Tripletex agent.
Model: claude-opus-4-5 — maximum reasoning quality for 6.0 score target.
Uses tool_use (function calling) to iteratively call Tripletex API.
"""

import json
import os
import logging
from datetime import date
from typing import Any

import anthropic

from tripletex_client import TripletexClient

logger = logging.getLogger(__name__)

# ─────────────────────────── MODEL ───────────────────────────
MODEL = "claude-opus-4-5"

# ─────────────────────────── TOOLS (function definitions) ───────────────────────────
TOOLS: list[dict] = [
    # ── EMPLOYEES ──────────────────────────────────────────
    {
        "name": "search_employees",
        "description": "Search for employees in Tripletex. Returns a list of employees matching the given filters. Use fields like firstName, lastName, email to filter. Returns id, firstName, lastName, email, employeeNumber.",
        "input_schema": {
            "type": "object",
            "properties": {
                "firstName": {"type": "string", "description": "Filter by first name (partial match)"},
                "lastName": {"type": "string", "description": "Filter by last name (partial match)"},
                "email": {"type": "string", "description": "Filter by email"},
                "fields": {"type": "string", "description": "Comma-separated fields to return, e.g. 'id,firstName,lastName,email'"},
            },
        },
    },
    {
        "name": "get_employee",
        "description": "Get a single employee by ID. Returns all fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer", "description": "Employee ID"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "create_employee",
        "description": (
            "Create a new employee. "
            "Required: firstName, lastName. "
            "Optional: email, employeeNumber, phoneNumberMobile, phoneNumberHome, phoneNumberWork, "
            "nationalIdNumber (norsk personnummer), dateOfBirth (YYYY-MM-DD), "
            "address (object with addressLine1, city, postalCode, country.id). "
            "Roles: set administrator=true to make admin."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "employeeNumber": {"type": "string"},
                "phoneNumberMobile": {"type": "string"},
                "phoneNumberHome": {"type": "string"},
                "phoneNumberWork": {"type": "string"},
                "nationalIdNumber": {"type": "string"},
                "dateOfBirth": {"type": "string", "description": "YYYY-MM-DD"},
                "address": {"type": "object", "description": "Address object"},
                "administrator": {"type": "boolean", "description": "Grant administrator access"},
            },
            "required": ["firstName", "lastName"],
        },
    },
    {
        "name": "update_employee",
        "description": "Update an existing employee by ID. Provide only the fields you want to change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "phoneNumberMobile": {"type": "string"},
                "phoneNumberHome": {"type": "string"},
                "phoneNumberWork": {"type": "string"},
                "nationalIdNumber": {"type": "string"},
                "dateOfBirth": {"type": "string"},
                "address": {"type": "object"},
                "administrator": {"type": "boolean"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "delete_employee",
        "description": "Delete an employee by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "create_employment",
        "description": (
            "Create an employment record for an employee. "
            "Required: employee.id, startDate (YYYY-MM-DD). "
            "Optional: endDate, typeOfEmployment (ORDINARY_PRIVATE_EMPLOYER_RELATIONSHIP / others), "
            "remunerationType, workingHoursScheme, shiftDurationHours."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer", "description": "Employee ID"},
                "startDate": {"type": "string", "description": "YYYY-MM-DD"},
                "endDate": {"type": "string", "description": "YYYY-MM-DD"},
                "typeOfEmployment": {"type": "integer", "description": "Employment type code"},
                "remunerationType": {"type": "integer"},
                "workingHoursScheme": {"type": "integer"},
                "shiftDurationHours": {"type": "number"},
            },
            "required": ["employee_id", "startDate"],
        },
    },
    # ── CUSTOMERS ──────────────────────────────────────────
    {
        "name": "search_customers",
        "description": "Search for customers by name, email, or organization number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "organizationNumber": {"type": "string"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "get_customer",
        "description": "Get full details of a customer by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "create_customer",
        "description": (
            "Create a new customer. "
            "Required: name. "
            "Optional: email, organizationNumber, phoneNumber, address (object), "
            "isCustomer (default true), isSupplier, invoicesDueIn (days), currency.id. "
            "For delivery address: deliveryAddresses (list of address objects)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "organizationNumber": {"type": "string"},
                "phoneNumber": {"type": "string"},
                "isCustomer": {"type": "boolean"},
                "isSupplier": {"type": "boolean"},
                "invoicesDueIn": {"type": "integer", "description": "Payment due days"},
                "address": {"type": "object"},
                "deliveryAddresses": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["name"],
        },
    },
    {
        "name": "update_customer",
        "description": "Update customer fields by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "organizationNumber": {"type": "string"},
                "phoneNumber": {"type": "string"},
                "address": {"type": "object"},
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "create_contact",
        "description": (
            "Create a contact person linked to a customer. "
            "Required: firstName, lastName, customer.id. "
            "Optional: email, phoneNumberMobile, position (job title)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "customer_id": {"type": "integer", "description": "Customer ID to link contact to"},
                "email": {"type": "string"},
                "phoneNumberMobile": {"type": "string"},
                "position": {"type": "string", "description": "Job title"},
            },
            "required": ["firstName", "lastName", "customer_id"],
        },
    },
    # ── PRODUCTS ──────────────────────────────────────────
    {
        "name": "search_products",
        "description": "Search for products by name or product number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "number": {"type": "string"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "create_product",
        "description": (
            "Create a product/service. "
            "Required: name. "
            "Optional: number (product number), priceExcludingVatCurrency, "
            "priceIncludingVatCurrency, costExcludingVatCurrency, vatType.id, unit.id, "
            "isInactive, description."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "number": {"type": "string"},
                "priceExcludingVatCurrency": {"type": "number"},
                "priceIncludingVatCurrency": {"type": "number"},
                "costExcludingVatCurrency": {"type": "number"},
                "description": {"type": "string"},
                "vatType": {"type": "object", "description": "e.g. {\"id\": 3} for 25% VAT"},
                "unit": {"type": "object", "description": "e.g. {\"id\": 1000} for pieces"},
                "isInactive": {"type": "boolean"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "update_product",
        "description": "Update product fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "string"},
                "number": {"type": "string"},
                "priceExcludingVatCurrency": {"type": "number"},
                "priceIncludingVatCurrency": {"type": "number"},
            },
            "required": ["product_id"],
        },
    },
    # ── ORDERS ──────────────────────────────────────────
    {
        "name": "create_order",
        "description": (
            "Create a sales order (required before creating invoice). "
            "Required: customer.id, orderDate (YYYY-MM-DD). "
            "Optional: deliveryDate, orderLines (list of {product.id, count, unitPriceExcludingVatCurrency, description, vatType.id})."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer"},
                "orderDate": {"type": "string", "description": "YYYY-MM-DD"},
                "deliveryDate": {"type": "string"},
                "orderLines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "count": {"type": "number"},
                            "unitPriceExcludingVatCurrency": {"type": "number"},
                            "unitPriceIncludingVatCurrency": {"type": "number"},
                            "description": {"type": "string"},
                            "vatType": {"type": "object"},
                        },
                    },
                },
                "department": {"type": "object", "description": "e.g. {\"id\": 123}"},
                "project": {"type": "object", "description": "e.g. {\"id\": 456}"},
            },
            "required": ["customer_id", "orderDate"],
        },
    },
    # ── INVOICES ──────────────────────────────────────────
    {
        "name": "search_invoices",
        "description": "Search for invoices. Can filter by customer, date range, paid status etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customerId": {"type": "integer"},
                "invoiceDateFrom": {"type": "string", "description": "YYYY-MM-DD"},
                "invoiceDateTo": {"type": "string"},
                "isPaid": {"type": "boolean"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "create_invoice",
        "description": (
            "Create an invoice. Two modes:\n"
            "1. From existing order: provide order_id(s).\n"
            "2. Full invoice with embedded order: provide customer_id + order_lines.\n"
            "Required: invoiceDate (YYYY-MM-DD), invoiceDueDate (YYYY-MM-DD), "
            "and either order_ids OR (customer_id + order_lines).\n"
            "order_lines items: {description, count, unitPriceExcludingVatCurrency, product_id (optional)}."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "invoiceDate": {"type": "string", "description": "YYYY-MM-DD"},
                "invoiceDueDate": {"type": "string", "description": "YYYY-MM-DD"},
                "order_ids": {"type": "array", "items": {"type": "integer"}, "description": "Existing order IDs"},
                "customer_id": {"type": "integer", "description": "For embedded order mode"},
                "order_lines": {
                    "type": "array",
                    "description": "For embedded order mode",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "count": {"type": "number"},
                            "unitPriceExcludingVatCurrency": {"type": "number"},
                            "unitPriceIncludingVatCurrency": {"type": "number"},
                            "product_id": {"type": "integer"},
                        },
                    },
                },
                "comment": {"type": "string", "description": "Invoice comment/remark"},
            },
            "required": ["invoiceDate", "invoiceDueDate"],
        },
    },
    {
        "name": "register_payment",
        "description": "Register a payment on an invoice. Marks it as paid.",
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer"},
                "payment_date": {"type": "string", "description": "YYYY-MM-DD"},
                "amount": {"type": "number"},
                "payment_type_id": {"type": "integer", "description": "Payment type ID (default 1 = bank)"},
            },
            "required": ["invoice_id", "payment_date", "amount"],
        },
    },
    {
        "name": "create_credit_note",
        "description": "Create a credit note (kreditnota) for an invoice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer"},
                "date": {"type": "string", "description": "YYYY-MM-DD credit note date"},
                "send_to_customer": {"type": "boolean", "default": False},
            },
            "required": ["invoice_id", "date"],
        },
    },
    {
        "name": "delete_invoice",
        "description": "Delete an invoice (only possible if not sent).",
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer"},
            },
            "required": ["invoice_id"],
        },
    },
    # ── TRAVEL EXPENSES ──────────────────────────────────────────
    {
        "name": "search_travel_expenses",
        "description": "Search travel expense reports.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employeeId": {"type": "integer"},
                "departureIsAfter": {"type": "string"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "create_travel_expense",
        "description": (
            "Create a travel expense report. "
            "Required: description, employee.id, departureDate (YYYY-MM-DD), returnDate (YYYY-MM-DD). "
            "Optional: travelDetails (destination), costs (list of cost items)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "employee_id": {"type": "integer"},
                "departureDate": {"type": "string"},
                "returnDate": {"type": "string"},
                "destination": {"type": "string"},
                "costs": {"type": "array", "items": {"type": "object"}},
                "project_id": {"type": "integer"},
            },
            "required": ["description", "employee_id", "departureDate", "returnDate"],
        },
    },
    {
        "name": "delete_travel_expense",
        "description": "Delete a travel expense report by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expense_id": {"type": "integer"},
            },
            "required": ["expense_id"],
        },
    },
    # ── PROJECTS ──────────────────────────────────────────
    {
        "name": "search_projects",
        "description": "Search for projects by name or customer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "customerId": {"type": "integer"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "create_project",
        "description": (
            "Create a project. "
            "Required: name, startDate (YYYY-MM-DD), projectManager.id (employee id). "
            "Optional: number, customer.id, endDate, description, department.id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "startDate": {"type": "string"},
                "projectManagerId": {"type": "integer", "description": "Employee ID of project manager"},
                "number": {"type": "string"},
                "customer_id": {"type": "integer"},
                "endDate": {"type": "string"},
                "description": {"type": "string"},
                "department_id": {"type": "integer"},
            },
            "required": ["name", "startDate", "projectManagerId"],
        },
    },
    {
        "name": "delete_project",
        "description": "Delete a project by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer"},
            },
            "required": ["project_id"],
        },
    },
    # ── DEPARTMENTS ──────────────────────────────────────────
    {
        "name": "search_departments",
        "description": "List or search departments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "create_department",
        "description": (
            "Create a department. "
            "Required: name. "
            "Optional: departmentNumber, manager.id (employee id)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "departmentNumber": {"type": "string"},
                "manager_id": {"type": "integer", "description": "Employee ID of department manager"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "update_department",
        "description": "Update department fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department_id": {"type": "integer"},
                "name": {"type": "string"},
                "departmentNumber": {"type": "string"},
                "manager_id": {"type": "integer"},
            },
            "required": ["department_id"],
        },
    },
    # ── MODULES / SETTINGS ──────────────────────────────────────────
    {
        "name": "get_modules",
        "description": "Get enabled modules/settings for the company. Useful to check what features are available.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "enable_module",
        "description": (
            "Enable a company module. Common modules: "
            "moduleAccountingReports, moduleDepartment, moduleProject, moduleTravelExpense, "
            "moduleInvoice, moduleProductAndStock, moduleSalary, moduleEmployee."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "module_name": {"type": "string", "description": "Module field name, e.g. 'moduleDepartment'"},
            },
            "required": ["module_name"],
        },
    },
    # ── VOUCHERS ──────────────────────────────────────────
    {
        "name": "search_vouchers",
        "description": "Search ledger vouchers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dateFrom": {"type": "string"},
                "dateTo": {"type": "string"},
                "number": {"type": "string"},
                "fields": {"type": "string"},
            },
        },
    },
    {
        "name": "reverse_voucher",
        "description": "Reverse (reversere) a voucher to correct accounting errors.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voucher_id": {"type": "integer"},
                "date": {"type": "string", "description": "YYYY-MM-DD reversal date"},
            },
            "required": ["voucher_id", "date"],
        },
    },
    # ── SUPPLIERS ──────────────────────────────────────────
    {
        "name": "create_supplier",
        "description": "Create a supplier. Required: name. Optional: email, organizationNumber, phoneNumber, address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "organizationNumber": {"type": "string"},
                "phoneNumber": {"type": "string"},
                "address": {"type": "object"},
            },
            "required": ["name"],
        },
    },
    # ── GENERIC ──────────────────────────────────────────
    {
        "name": "api_get",
        "description": "Make a generic GET request to any Tripletex API endpoint. Use this for endpoints not covered by other tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "API path, e.g. '/employee' or '/product/unit'"},
                "params": {"type": "object", "description": "Query parameters"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "api_post",
        "description": "Make a generic POST request to any Tripletex API endpoint.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "body": {"type": "object"},
            },
            "required": ["path", "body"],
        },
    },
    {
        "name": "api_put",
        "description": "Make a generic PUT request to any Tripletex API endpoint.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "body": {"type": "object"},
                "params": {"type": "object"},
            },
            "required": ["path", "body"],
        },
    },
    {
        "name": "api_delete",
        "description": "Make a generic DELETE request to any Tripletex API endpoint.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["path"],
        },
    },
]

# ─────────────────────────── SYSTEM PROMPT ───────────────────────────
SYSTEM_PROMPT = f"""You are an expert Tripletex accounting agent competing in NM i AI 2026 for a 400,000 NOK prize.
Your goal: complete accounting tasks in Tripletex with PERFECT correctness AND maximum efficiency (minimum API calls, zero 4xx errors).

Today's date: {date.today().isoformat()}

## TRIPLETEX API FACTS
- Authentication: Basic Auth with username "0" and session token as password (handled by tools)
- Every submission starts with a FRESH empty Tripletex account
- API base: provided via proxy URL in the request
- IDs: always numeric integers. After creating an entity you get its ID from the response

## SCORING RULES (critical!)
- CORRECTNESS: Field-by-field check. Every wrong or missing field costs points.
- EFFICIENCY BONUS: Only applies if correctness = 100%. Fewer API calls = higher bonus.
- 4xx errors DESTROY efficiency bonus — validate before calling!
- Tier multiplier: Tier 1 = ×1, Tier 2 = ×2, Tier 3 = ×3
- Perfect Tier 3 + best efficiency = 6.0 (max possible score)

## STRATEGY FOR MAXIMUM SCORE
1. **Read the task completely** before making ANY API calls. Extract ALL fields mentioned.
2. **Plan** the minimal sequence of API calls needed.
3. **Never guess** required fields — read the task carefully.
4. **Create prerequisites first** (e.g., need customer before invoice, need order before invoice).
5. **Use embedded creation** when possible (e.g., create invoice with embedded order instead of separate calls).
6. **Never trial-and-error** — plan correctly the first time.
7. **Verify only if uncertain** — unnecessary GET calls reduce efficiency score.

## COMMON PATTERNS
- Simple employee/customer: 1 POST call
- Invoice with new customer: POST customer → POST order → POST invoice (or POST invoice with embedded order = 2 calls)
- Invoice for existing customer: GET customer (to find ID) → POST order → POST invoice
- Payment registration: GET invoice ID → POST payment
- Credit note: GET invoice ID → PUT invoice/:createCreditNote
- Travel expense: POST travelExpense (employee must exist first)
- Project: POST project (customer and employee must exist first)

## LANGUAGE
Tasks come in 7 languages: Norwegian (bokmål/nynorsk), English, Spanish, Portuguese, German, French.
Parse the task in whatever language it's written — the data (names, amounts, dates) is always in the prompt.

## FIELD PRECISION
- Dates: always YYYY-MM-DD format
- Phone numbers: include country code if given (e.g. +47 for Norway)
- Norwegian org numbers: 9 digits
- Email: lowercase, exact as given
- Names: preserve exact capitalisation from the task
- Amounts: decimal number (not string)

## IMPORTANT API QUIRKS
- Employee `administrator` field: set to true/false directly on employee object
- Invoice requires either (order_ids) or (customer_id + embedded orderLines via create_order first)
- Travel expense: employee must exist before creating expense
- Departments: may need to enable moduleDepartment first
- Payment types: use get_payment_types tool if unsure, default is bank transfer

COMPLETE THE TASK. DO NOT STOP UNTIL DONE.
"""

# ─────────────────────────── TOOL EXECUTOR ───────────────────────────

def execute_tool(tool_name: str, tool_input: dict, client: TripletexClient) -> Any:
    """Execute a tool call and return the result."""
    try:
        if tool_name == "search_employees":
            return client.search_employees(**tool_input)

        elif tool_name == "get_employee":
            return client.get_employee(tool_input["employee_id"])

        elif tool_name == "create_employee":
            inp = dict(tool_input)
            emp_id = inp.pop("employee_id", None)
            return client.create_employee(inp)

        elif tool_name == "update_employee":
            inp = dict(tool_input)
            eid = inp.pop("employee_id")
            return client.update_employee(eid, inp)

        elif tool_name == "delete_employee":
            return client.delete_employee(tool_input["employee_id"])

        elif tool_name == "create_employment":
            inp = dict(tool_input)
            eid = inp.pop("employee_id")
            payload = {"employee": {"id": eid}, **inp}
            return client.create_employment(payload)

        elif tool_name == "search_customers":
            return client.search_customers(**tool_input)

        elif tool_name == "get_customer":
            return client.get_customer(tool_input["customer_id"])

        elif tool_name == "create_customer":
            inp = dict(tool_input)
            return client.create_customer(inp)

        elif tool_name == "update_customer":
            inp = dict(tool_input)
            cid = inp.pop("customer_id")
            return client.update_customer(cid, inp)

        elif tool_name == "create_contact":
            inp = dict(tool_input)
            cid = inp.pop("customer_id")
            payload = {"customer": {"id": cid}, **inp}
            return client.create_contact(payload)

        elif tool_name == "search_products":
            return client.search_products(**tool_input)

        elif tool_name == "create_product":
            return client.create_product(tool_input)

        elif tool_name == "update_product":
            inp = dict(tool_input)
            pid = inp.pop("product_id")
            return client.update_product(pid, inp)

        elif tool_name == "create_order":
            inp = dict(tool_input)
            cid = inp.pop("customer_id")
            # Build orderLines with product references
            raw_lines = inp.pop("orderLines", [])
            order_lines = []
            for line in raw_lines:
                l = dict(line)
                prod_id = l.pop("product_id", None)
                if prod_id:
                    l["product"] = {"id": prod_id}
                order_lines.append(l)
            payload = {"customer": {"id": cid}, "orderLines": order_lines, **inp}
            return client.create_order(payload)

        elif tool_name == "search_invoices":
            return client.search_invoices(**tool_input)

        elif tool_name == "create_invoice":
            inp = dict(tool_input)
            order_ids = inp.pop("order_ids", None)
            customer_id = inp.pop("customer_id", None)
            order_lines = inp.pop("order_lines", None)

            if order_ids:
                # From existing orders
                payload = {
                    "invoiceDate": inp["invoiceDate"],
                    "invoiceDueDate": inp["invoiceDueDate"],
                    "orders": [{"id": oid} for oid in order_ids],
                }
                if "comment" in inp:
                    payload["comment"] = inp["comment"]
            elif customer_id and order_lines:
                # Create order inline then invoice
                today = inp["invoiceDate"]
                order_resp = client.create_order({
                    "customer": {"id": customer_id},
                    "orderDate": today,
                    "orderLines": [
                        {
                            **{k: v for k, v in line.items() if k != "product_id"},
                            **({"product": {"id": line["product_id"]}} if line.get("product_id") else {}),
                        }
                        for line in order_lines
                    ],
                })
                order_id = order_resp["id"]
                payload = {
                    "invoiceDate": inp["invoiceDate"],
                    "invoiceDueDate": inp["invoiceDueDate"],
                    "customer": {"id": customer_id},
                    "orders": [{"id": order_id}],
                }
                if "comment" in inp:
                    payload["comment"] = inp["comment"]
            else:
                payload = inp

            return client.create_invoice(payload)

        elif tool_name == "register_payment":
            return client.register_payment(
                tool_input["invoice_id"],
                tool_input["payment_date"],
                tool_input["amount"],
                tool_input.get("payment_type_id", 1),
            )

        elif tool_name == "create_credit_note":
            return client.create_credit_note(
                tool_input["invoice_id"],
                tool_input["date"],
                tool_input.get("send_to_customer", False),
            )

        elif tool_name == "delete_invoice":
            return client.delete_invoice(tool_input["invoice_id"])

        elif tool_name == "search_travel_expenses":
            return client.search_travel_expenses(**tool_input)

        elif tool_name == "create_travel_expense":
            inp = dict(tool_input)
            eid = inp.pop("employee_id")
            dest = inp.pop("destination", None)
            proj_id = inp.pop("project_id", None)
            payload = {"employee": {"id": eid}, **inp}
            if dest:
                payload["travelDetails"] = {"destination": dest}
            if proj_id:
                payload["project"] = {"id": proj_id}
            return client.create_travel_expense(payload)

        elif tool_name == "delete_travel_expense":
            return client.delete_travel_expense(tool_input["expense_id"])

        elif tool_name == "search_projects":
            return client.search_projects(**tool_input)

        elif tool_name == "create_project":
            inp = dict(tool_input)
            pm_id = inp.pop("projectManagerId")
            cust_id = inp.pop("customer_id", None)
            dept_id = inp.pop("department_id", None)
            payload = {"projectManager": {"id": pm_id}, **inp}
            if cust_id:
                payload["customer"] = {"id": cust_id}
            if dept_id:
                payload["department"] = {"id": dept_id}
            return client.create_project(payload)

        elif tool_name == "delete_project":
            return client.delete_project(tool_input["project_id"])

        elif tool_name == "search_departments":
            return client.search_departments(**tool_input)

        elif tool_name == "create_department":
            inp = dict(tool_input)
            mgr_id = inp.pop("manager_id", None)
            payload = dict(inp)
            if mgr_id:
                payload["manager"] = {"id": mgr_id}
            return client.create_department(payload)

        elif tool_name == "update_department":
            inp = dict(tool_input)
            did = inp.pop("department_id")
            mgr_id = inp.pop("manager_id", None)
            payload = dict(inp)
            if mgr_id:
                payload["manager"] = {"id": mgr_id}
            return client.update_department(did, payload)

        elif tool_name == "get_modules":
            return client.get_modules()

        elif tool_name == "enable_module":
            module_name = tool_input["module_name"]
            current = client.get_modules()
            current[module_name] = True
            return client.update_modules(current)

        elif tool_name == "search_vouchers":
            return client.search_vouchers(**tool_input)

        elif tool_name == "reverse_voucher":
            return client.reverse_voucher(tool_input["voucher_id"], tool_input["date"])

        elif tool_name == "create_supplier":
            return client.create_supplier(tool_input)

        elif tool_name == "api_get":
            return client.generic_get(tool_input["path"], tool_input.get("params"))

        elif tool_name == "api_post":
            return client.generic_post(tool_input["path"], tool_input["body"])

        elif tool_name == "api_put":
            return client.generic_put(tool_input["path"], tool_input["body"], tool_input.get("params"))

        elif tool_name == "api_delete":
            return client.generic_delete(tool_input["path"], tool_input.get("params"))

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Tool {tool_name} failed: {error_msg}")
        return {"error": error_msg, "tool": tool_name}


# ─────────────────────────── MAIN AGENT LOOP ───────────────────────────

def run_agent(
    task: str,
    base_url: str,
    session_token: str,
    files: list[dict] | None = None,
    max_iterations: int = 20,
) -> dict:
    """
    Run the Claude agent to complete a Tripletex task.
    Returns {"status": "completed"} on success.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)
    tripletex = TripletexClient(base_url=base_url, session_token=session_token)

    # Build initial user message
    user_content = f"TASK: {task}"
    if files:
        user_content += f"\n\nATTACHED FILES: {json.dumps([{'filename': f.get('filename'), 'content_length': len(f.get('content_base64', ''))} for f in files])}"
        user_content += "\nNote: Process attached PDFs/images to extract invoice data, amounts, etc."

    messages = [{"role": "user", "content": user_content}]

    try:
        for iteration in range(max_iterations):
            logger.info(f"Agent iteration {iteration + 1}/{max_iterations}")

            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            logger.info(f"Claude stop_reason: {response.stop_reason}, content blocks: {len(response.content)}")

            # Append assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # If Claude is done (no more tool calls)
            if response.stop_reason == "end_turn":
                logger.info("Agent completed task (end_turn)")
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        logger.info(f"Calling tool: {tool_name} with input: {json.dumps(tool_input, default=str)[:300]}")

                        result = execute_tool(tool_name, tool_input, tripletex)
                        logger.info(f"Tool result: {json.dumps(result, default=str)[:300]}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str),
                        })

                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                logger.warning(f"Unexpected stop_reason: {response.stop_reason}")
                break

    finally:
        tripletex.close()

    return {"status": "completed"}
