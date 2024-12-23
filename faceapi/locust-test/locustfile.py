from locust import HttpUser, task
import json
import base64


image1 = open('/mnt/locust/request-data/1.jpg', 'rb')
image1 = base64.b64encode(image1.read()).decode('utf-8')
image2 = open('/mnt/locust/request-data/2.jpg', 'rb')
image2 = base64.b64encode(image2.read()).decode('utf-8')
contents_detect = open('/mnt/locust/request-data/detect.json', 'rb').read()
contents_detect = json.loads(contents_detect)
contents_detect["image"] = image1
contents_detect = json.dumps(contents_detect)
contents_quality = open('/mnt/locust/request-data/quality.json', 'rb').read()
contents_quality = json.loads(contents_quality)
contents_quality["image"] = image1
contents_quality = json.dumps(contents_quality)
contents_match = open('/mnt/locust/request-data/match.json', 'rb').read()
contents_match = json.loads(contents_match)
contents_match["images"][0]["data"] = image1
contents_match["images"][1]["data"] = image2
contents_match = json.dumps(contents_match)
contents_liveness = open('/mnt/locust/request-data/request.bin', 'rb').read()
contents_start_liveness = open('/mnt/locust/request-data/start-liveness-data.json', 'rb').read()
public_key = json.loads(contents_start_liveness)["publicKey"]
contents_search = open('/mnt/locust/request-data/search.json', 'rb').read()
contents_search = json.loads(contents_search)
contents_search["image"]["content"] = image2
contents_search = json.dumps(contents_search)


class UserDetect(HttpUser):
    @task
    def detect(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        self.client.post("/api/detect", data=contents_detect, headers=headers)


class UserQuality(HttpUser):
    @task
    def quality(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        self.client.post("/api/detect", data=contents_quality, headers=headers)


class UserMatch(HttpUser):
    @task
    def match(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        self.client.post("/api/match", data=contents_match, headers=headers)


class UserLiveness(HttpUser):
    @task
    def liveness(self):

        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        with self.client.post("/api/v2/liveness/start", data=contents_start_liveness, headers=headers) as response:
            res_json = json.loads(response.text)
            transaction_id = res_json["transactionId"]
            self.client.post(f"/api/v2/liveness?transactionId={transaction_id}",
                                          headers={'x-client-key': public_key}, data=contents_liveness, name="/api/v2/liveness")


class UserSearch(HttpUser):
    @task
    def search(self):
        self.client.verify = False

        headers = {'Content-Type': 'application/json'}

        self.client.post("/api/search", data=contents_search, headers=headers, name="/api/search")
