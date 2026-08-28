import uuid
from datetime import UTC, datetime

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "hunter2hunter2",
            "display_name": "Sync Test",
            "timezone": "Europe/Tallinn",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_push_then_pull_round_trip(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-round-trip@example.com")
    goal_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    push_payload = {
        "goals": [
            {
                "id": goal_id,
                "user_id": (
                    await client.get("/auth/me", headers=headers)
                ).json()["id"],
                "parent_id": None,
                "title": "Learn Rust",
                "description": None,
                "target_date": None,
                "status": "active",
                "completed_at": None,
                "sort_order": 0,
                "created_at": now,
                "updated_at": now,
                "deleted_at": None,
            }
        ]
    }

    push_response = await client.post("/sync", json=push_payload, headers=headers)
    assert push_response.status_code == 204

    pull_response = await client.get("/sync", headers=headers)
    assert pull_response.status_code == 200
    body = pull_response.json()
    assert any(goal["id"] == goal_id for goal in body["goals"])
