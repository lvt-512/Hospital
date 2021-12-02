import sys

from flask_login import current_user
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
from paypalhttp import HttpError

from my_clinic import app, utils


class PayPalClient:
    def __init__(self):
        self.client_id = app.config["PAYPAL-SANDBOX-CLIENT-ID"]
        self.client_secret = app.config["PAYPAL-SANDBOX-CLIENT-SECRET"]

        """Set up and return PayPal Python SDK environment with PayPal access credentials.
           This sample uses SandboxEnvironment. In production, use LiveEnvironment."""

        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)

        """ Returns PayPal HTTP client instance with environment that has access
            credentials context. Use this instance to invoke PayPal APIs, provided the
            credentials have access. """
        self.client = PayPalHttpClient(self.environment)

    def object_to_json(self, json_data):
        """
        Function to print all json data in an organized readable manner
        """
        result = {}
        if sys.version_info[0] < 3:
            itr = json_data.__dict__.iteritems()
        else:
            itr = json_data.__dict__.items()
        for key, value in itr:
            # Skip internal attributes.
            if key.startswith("__"):
                continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else \
                self.object_to_json(value) if not self.is_primittive(value) else value
        return result

    def array_to_json_array(self, json_array):
        result = []
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if not self.is_primittive(item) else \
                                  self.array_to_json_array(item) if isinstance(item, list) else item)
        return result

    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, int)


class CreateOrder(PayPalClient):
    # 2. Set up your server to receive a call from the client
    """ This is the sample function to create an order. It uses the
      JSON body returned by buildRequestBody() to create an order."""

    def create_order(self, debug=False):
        request = OrdersCreateRequest()
        request.headers['prefer'] = 'return=representation'
        # 3. Call PayPal to set up a transaction
        request.request_body(self.build_request_body())
        try:
            # Call API with your client and get a response for your call
            response = self.client.execute(request)
            if debug:
                print('Status Code: ', response.status_code)
                print('Status: ', response.result.status)
                print('Order ID: ', response.result.id)
                print('Intent: ', response.result.intent)
                print('Links:')
                for link in response.result.links:
                    print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
                print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                                   response.result.purchase_units[0].amount.value))
            # If call returns body in response,
            # you can get the deserialized version from the result attribute of the response
            return response
        except IOError as ioe:
            print(ioe)
            if isinstance(ioe, HttpError):
                # Something went wrong server-side
                print(ioe.status_code)

        """Setting up the JSON request body for creating the order. Set the intent in the
        request body to "CAPTURE" for capture intent flow."""

    @staticmethod
    def build_request_body():
        """Method to create body with CAPTURE intent"""
        receipt = utils.get_request_payment(current_user.patient_id)
        items = []
        total_quantity, total_amount = 0, 0
        for item in receipt.details:
            items.append({
                "name": item.medicine.name,
                "sku": item.id,
                "unit_amount": {
                    "currency_code": "USD",
                    "value": item.unit_price
                },
                "quantity": item.quantity,
                "receipt_id": item.receipt_id
            })

            total_quantity += item.quantity
            total_amount += item.quantity * item.unit_price

        return \
            {
                "intent": "CAPTURE",
                "application_context": {
                    "brand_name": "EXAMPLE INC",
                    "landing_page": "BILLING",
                    "shipping_preference": "SET_PROVIDED_ADDRESS",
                    "user_action": "CONTINUE"
                },
                "purchase_units": [
                    {
                        "reference_id": "PUHF",
                        "description": "Sporting Goods",

                        "custom_id": "CUST-HighFashions",
                        "soft_descriptor": "HighFashions",
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{total_amount}",
                            "breakdown": {
                                "item_total": {
                                    "currency_code": "USD",
                                    "value": f"{total_amount}"
                                }
                            }
                        },
                        "items": items,
                        "shipping": {
                            "method": "United States Postal Service",
                            "address": {
                                "name": {
                                    "full_name": "John",
                                    "surname": "Doe"
                                },
                                "address_line_1": "123 Townsend St",
                                "address_line_2": "Floor 6",
                                "admin_area_2": "San Francisco",
                                "admin_area_1": "CA",
                                "postal_code": "94107",
                                "country_code": "US"
                            }
                        }
                    }
                ]
            }


class CaptureOrder(PayPalClient):
    # 2. Set up your server to receive a call from the client
    """this sample function performs payment capture on the order.
    Approved order ID should be passed as an argument to this function"""

    def capture_order(self, order_id, debug=False):
        """Method to capture order using order_id"""
        request = OrdersCaptureRequest(order_id)
        # 3. Call PayPal to capture an order
        try:
            # Call API with your client and get a response for your call
            response = self.client.execute(request)

            # 4. Save the capture ID to your database.
            # Implement logic to save capture to your database for future reference.
            if debug:
                print('Status Code: ', response.status_code)
                print('Status: ', response.result.status)
                print('Order ID: ', response.result.id)
                print('Links: ')
                for link in response.result.links:
                    print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
                print('Capture Ids: ')
                for purchase_unit in response.result.purchase_units:
                    for capture in purchase_unit.payments.captures:
                        print('\t', capture.id)
                print("Buyer:")
                print("\tEmail Address: {}\n\tName: {}\n\tPhone Number: {}" \
                      .format(response.result.payer.email_address,
                              response.result.payer.name.given_name, " ", response.result.payer.name.surname,
                              response.result.payer.phone.phone_number.national_number))

            return response

        except IOError as ioe:
            if isinstance(ioe, HttpError):
                # Something went wrong server-side
                print(ioe.status_code)
                print(ioe.headers)
                print(ioe)
            else:
                # Something went wrong client side
                print(ioe)


class GetOrder(PayPalClient):
    # 2. Set up your server to receive a call from the client
    """You can use this function to retrieve an order by passing order ID as an argument"""

    def get_order(self, order_id):
        """Method to get order"""
        request = OrdersGetRequest(order_id)
        # 3. Call PayPal to get the transaction
        response = self.client.execute(request)
        # 4. Save the transaction in your database.
        # Implement logic to save transaction to your database for future reference.
        print('Status Code: ', response.status_code)
        print('Status: ', response.result.status)
        print('Order ID: ', response.result.id)
        print('Intent: ', response.result.intent)
        print('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
        print('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                           response.result.purchase_units[0].amount.value))
