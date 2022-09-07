from __future__ import unicode_literals
from time import sleep, strftime, strptime
from urllib import response
from wsgiref import headers
import datetime as DT
from numpy import indices
from requests.api import get
import frappe
import json
from datetime import datetime, timedelta
from erpnext import get_default_company
from frappe.utils import cstr, cint, nowdate, flt, now
from frappe import _
import requests
import math
from requests.exceptions import HTTPError
import upro_erp_integ
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice, make_delivery_note
from upro_erp_integ.uproerpinteg.doctype.b2b_log.b2b_log import make_b2b_log
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils.background_jobs import enqueue
import csv

b2b_settings = frappe.get_doc("B2B Settings")


# @frappe.whitelist()
# def create_bo():
#     bo = Blanket_Order()
#     frappe.set_user('Administrator')
#     data = json.loads(frappe.request.data)
#     orders = data["orders"]
#     response = bo.call(orders)
#     return response


@frappe.whitelist()
def create_so():
    b2b = B2B()
    frappe.set_user('Administrator')
    data = json.loads(frappe.request.data)
    make_b2b_log(
        status="Success", exception=data)
    orders = data['orders']
    response = b2b.call(orders)
    return response

# GET http://localhost:8000/api/method/upro_erp_integ.uproerpinteg.b2b.get_stock_status?item_code=10031&warehouse=Ohio - Columbus (USA) - UPIL
# Authorization to be added in header as "basic base64encodedtoken"
# Must add Accpet and Content-Type as application/json


@frappe.whitelist()
def get_stock_status():
    b2b = B2B()
    item_code = 'item_code'
    warehouse = 'warehouse'
    # validations
    if not item_code in frappe.form_dict:
        return json.dumps({'status': 'item_code is missing'})

    if not warehouse in frappe.form_dict:
        return json.dumps({'status': 'warehouse_name is missing'})

    if not frappe.form_dict[item_code]:
        return json.dumps({'status': 'item_code is missing'})

    if not frappe.form_dict[warehouse]:
        return json.dumps({'status': 'warehouse_name is missing'})

    ic = frappe.form_dict[item_code]
    parent_warehouse = frappe.form_dict[warehouse]
    response = b2b.get_stock_status(ic, parent_warehouse)
    return response

# GET http://localhost:8000/api/method/upro_erp_integ.uproerpinteg.b2b.get_items?days=2
# Authorization to be added in header as "basic base64encodedtoken"
# Must add Accpet and Content-Type as application/json


@frappe.whitelist()
def get_items():
    b2b = B2B()
    response = b2b.get_items_info()
    return response

# GET http://localhost:8000/api/method/upro_erp_integ.uproerpinteg.b2b.get_invoice_info?invoice_no=12345&item_qty=22&tracking_no=ABCDE


@frappe.whitelist()
def get_invoice_info():
    b2b = B2B()
    response = b2b.get_invoice_info()
    return response


class B2B:
    def _init_(self):
        self.orders = []

    def call(self, orders):
        try:
            self.orders = orders
            frappe.log_error(["Orders List", self.orders])
            for self.order in self.orders:
                if not self.order_exists():
                    self.customer_fname = ''
                    self.customer_lname = ''
                    self.items_arr = []
                    self.shipping_address = ''
                    self.billing_address = ''
                    self.items_in_sys = []
                    self.items_not_in_system = []
                    status = self.get_customer()
                    if status.get("Invalid"):
                        return status.get("Invalid")
                    else:
                        self.get_address()
                        self.get_items()
                        self.create_shipping_rule()
                        self.create_so()
                        return "Order Saved"
                else:
                    return "Order already exists"
        except Exception as err:
            make_b2b_log(
                status="Error", exception=str(err))

    def order_exists(self):
        order_id = self.order["purchase_order_no"]
        so_no = self.order["sales_order_number"]
        so = frappe.db.sql("""select name from `tabSales Order` where up_sales_order_number='{0}' or po_no = '{1}'""".format(
            so_no, order_id), as_dict=True)
        order_exists = False
        if so:
            order_exists = True
        return order_exists

    def get_customer(self):
        # Written based on the following scenarios
        # No new customer creation. Just mapping with existing customer or dummy customer
        # customer id "yes" first name "yes" last name "yes" - ok - map
        # customer id "yes and exists" first name "no" last name "no" - ok - map
        # customer id "yes and not exists" first name "no" last name "no" - can not create any customer with this name - Dummy customer with dummy names
        # customer id "No" first name "yes" last name "yes" - ok - Dummy customer with proper names
        # customer id "No and not exists" first name "no" last name "no" - can not create any customer with this name - Dummy customer with dummy names
        customer_info = self.order["customer_info"]
        customer_id = customer_info.get("id")
        company_name = self.order["customer_info"]["ship_to_address"]["company_name"]
        if company_name:
            if int(customer_id) > 0 or customer_id is not None:
                customer = frappe.db.get_value(
                    "Customer", {"up_b2b_customer_id": customer_id}, "customer_name")
                if customer:
                    self.customer = customer
                    self.customer_fname = customer
                    self.customer_lname = ""
                    self.company = company_name
                    return {"Valid": "Customer Has Been Created"}

                else:
                    if((customer_info.get("firstname") is None) or (customer_info.get("firstname") == "")) or ((customer_info.get("lastname") is None) or (customer_info.get("lastname") == "")):
                        make_b2b_log(
                            status="Error", exception="Customer Information Is Not Found")
                        return {"Invalid": "Customer Information Is Not Found"}
                    else:
                        self.customer_fname = customer_info.get("firstname")
                        self.customer_lname = customer_info.get("lastname")
                        self.customer = self.customer_fname + " " + self.customer_lname
                        new_cus = self.create_customer(customer_id)
                        new_cus.flags.ignore_mandatory = True
                        new_cus.insert(ignore_permissions=True)
                        self.customer = new_cus.customer_name
                        self.company = company_name
                        make_b2b_log(
                            status="Error", exception="Existing Customer not found and creating new customer")
                        return {"Valid": "Existing Customer not found and creating new customer"}

            else:
                self.customer = "Dummy Customer for B2B"
                self.customer_fname = "Dummy Customer for B2B"
                self.customer_lname = ""
                self.company = company_name
                return {"Valid": "Customer ID is Invalid"}
        else:
            return {"Invalid": "Company Name Is Required"}

    def create_customer(self, customer_id):
        import frappe.utils.nestedset
        frappe.set_user('Administrator')
        return frappe.get_doc({
            "doctype": "Customer",
            "name": customer_id,
            "customer_name": self.customer,
            "up_b2b_customer_id": customer_id,
            "territory": frappe.utils.nestedset.get_root_of("Territory"),
            "customer_type": _("Individual")
            # "customer_group": "1", #q what will be the customer group for B2B orders
        })

    def get_address(self):
        ship_to_details = self.order["customer_info"]["ship_to_address"]
        self.company_name = ship_to_details["company_name"]
        bill_to_details = self.order["customer_info"]["bill_to_address"]
        self.shipping_address = self.save_address(ship_to_details, "Shipping")
        self.billing_address = self.save_address(bill_to_details, "Billing")

    def save_address(self, address, type):
        try:
            doc = self.address_doc(address, type)
            doc.insert(ignore_mandatory=True)
            return doc.name
        except Exception as err:
            make_b2b_log(
                status="Error", exception="Error while creating Address" + str(err))

    def address_doc(self, address, atype):
        customer_country = address.get("country_id")
        doc = frappe.get_doc({
            "doctype": "Address",
            "address_type": atype,
            "address_line1": address.get("street"),
            "address_title": self.customer_fname + " " + self.customer_lname,
            "city": address.get("city"),
            "state": address.get("state"),
            "pincode": address.get("zip"),
            "phone": address.get("phone_number"),
            "country": customer_country,
            "represents_company": address.get("company_name"),
            "email_id": address.get("email"),
            "location_id": address.get("location_id"),
            "links": [{
                "link_doctype": "Customer",
                "link_name":  self.customer
            }]
        })
        return doc

    def get_items(self):
        order_items = self.order["items"]
        items_array = []
        for order_item in order_items:
            sku = order_item["item_code"]
            item = frappe.db.get_value("Item", {"item_code": sku}, "name")
            if item is None:
                mail_msg = " In B2B Order " + \
                    str(self.order.get("increment_id")) + \
                    " following are Invalid Line Item " + str(sku)
                make_b2b_log(status="Error", exception=mail_msg)
            else:
                price = flt(order_item.get("rate"))
                discount = 0
                induvidual_rate = price - discount
                cf = self.get_pan_details(str(order_item.get("item_code")))
                if cf is None:
                    pan_size = ''
                else:
                    pan_size = round(
                        float(float(order_item.get("qty"))/cf), 2)
                items_array.append({
                    "item_code": str(order_item.get("item_code")),
                    "item_name": order_item.get("item_name"),
                    "rate": induvidual_rate,
                    "up_pan_size": pan_size,
                    "up_customer_ship_to_date": self.order["shipment_date"],
                    # Note: This method to be added
                    "delivery_date": self.get_date_warehouse_lt(),
                    "qty": order_item.get("qty"),
                    "warehouse": self.get_item_level_warehouse(),
                })
        self.items_in_sys = items_array

    def get_pan_details(self, item_code):
        conversion_factor = frappe.get_value("UOM Conversion Detail", {
                                             "parent": item_code, "uom": "PAN"}, "conversion_factor")
        return conversion_factor

    def get_item_level_warehouse(self):
        return frappe.db.get_value("Item Warehouse Mapping", {"parent": "Default Warehouse Mapping", "physical_warehouse": self.order["physical_warehouse"]}, "default_storage_location")

    def get_date_warehouse_lt(self):
        shipment_date = self.order.get("shipment_date")
        shipment_date = datetime.strptime(shipment_date, '%Y-%m-%d').date()
        warehouse_doc = frappe.get_doc(
            "Warehouse", self.order.get("physical_warehouse"))
        get_lead_time_days = timedelta(
            days=warehouse_doc.up_warehouse_lead_time)
        delivery_date = shipment_date - get_lead_time_days
        return delivery_date

    def get_sales_person(self, agent_code):
        sales_person = None
        query = """select sales_person_name
                    from `tabSales Person`
                    where sales_person_name like "{0} - %";
                    """.format(agent_code)
        sales_person_arr = frappe.db.sql(query, as_dict=True)
        if len(sales_person_arr) != 0:
            sales_person = sales_person_arr[0]["sales_person_name"]
        return sales_person

    def create_shipping_rule(self):
        shipping_rule_name = self.order.get("shipment_via").strip()
        try:
            shipping_rule = frappe.db.get_value(
                "Shipping Rule", {"name": shipping_rule_name}, "name")
            if shipping_rule is None:
                sr = frappe.new_doc("Shipping Rule")
                sr.account = b2b_settings.bank_account
                sr.cost_center = b2b_settings.cost_center
                sr.label = shipping_rule_name
                sr.name = shipping_rule_name
                sr.insert(ignore_permissions=True)
                sr.submit()
                self.shipping_rule = sr.name
            else:
                self.shipping_rule = shipping_rule
        except Exception as err:
            make_b2b_log(status="Error",
                         exception=shipping_rule_name + str(err))

    def create_so(self):
        try:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "title": self.company_name,
                "up_sales_order_number": self.order.get("sales_order_number"),
                "up_sales_channel": self.order.get("sales_channel"),
                "up_company_name": self.company_name,
                "customer": self.customer,
                "po_no": self.order.get("purchase_order_no"),
                "up_b2b_shipment_date": self.order.get("shipment_date"),
                "delivery_date": self.order.get("delivery_date"),
                "items": self.items_in_sys,
                "up_b2b_special_instruction": self.order.get("special_instruction"),
                "up_sa1": self.get_sales_person(self.order.get('sales_agent_code')),
                "up_source_physical_warehouse": self.order.get("physical_warehouse"),
                "company": b2b_settings.company,
                "customer_address": self.billing_address,
                "shipping_address_name": self.shipping_address,
                "up_distribution_center": self.order.get("distribution_center"),
                "up_store_number": self.order.get("store_number"),
                "up_do_not_ship_before": self.order.get("do_not_ship_before"),
                "up_do_not_ship_after": self.order.get("do_not_ship_after"),
                "shipping_rule": self.shipping_rule
            })

            so.flags.ignore_mandatory = True
            so.save(ignore_permissions=True)
            so.submit()
            make_b2b_log(
                status="Success", exception="New sale order " + so.name + " created successfully")
            return so
        except Exception as err:
            make_b2b_log(
                status="Error", exception="Sale order creation err-" + str(err))

    def get_stock_status(self, ic, parent_warehouse):
        status = 'out of stock'
        whs = frappe.db.sql(""" WITH RECURSIVE top_down_cte AS ( SELECT M.name, M.is_group FROM tabWarehouse AS M WHERE M.name=%s UNION SELECT m.name, m.is_group FROM top_down_cte INNER JOIN tabWarehouse AS m ON top_down_cte.name = m.parent_warehouse )SELECT name FROM top_down_cte where is_group=0;""", (parent_warehouse), as_dict=1)
        warehouse_array = []
        for obj in whs:
            warehouse_array.append(obj.name)
        if not warehouse_array:
            return {'status': 'No child warehouse found'}

        query = """select item_code, sum(actual_qty) as qty
                        from `tabStock Ledger Entry`
                        where warehouse IN {0} AND item_code="{1}" group by item_code;
                        """.format(tuple(warehouse_array), ic)
        stock = frappe.db.sql(query, as_dict=True)

        query1 = """select warehouse, item_code, actual_qty as qty
                        from `tabStock Ledger Entry`
                        where warehouse IN {0} AND item_code="{1}";
                        """.format(tuple(warehouse_array), ic)

        stock_whwise = frappe.db.sql(query1, as_dict=True)

        if stock:
            if stock[0]['qty'] > 0:
                status = "in stock"
                return {'status': status, 'qty': stock[0]['qty'], 'items': stock_whwise}
            else:
                return {'status': status, 'qty': stock[0]['qty']}
        else:
            return {'status': 'Item not found'}

    def get_items_info(self):
        n_days = 7
        days = 'days'
        if days in frappe.form_dict:
            n_days = int(frappe.form_dict['days'])

        today = DT.date.today()
        week_ago = today - DT.timedelta(days=n_days)

        query = """select
                        i.item_code,
                        i.item_name,
                        i.description,
                        i.item_group as class_code,
                        i.up_msrp as msrp,
                        i.disabled,
                        i.up_pan_size as pan_size,
                        i.up_product_upc_bar_code as product_upc_bar_code,
                        i.up_us_hs_code as us_harmonized_code,
                        i.up_euro_hs_code as euro_harmonized_code,
                        i.up_abc_code as abc_code,
                        i.up_scc_14_bar_code as scc_14_bar_code,
                        ip.price_list_rate as master_price,
                        idi.case_weight_pounds,
                        idi.case_weight_kilograms,
                        idi.case_length_inches,
                        idi.case_length_centimeters,
                        idi.case_width_inches,
                        idi.case_width_centimeters,
                        idi.case_height_inches,
                        idi.case_height_centimeters,
                        idi.case_cube_cubic_feet,
                        idi.case_cube_cubic_meters,
                        idi.individual_length_inches,
                        idi.individual_length_centimeters,
                        idi.individual_width_inches,
                        idi.individual_width_centimeters,
                        idi.individual_height_inches,
                        idi.individual_height_centimeters,
                        i.weight_per_unit as individual_weight_pounds,
                        i.up_alternate_weight_per_unit as individual_weight_kilograms,
                        idi.individual_cube_cubic_feet,
                        u.uom,
                        u.conversion_factor
                        from `tabItem` i
                        left join `tabItem Price` ip on i.item_code=ip.item_code
                        left join `tabItem Dimensions` idi on i.item_code= idi.item
                        left join `tabUOM Conversion Detail` u on i.item_code = u.parent
                        where i.modified between '{0}' and '{1}' and ip.selling = '{2}'""".format(week_ago, today, int(1))

        items = frappe.db.sql(query, as_dict=True)
        return items

    def get_invoice_info(self):
        date = frappe.form_dict['date']
        response = []
        sale_invoices = frappe.db.get_list("Sales Invoice", {
                                           "posting_date": date, "up_sales_channel": ["in", ("B2B", "EDI")]}, ["name", "po_no"])
        for sale_invoice in sale_invoices:
            item_details = frappe.db.get_list(
                "Sales Invoice Item", {"parent": sale_invoice['name']}, ['*'])
            delivery_note_id = item_details[0]['delivery_note']
            if delivery_note_id is None:
                continue
            tracking_no = frappe.db.get_list("Packing Slip Shipment", {
                                             "parent": delivery_note_id}, ["tracking_number"])
            items = []
            for item in item_details:
                items.append({
                    "item_name": item.item_name,
                    "item_qty": item.qty
                })
            response.append({"invoice Number": sale_invoice['name'],
                             "item_details": items,
                             "purchase_order_no": sale_invoice['po_no'],
                             "tracking_info": tracking_no
                             })
        return response


# class Blanket_Order():

#     def __init__(self):
#         self.orders = []

#     def call(self, orders):
#         try:
#             self.orders = orders
#             frappe.log_error(["Order List", self.orders])
#             for self.order in self.orders:
#                 self.get_customer()
#                 self.get_address()
#                 self.get_items()
#                 self.get_sales_agent()
#                 self.create_bo()
#         except Exception as e:
#             frappe.log_error(["Error", "Error in call"])

#     def get_customer(self):
#         customer_info = self.order["customer_info"]
#         customer_id = customer_info.get("id")
#         if int(customer_id) > 0 or customer_id is not None:
#             customer = frappe.db.get_value(
#                 "Customer", {"up_b2b_customer_id": customer_id}, "customer_name")
#             if customer:
#                 self.customer = customer
#                 self.customer_fname = customer
#                 self.customer_lname = ""
#                 return {"Valid": "Customer Has Been Created"}

#             else:
#                 if((customer_info.get("firstname") is None) or (customer_info.get("firstname") == "")) or ((customer_info.get("lastname") is None) or (customer_info.get("lastname") == "")):
#                     make_b2b_log(
#                         status="Error", exception="Customer Information Is Not Found")
#                     return {"Invalid": "Customer Information Is Not Found"}
#                 else:
#                     self.customer_fname = customer_info.get("firstname")
#                     self.customer_lname = customer_info.get("lastname")
#                     self.customer = self.customer_fname + " " + self.customer_lname
#                     new_cus = self.create_customer(customer_id)
#                     new_cus.flags.ignore_mandatory = True
#                     new_cus.insert(ignore_permissions=True)
#                     self.customer = new_cus.customer_name
#                     make_b2b_log(
#                         status="Error", exception="Existing Customer not found and creating new customer")
#                     return {"Valid": "Existing Customer not found and creating new customer"}

#         else:
#             self.customer = "Dummy Customer for B2B"
#             self.customer_fname = "Dummy Customer for B2B"
#             self.customer_lname = ""
#             return {"Valid": "Customer ID is Invalid"}

#     def create_customer(self, customer_id):
#         import frappe.utils.nestedset
#         frappe.set_user('Administrator')
#         return frappe.get_doc({
#             "doctype": "Customer",
#             "name": customer_id,
#             "customer_name": self.customer,
#             "up_b2b_customer_id": customer_id,
#             "territory": frappe.utils.nestedset.get_root_of("Territory"),
#             "customer_type": _("Individual")
#             # "customer_group": "1", #q what will be the customer group for B2B orders
#         })

#     def get_address(self):
#         ship_to_details = self.order["customer_info"]["ship_to_address"]
#         self.shipping_address = self.save_address(ship_to_details, "Shipping")

#     def save_address(self, address, type):
#         try:
#             doc = self.address_doc(address, type)
#             doc.insert(ignore_mandatory=True)
#             return doc.name
#         except Exception as err:
#             make_b2b_log(
#                 status="Error", exception="Error while creating Address" + str(err))

#     def address_doc(self, address, atype):
#         customer_country = address.get("country_id")
#         doc = frappe.get_doc({
#             "doctype": "Address",
#             "address_type": atype,
#             "address_line1": address.get("street"),
#             "address_title": self.customer_fname + " " + self.customer_lname,
#             "city": address.get("city"),
#             "state": address.get("state"),
#             "pincode": address.get("zip"),
#             "phone": address.get("phone_number"),
#             "country": customer_country,
#             "represents_company": address.get("company_name"),
#             "email_id": address.get("email"),
#             "location_id": address.get("location_id"),
#             "links": [{
#                 "link_doctype": "Customer",
#                 "link_name":  self.customer
#             }]
#         })
#         return doc

#     def get_items(self):
#         item_list = self.order["items"]
#         self.item_array = []
#         try:
#             for item in item_list:
#                 item_name = frappe.get_list(
#                     "Item", {"name": item["item_code"]}, "name")
#                 if item_name:
#                     self.uom = item["uom"]
#                     cf = self.get_pan_details(item.get("item_code"))
#                     if cf is None:
#                         pan_size = ""
#                     else:
#                         pan_size = round(
#                             float(float(item.get("qty"))/cf), 2)
#                     self.item_array.append({
#                         "item_code": item.get("item_code"),
#                         "item_name": item.get("item_name"),
#                         "rate": item.get('rate'),
#                         "uom": item["uom"],
#                         "up_pan_size": pan_size,
#                         "qty": item["qty"],
#                         "warehouse": self.get_item_level_warehouse()
#                     })
#             return self.item_array
#         except Exception as e:
#             frappe.log_error(["ERROR", e])

#     def get_item_level_warehouse(self):
#         warehouse = frappe.get_value("Item Warehouse Mapping", {
#                                      "parent": "Default Warehouse Mapping", "physical_warehouse": self.order["physical_warehouse"]}, "default_storage_location")
#         return warehouse

#     def get_pan_details(self, item_code):
#         conversion_factor = frappe.get_value("UOM Conversion Detail", {
#                                              "parent": item_code, "uom": self.uom}, "conversion_factor")
#         return conversion_factor

#     def get_sales_agent(self):
#         try:
#             agent_code = self.order.get("sales_agent_code")
#             agent_code_name = frappe.get_value(
#                 "Sales Person", {"sales_person_name": agent_code}, "name")
#             if agent_code_name:
#                 self.agent = agent_code_name
#             else:
#                 agent = frappe.get_doc({
#                     "doctype": "Sales Person",
#                     "sales_person_name": agent_code
#                 })
#                 agent.flags.ignore_mandatory = True
#                 agent.save(ignore_permissions=True)
#                 self.agent = agent.sales_person_name
#         except Exception as e:
#             frappe.log_error(["SALES AGENT", e])

#     def create_bo(self):
#         try:
#             bo = frappe.get_doc({
#                 "doctype": "Blanket Order",
#                 "up_sales_channel": self.order.get("sales_channel"),
#                 "up_source_physical_warehouse": self.order.get("physical_warehouse"),
#                 "customer": self.customer,
#                 "items": self.item_array,
#                 "up_sa1": self.agent,
#                 "currency": self.order.get("currency"),
#                 "price_list_currency": self.order.get("currency"),
#                 "company_currency": self.order.get("currency"),
#                 "up_shipping_address_name": self.shipping_address
#             })
#             bo.flags.ignore_mandatory = True
#             bo.save(ignore_permissions=True)
#             return bo
#         except Exception as e:
#             return e

