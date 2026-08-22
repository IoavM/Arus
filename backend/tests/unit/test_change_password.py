import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_change_password_flow(client: AsyncClient):
    # 0. Register company to get an active user and token
    reg_payload = {
        "company_name": "Empresa Password Test",
        "tax_id": "900555444",
        "owner_name": "Propietario Password",
        "email": "password_user@test.com",
        "password": "initialpassword123"
    }
    reg_res = await client.post("/api/v1/auth/register-company", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    token = reg_data["access_token"]
    user_id = reg_data["user"]["id"]
    tenant_id = reg_data["user"]["tenant_id"]
    role_id = reg_data["user"]["role_id"]

    headers = {"Authorization": f"Bearer {token}"}

    # (5) POST /api/v1/auth/change-password sin header Authorization -> HTTP 401
    unauth_res = await client.post("/api/v1/auth/change-password", json={
        "current_password": "initialpassword123",
        "new_password": "newpassword456"
    })
    assert unauth_res.status_code == 401

    # (1) current_password incorrecta -> HTTP 400, la contraseña no cambia
    wrong_pwd_res = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrongpassword999", "new_password": "newpassword456"},
        headers=headers
    )
    assert wrong_pwd_res.status_code == 400
    assert "incorrecta" in wrong_pwd_res.json()["detail"].lower()

    # Verify old password still works for login after failed attempt
    login_old_check = await client.post("/api/v1/auth/login", json={
        "email": "password_user@test.com",
        "password": "initialpassword123"
    })
    assert login_old_check.status_code == 200

    # (2) cambio exitoso con current_password correcta y new_password válida -> HTTP 200
    success_res = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "initialpassword123", "new_password": "newpassword456"},
        headers=headers
    )
    assert success_res.status_code == 200
    assert "actualizada" in success_res.json()["message"].lower()

    # (3) tras el cambio, POST /api/v1/auth/login con la nueva contraseña -> HTTP 200, mismo role_id/tenant_id
    login_new_res = await client.post("/api/v1/auth/login", json={
        "email": "password_user@test.com",
        "password": "newpassword456"
    })
    assert login_new_res.status_code == 200
    login_new_data = login_new_res.json()
    assert login_new_data["user"]["id"] == user_id
    assert login_new_data["user"]["tenant_id"] == tenant_id
    assert login_new_data["user"]["role_id"] == role_id

    # (4) tras el cambio, login con la contraseña anterior -> HTTP 401
    login_old_res = await client.post("/api/v1/auth/login", json={
        "email": "password_user@test.com",
        "password": "initialpassword123"
    })
    assert login_old_res.status_code == 401
