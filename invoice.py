

def invoice_json(self):
    self.so = Write code to retrieve sale order
    return {
        "type": {
            "name": "810_INVOICE"
        },
        "stream": "test",  # This need to be obtained from settings
        "sender": {
            "isaId": self.get_sender()
        },
        "receiver": {
            "isaId": self.get_receiver()
        },
        "message": {
            "transactionSets": [
                {
                    "beginningSegmentForInvoice": [
                        {
                            "date": self.current_date,
                            "invoiceNumber": "INV0414A",  # Hard coded for now
                            "purchaseOrderNumber": self.so.po_no
                        }
                    ],
                    "N1_loop": self.get_bill_to_address,
                    "termsOfSaleDeferredTermsOfSale": [
                        {
                            "termsTypeCode": "01",
                            "termsBasisDateCode": "3",
                            "termsDiscountPercent": ".01",
                            "termsDiscountDueDate": "20220719",
                            "termsDiscountDaysDue": "35",
                            "termsNetDueDate": "20220720",
                            "termsNetDays": "36",
                            "description": "1% 35 net36 days"
                        }
                    ],
                    "IT1_loop": invoice_items_array,
                    "totalMonetaryValueSummary": [
                        {
                            "amount": "455400"
                        }
                    ],
                    "transactionTotals": [
                        {
                            "numberOfLineItems": "3",
                            "hashTotal": "30"
                        }
                    ]
                }
            ]
        }
    }
def get_sender(self):
    return self.so.up_sender
def get_receiver(self):
    return self.so.up_receiver
def current_date(self):
    return current_date
def get_bill_to_address(self):
    bill_to = self.so.bill_to_address  # Need to add query here
    bill_to_array = []
    name = bill_to.name
    address1 = bill_to.address1
    address2 = bill_to.address2
    city = bill_to.city
    state = bill_to.state
    zip = bill_to.postal_code
    bill_to = []
    bill_to_party = {}
    party_identification_arr = []
    party_location_arr = []
    geographic_location_arr = []
    party_identification_dict = {}
    party_location_dict = {}
    geographic_location_dict = {}
    party_identification_dict['entityIdentifierCode'] = 'BT'
    party_identification_dict['name'] = name
    party_location_dict['addressInformation'] = address1
    party_location_dict['addressInformation1'] = address2
    geographic_location_dict['cityName'] = city
    geographic_location_dict['stateOrProvinceCode'] = state
    geographic_location_dict['postalCode'] = zip
    party_identification_arr.append(party_identification_dict)
    party_location_arr.append(party_location_dict)
    party_identification_arr.append(geographic_location_dict)
    bill_to_party['partyIdentification'] = party_identification_arr
    bill_to_party['partyLocation'] = party_location_arr
    bill_to_party['geographicLocation'] = geographic_location_arr
    bill_to.append(bill_to_party)
    return bill_to
def invoice_items_array(self):
    self.items = so.items
    index = 0
    items_array = []
    for item in self.items:
        print(item)
        index += 1
        item_whole_dict = {}
        item_array = []
        item_dict = {}
        item_dict['assignedIdentification'] = str(index)
    item_dict['quantityInvoiced'] = item.qty
    item_dict['unitOrBasisForMeasurementCode'] = item.uom
    item_dict['unitPrice'] = item.price
    item_dict['productServiceIDQualifier'] = item.new field
    item_dict['productServiceID'] = item.new field
    item_array.append(item_dict)
    item_whole_dict["baselineItemDataInvoice"] = item_array
    items_array.append(item_whole_dict)
    return items_array