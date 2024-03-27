from locust import HttpUser, task
import json
import base64

keys = open('/mnt/locust/request-data/keys.json', 'rb').read()
public_key = json.loads(keys)["publicKey"]
private_key = json.loads(keys)["privateKey"]
contents_reprocess = open('/mnt/locust/request-data/request.bin', 'rb').read()
image = open('/mnt/locust/request-data/test-doc.jpg', 'rb')
image = base64.b64encode(image.read()).decode('utf-8')
contents_process = open('/mnt/locust/request-data/process.json', 'rb').read()
contents_process = json.loads(contents_process)
contents_process["List"][0]["ImageData"]["image"] = image
contents_process = json.dumps(contents_process)


class UserOldApi(HttpUser):
    @task
    def process(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        self.client.post("/api/process", data=contents_process, headers=headers)


class UserApiV2(HttpUser):
    @task
    def backend_reprocess(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        with self.client.post("/api/v2/transaction/start", json={"privateKey": private_key, 'metadata': {}}, headers=headers) as response:
            res_json = json.loads(response.text)
            transaction_id = res_json["transactionId"]
            self.client.post(f"/api/v2/transaction/{transaction_id}", headers={'x-client-key': public_key},
                             data=contents_reprocess, name="/api/v2/transaction/{transactionId}")
            self.client.post(f"/api/v2/transaction/{transaction_id}/process",
                             headers=headers, json={"processParam": {"scenario": "FullAuth"}},
                             name="/api/v2/transaction/{transactionId}/process")
            self.client.get(f"/api/v2/transaction/{transaction_id}/results?withImages=true",
                            name="/api/v2/transaction/{transactionId}/results?withImages=true")


