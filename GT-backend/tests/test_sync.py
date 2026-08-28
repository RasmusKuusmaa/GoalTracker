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


async def _user_id(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.get("/auth/me", headers=headers)
    user_id: str = response.json()["id"]
    return user_id


def _goal_row(user_id: str, goal_id: str, updated_at: str) -> dict[str, object]:
    return {
        "id": goal_id,
        "user_id": user_id,
        "parent_id": None,
        "title": "Learn Rust",
        "description": None,
        "target_date": None,
        "status": "active",
        "completed_at": None,
        "sort_order": 0,
        "created_at": updated_at,
        "updated_at": updated_at,
        "deleted_at": None,
    }


async def test_push_then_pull_round_trip(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-round-trip@example.com")
    user_id = await _user_id(client, headers)
    goal_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    push_payload = {"goals": [_goal_row(user_id, goal_id, now)]}

    push_response = await client.post("/sync", json=push_payload, headers=headers)
    assert push_response.status_code == 200
    assert push_response.json()["goals"][0]["id"] == goal_id

    pull_response = await client.get("/sync", headers=headers)
    assert pull_response.status_code == 200
    body = pull_response.json()
    assert any(goal["id"] == goal_id for goal in body["goals"])


async def test_push_rejects_row_with_foreign_user_id(client: AsyncClient) -> None:
    headers = await _auth_headers(client, "sync-scope-foreign@example.com")
    other_headers = await _auth_headers(client, "sync-scope-other@example.com")
    other_user_id = await _user_id(client, other_headers)
    now = datetime.now(UTC).isoformat()
    push_payload = {"goals": [_goal_row(other_user_id, str(uuid.uuid4()), now)]}

    response = await client.post("/sync", json=push_payload, headers=headers)

    assert response.status_code == 403


async def test_push_rejects_id_collision_with_another_users_row(client: AsyncClient) -> None:
    owner_headers = await _auth_headers(client, "sync-collision-owner@example.com")
    owner_id = await _user_id(client, owner_headers)
    goal_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    await client.post(
        "/sync", json={"goals": [_goal_row(owner_id, goal_id, now)]}, headers=owner_headers
    )

    attacker_headers = await _auth_headers(client, "sync-collision-attacker@example.com")
    attacker_id = await _user_id(client, attacker_headers)
    later = datetime.now(UTC).isoformat()
    response = await client.post(
        "/sync",
        json={"goals": [_goal_row(attacker_id, goal_id, later)]},
        headers=attacker_headers,
    )

    assert response.status_code == 403
