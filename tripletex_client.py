"""
Tripletex API v2 client wrapper.
Auth: Basic Auth with username "0" and session token as password.
"""

import httpx
from typing import Any, Optional


class TripletexClient:
    def __init__(self, base_url: str, session_token: str, timeout: float = 30.0):
        # Normalize base_url – strip trailing slash
        self.base_url = base_url.rstrip("/")
        self.auth = ("0", session_token)
        self.timeout = timeout
        self._client = httpx.Client(
            auth=self.auth,
            timeout=self.timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        resp = self._client.get(self._url(path), params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, body: dict) -> dict:
        resp = self._client.post(self._url(path), json=body)
        resp.raise_for_status()
        return resp.json()

    def put(self, path: str, body: dict, params: Optional[dict] = None) -> dict:
        resp = self._client.put(self._url(path), json=body, params=params)
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        resp = self._client.delete(self._url(path), params=params)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"status": "deleted"}

    def close(self):
        self._client.close()

    # ─────────────────────────── EMPLOYEES ───────────────────────────

    def search_employees(self, **params) -> list[dict]:
        params.setdefault("fields", "id,firstName,lastName,email,employeeNumber,phoneNumberMobile,phoneNumberHome,phoneNumberWork")
        params.setdefault("count", 100)
        data = self.get("/employee", params=params)
        return data.get("values", [])

    def get_employee(self, employee_id: int) -> dict:
        return self.get(f"/employee/{employee_id}", params={"fields": "*"})["value"]

    def create_employee(self, payload: dict) -> dict:
        """Create employee. IMPORTANT: requires department.id and userType.
        Auto-fetches default department if not provided."""
        if "department" not in payload or not payload.get("department"):
            # Auto-fetch first available department
            depts = self.search_departments()
            if depts:
                payload["department"] = {"id": depts[0]["id"]}
        if "userType" not in payload:
            payload["userType"] = "STANDARD"
        return self.post("/employee", payload)["value"]

    def update_employee(self, employee_id: int, payload: dict) -> dict:
        return self.put(f"/employee/{employee_id}", payload)["value"]

    def delete_employee(self, employee_id: int) -> dict:
        return self.delete(f"/employee/{employee_id}")

    # Employment (ansettelsesforhold)
    def create_employment(self, payload: dict) -> dict:
        return self.post("/employee/employment", payload)["value"]

    def get_employments(self, employee_id: int) -> list[dict]:
        data = self.get("/employee/employment", params={"employeeId": employee_id, "fields": "*"})
        return data.get("values", [])

    # Employee roles
    def get_roles(self) -> list[dict]:
        data = self.get("/employee/employmentDetails/ocupationCode", params={"fields": "id,name", "count": 200})
        return data.get("values", [])

    # ─────────────────────────── CUSTOMERS ───────────────────────────

    def search_customers(self, **params) -> list[dict]:
        params.setdefault("fields", "id,name,email,organizationNumber,phoneNumber")
        params.setdefault("count", 100)
        data = self.get("/customer", params=params)
        return data.get("values", [])

    def get_customer(self, customer_id: int) -> dict:
        return self.get(f"/customer/{customer_id}", params={"fields": "*"})["value"]

    def create_customer(self, payload: dict) -> dict:
        payload.setdefault("isCustomer", True)
        return self.post("/customer", payload)["value"]

    def update_customer(self, customer_id: int, payload: dict) -> dict:
        return self.put(f"/customer/{customer_id}", payload)["value"]

    def delete_customer(self, customer_id: int) -> dict:
        return self.delete(f"/customer/{customer_id}")

    # Contacts linked to customer
    def search_contacts(self, **params) -> list[dict]:
        params.setdefault("fields", "id,firstName,lastName,email,phoneNumberMobile,customer")
        params.setdefault("count", 100)
        data = self.get("/contact", params=params)
        return data.get("values", [])

    def create_contact(self, payload: dict) -> dict:
        return self.post("/contact", payload)["value"]

    def update_contact(self, contact_id: int, payload: dict) -> dict:
        return self.put(f"/contact/{contact_id}", payload)["value"]

    # ─────────────────────────── PRODUCTS ───────────────────────────

    def search_products(self, **params) -> list[dict]:
        params.setdefault("fields", "id,name,number,costExcludingVatCurrency,priceExcludingVatCurrency,priceIncludingVatCurrency")
        params.setdefault("count", 100)
        data = self.get("/product", params=params)
        return data.get("values", [])

    def get_product(self, product_id: int) -> dict:
        return self.get(f"/product/{product_id}", params={"fields": "*"})["value"]

    def create_product(self, payload: dict) -> dict:
        return self.post("/product", payload)["value"]

    def update_product(self, product_id: int, payload: dict) -> dict:
        return self.put(f"/product/{product_id}", payload)["value"]

    # ─────────────────────────── ORDERS ───────────────────────────

    def search_orders(self, **params) -> list[dict]:
        params.setdefault("fields", "id,number,customer,orderDate,deliveryDate,isShowOpenPostsOnInvoices")
        params.setdefault("count", 100)
        data = self.get("/order", params=params)
        return data.get("values", [])

    def get_order(self, order_id: int) -> dict:
        return self.get(f"/order/{order_id}", params={"fields": "*,orderLines(*)"})["value"]

    def create_order(self, payload: dict) -> dict:
        return self.post("/order", payload)["value"]

    def update_order(self, order_id: int, payload: dict) -> dict:
        return self.put(f"/order/{order_id}", payload)["value"]

    def create_order_line(self, payload: dict) -> dict:
        return self.post("/order/orderline", payload)["value"]

    # ─────────────────────────── INVOICES ───────────────────────────

    def search_invoices(self, **params) -> list[dict]:
        params.setdefault("fields", "id,number,customer,invoiceDate,invoiceDueDate,amountExcludingVatCurrency,amountIncludingVatCurrency,isPaid")
        params.setdefault("count", 100)
        data = self.get("/invoice", params=params)
        return data.get("values", [])

    def get_invoice(self, invoice_id: int) -> dict:
        return self.get(f"/invoice/{invoice_id}", params={"fields": "*"})["value"]

    def create_invoice(self, payload: dict) -> dict:
        """
        Can embed orders directly or reference order IDs.
        payload example:
        {
            "invoiceDate": "2026-03-20",
            "invoiceDueDate": "2026-04-20",
            "customer": {"id": 123},
            "orders": [{"id": 456}]
        }
        """
        return self.post("/invoice", payload)["value"]

    def send_invoice(self, invoice_id: int, send_type: str = "EMAIL") -> dict:
        """send_type: EMAIL, EHF, EFAKTURA, VIPPS, PAPER, MANUAL"""
        return self.put(f"/invoice/{invoice_id}/:send", {}, params={"sendType": send_type})

    def register_payment(self, invoice_id: int, payment_date: str, amount: float,
                         payment_type_id: int = 1) -> dict:
        """Register payment on invoice."""
        return self.post("/invoice/payment", {
            "invoice": {"id": invoice_id},
            "paymentDate": payment_date,
            "amount": amount,
            "paymentTypeId": payment_type_id,
        }).get("value", {})

    def create_credit_note(self, invoice_id: int, date: str, send_to_customer: bool = False) -> dict:
        return self.put(f"/invoice/{invoice_id}/:createCreditNote", {},
                        params={"date": date, "sendToCustomer": send_to_customer})

    def delete_invoice(self, invoice_id: int) -> dict:
        return self.delete(f"/invoice/{invoice_id}")

    # ─────────────────────────── PAYMENT TYPES ───────────────────────────

    def get_payment_types(self) -> list[dict]:
        data = self.get("/ledger/paymentType", params={"fields": "id,name", "count": 50})
        return data.get("values", [])

    # ─────────────────────────── TRAVEL EXPENSES ───────────────────────────

    def search_travel_expenses(self, **params) -> list[dict]:
        params.setdefault("fields", "id,description,employee,travelDetails,departureDate,returnDate,isCompleted")
        params.setdefault("count", 100)
        data = self.get("/travelExpense", params=params)
        return data.get("values", [])

    def get_travel_expense(self, expense_id: int) -> dict:
        return self.get(f"/travelExpense/{expense_id}", params={"fields": "*"})["value"]

    def create_travel_expense(self, payload: dict) -> dict:
        return self.post("/travelExpense", payload)["value"]

    def update_travel_expense(self, expense_id: int, payload: dict) -> dict:
        return self.put(f"/travelExpense/{expense_id}", payload)["value"]

    def delete_travel_expense(self, expense_id: int) -> dict:
        return self.delete(f"/travelExpense/{expense_id}")

    def approve_travel_expense(self, expense_id: int) -> dict:
        return self.put(f"/travelExpense/{expense_id}/:approve", {})

    # Travel cost categories
    def get_travel_cost_categories(self) -> list[dict]:
        data = self.get("/travelExpense/costCategory", params={"fields": "id,name,isFoodAndBeverage,isAccommodation,isTransport", "count": 100})
        return data.get("values", [])

    # ─────────────────────────── PROJECTS ───────────────────────────

    def search_projects(self, **params) -> list[dict]:
        params.setdefault("fields", "id,name,number,customer,startDate,endDate,projectManager,department")
        params.setdefault("count", 100)
        data = self.get("/project", params=params)
        return data.get("values", [])

    def get_project(self, project_id: int) -> dict:
        return self.get(f"/project/{project_id}", params={"fields": "*"})["value"]

    def create_project(self, payload: dict) -> dict:
        return self.post("/project", payload)["value"]

    def update_project(self, project_id: int, payload: dict) -> dict:
        return self.put(f"/project/{project_id}", payload)["value"]

    def delete_project(self, project_id: int) -> dict:
        return self.delete(f"/project/{project_id}")

    # ─────────────────────────── DEPARTMENTS ───────────────────────────

    def search_departments(self, **params) -> list[dict]:
        params.setdefault("fields", "id,name,departmentNumber")
        params.setdefault("count", 100)
        data = self.get("/department", params=params)
        return data.get("values", [])

    def get_department(self, department_id: int) -> dict:
        return self.get(f"/department/{department_id}", params={"fields": "*"})["value"]

    def create_department(self, payload: dict) -> dict:
        return self.post("/department", payload)["value"]

    def update_department(self, department_id: int, payload: dict) -> dict:
        return self.put(f"/department/{department_id}", payload)["value"]

    # ─────────────────────────── COMPANY / MODULES ───────────────────────────

    def get_company_settings(self) -> dict:
        return self.get("/company", params={"fields": "*"})["value"]

    def get_modules(self) -> dict:
        return self.get("/company/settings/modules", params={"fields": "*"})["value"]

    def update_modules(self, payload: dict) -> dict:
        return self.put("/company/settings/modules", payload)["value"]

    # ─────────────────────────── LEDGER / VOUCHERS ───────────────────────────

    def search_vouchers(self, **params) -> list[dict]:
        params.setdefault("fields", "id,number,description,voucherType,date")
        params.setdefault("count", 100)
        data = self.get("/ledger/voucher", params=params)
        return data.get("values", [])

    def get_voucher(self, voucher_id: int) -> dict:
        return self.get(f"/ledger/voucher/{voucher_id}", params={"fields": "*"})["value"]

    def reverse_voucher(self, voucher_id: int, date: str) -> dict:
        return self.put(f"/ledger/voucher/{voucher_id}/:reverse", {}, params={"date": date})

    def delete_voucher(self, voucher_id: int) -> dict:
        return self.delete(f"/ledger/voucher/{voucher_id}")

    # ─────────────────────────── SUPPLIER INVOICE ───────────────────────────

    def search_supplier_invoices(self, **params) -> list[dict]:
        params.setdefault("fields", "id,invoiceNumber,supplier,invoiceDate,amountIncludingVatCurrency")
        params.setdefault("count", 100)
        data = self.get("/supplierInvoice", params=params)
        return data.get("values", [])

    def get_supplier_invoice(self, invoice_id: int) -> dict:
        return self.get(f"/supplierInvoice/{invoice_id}", params={"fields": "*"})["value"]

    # ─────────────────────────── SUPPLIERS ───────────────────────────

    def search_suppliers(self, **params) -> list[dict]:
        params.setdefault("fields", "id,name,email,organizationNumber")
        params.setdefault("count", 100)
        data = self.get("/supplier", params=params)
        return data.get("values", [])

    def create_supplier(self, payload: dict) -> dict:
        payload.setdefault("isSupplier", True)
        return self.post("/supplier", payload)["value"]

    def update_supplier(self, supplier_id: int, payload: dict) -> dict:
        return self.put(f"/supplier/{supplier_id}", payload)["value"]

    # ─────────────────────────── GENERIC ───────────────────────────

    def generic_get(self, path: str, params: Optional[dict] = None) -> Any:
        return self.get(path, params=params)

    def generic_post(self, path: str, body: dict) -> Any:
        return self.post(path, body)

    def generic_put(self, path: str, body: dict, params: Optional[dict] = None) -> Any:
        return self.put(path, body, params=params)

    def generic_delete(self, path: str, params: Optional[dict] = None) -> Any:
        return self.delete(path, params=params)
