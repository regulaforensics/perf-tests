"""IDV perf scenario: view search and get each session by ID."""

import json
import os

from locust import HttpUser, between, task


auth_credentials_path = os.getenv("AUTH_CREDENTIALS_PATH", "/mnt/locust/request-data/auth.json")
view_namespace = os.getenv("VIEW_NAMESPACE", "active-views-3")

try:
    with open(auth_credentials_path, "r") as file:
        auth_data = json.load(file)
        USER_ID = auth_data.get("user_id", "regula-idv")
        PASSWORD = auth_data.get("password", "t3stP@ss")
except (FileNotFoundError, json.JSONDecodeError):
    USER_ID = "regula-idv"
    PASSWORD = "t3stP@ss"


def extract_session_ids(payload):
    """Extract session IDs from sessions search response."""
    if isinstance(payload, dict):
        candidates = payload.get("items") or payload.get("records") or payload.get("data") or []
    elif isinstance(payload, list):
        candidates = payload
    else:
        candidates = []

    ids = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        session_id = item.get("id") or item.get("sessionId") or item.get("session_id")
        if session_id:
            ids.append(session_id)

    return list(dict.fromkeys(ids))


def build_search_payload(view_payload):
    """Build /api/sessions/search payload from the first namespace view item."""
    if not isinstance(view_payload, dict):
        return None

    items = view_payload.get("items") or []
    if not items or not isinstance(items[0], dict):
        return None

    view_item = items[0]
    view_value = view_item.get("value")
    if not isinstance(view_value, dict):
        return None

    workflows = view_value.get("workflows") or []
    if not isinstance(workflows, list):
        workflows = []

    return {
        "id": view_value.get("id") or view_item.get("key"),
        "title": view_value.get("title"),
        "description": view_value.get("description"),
        "workflows": workflows,
        "columns": view_value.get("columns") or [],
        "sort": [],
        "filter": {
            "op": "$and",
            "groups": [
                {
                    "op": "$and",
                    "conditions": [
                        {
                            "field": "workflow.id",
                            "op": "$in",
                            "value": workflows,
                        }
                    ],
                }
            ],
        },
        "groupIds": view_value.get("groupIds") or view_item.get("groupIds") or [],
        "userIds": view_value.get("userIds") or view_item.get("userIds") or [],
    }


class IDVViewGetByIdPerf(HttpUser):
    """Search sessions from view and retrieve each by session ID."""

    wait_time = between(1, 2)

    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @task(1)
    def view_search_and_get_by_id(self):
        with self.client.get(
            f"/api/views/namespaces/{view_namespace}?limit=100&skip=0",
            headers=self.headers,
            auth=(USER_ID, PASSWORD),
            catch_response=True,
            name="/api/views/namespaces/{namespace}",
        ) as view_response:
            if view_response.status_code != 200:
                view_response.failure(f"View fetch failed: {view_response.status_code}")
                return

            try:
                view_payload = view_response.json()
            except (json.JSONDecodeError, KeyError) as error:
                view_response.failure(f"Failed to parse view response: {error}")
                return

            search_payload = build_search_payload(view_payload)
            if not search_payload:
                view_response.failure("View response has no usable definition")
                return

            view_response.success()

        with self.client.post(
            "/api/sessions/search?limit=100",
            json=search_payload,
            headers=self.headers,
            auth=(USER_ID, PASSWORD),
            catch_response=True,
            name="/api/sessions/search",
        ) as search_response:
            if search_response.status_code != 200:
                search_response.failure(f"Session search failed: {search_response.status_code}")
                return

            try:
                session_ids = extract_session_ids(search_response.json())
            except (json.JSONDecodeError, KeyError) as error:
                search_response.failure(f"Failed to parse search response: {error}")
                return

            if not session_ids:
                search_response.failure("No sessions found in nightly view")
                return

            search_response.success()

        for session_id in session_ids:
            with self.client.get(
                f"/api/sessions/{session_id}",
                headers=self.headers,
                auth=(USER_ID, PASSWORD),
                catch_response=True,
                name="/api/sessions/{session_id}",
            ) as session_response:
                if session_response.status_code != 200:
                    session_response.failure(f"Session retrieval failed: {session_response.status_code}")
                    continue

                try:
                    payload = session_response.json()
                    response_id = payload.get("id") or payload.get("sessionId")
                    if response_id:
                        session_response.success()
                    else:
                        session_response.failure("Session payload has no id/sessionId")
                except (json.JSONDecodeError, KeyError) as error:
                    session_response.failure(f"Failed to parse session payload: {error}")


