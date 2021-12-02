import base64
import hashlib
import hmac
import json
import urllib.request
import uuid

from flask_login import current_user

from my_clinic import utils, momo


class MoMo:
    def __init__(self):
        receipt = utils.get_request_payment(current_user.patient_id)
        momo["amount"] = str(int(utils.receipt_stats(receipt)["total_amount"]))
        momo["orderId"] = str(uuid.uuid4())
        momo["requestId"] = str(uuid.uuid4())
        # Additional information for order in the format: {'key': 'value'}
        extra_data = {"receipt": receipt.id}
        s = json.dumps(extra_data)  # Turns your json dict into a str
        # pass empty value or Encode base64 JsonString
        momo["extraData"] = base64.b64encode(s.encode('utf-8')).decode('utf-8')

    def payment_order(self):
        # json object send to MoMo endpoint
        data = {
            'partnerCode': momo["partnerCode"],
            'accessKey': momo["accessKey"],
            'requestId': momo["requestId"],
            'amount': momo["amount"],
            'orderId': momo["orderId"],
            'orderInfo': momo["orderInfo"],
            'returnUrl': momo["returnUrl"],
            'notifyUrl': momo["notifyUrl"],
            'requestType': momo["requestType"],
            'signature': self.raw_signature(),
            'extraData': momo["extraData"]
        }

        data = json.dumps(data)

        req = urllib.request.Request(momo["endpoint"], data.encode('utf-8'), {'Content-Type': 'application/json'})
        f = urllib.request.urlopen(req)

        response = f.read().decode('utf-8')  # convert bytes to string
        f.close()

        return json.loads(response)

    @staticmethod
    def raw_signature():
        # before sign HMAC SHA256 with format:
        raw_signature = "partnerCode=" + momo["partnerCode"] + \
                       "&accessKey=" + momo["accessKey"] + \
                       "&requestId=" + momo["requestId"] + \
                       "&amount=" + momo["amount"] + \
                       "&orderId=" + momo["orderId"] + \
                       "&orderInfo=" + momo["orderInfo"] + \
                       "&returnUrl=" + momo["returnUrl"] + \
                       "&notifyUrl=" + momo["notifyUrl"] + \
                       "&extraData=" + momo["extraData"]
        # signature
        h = hmac.new(momo["secretKey"].encode('utf-8'), raw_signature.encode('utf-8'), hashlib.sha256)
        signature = h.hexdigest()
        return signature
