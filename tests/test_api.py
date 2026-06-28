from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.main import app
from src.utils.db import get_db, Base
import pytest
from tests.test_data import *
from tests.helpers import *
from src.utils.settings import settings

import logging
logging.basicConfig(level=logging.INFO)

client = TestClient(app)


engine = create_engine(url=settings.TEST_DB_CONNECTION)
TestSession = sessionmaker(bind=engine)

def override_get_db():
    session = TestSession()
    try: 
        yield session
    finally:
        session.close()

app.dependency_overrides[get_db] = override_get_db

# --------------- Setup (DB, Token)---------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def auth_token(setup_test_db):  
    # Register 
    name = "Lea Ashley"
    username = "lea"
    email = "lea@gmail.com"
    password = "1234Aa$$"
    response = client.post(
        "/auth/register",
        json={"name": name,"username": username,"email": email,"password": password},
    )
       
    # Login
    response = client.post(
        "/auth/login",
        json={"email": email,"password": password},
    )
    data = response.json()
    return data["token"]

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture(scope="session", autouse=True)
def init_test_db(auth_headers):
    # 1) Bulk Create Assets 
    response = client.post(
        "/assets/bulk-create",
        json = bulk_related_assets_json,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # 2) Bulk Create Relationships
    response = client.post(
        "/relationships/bulk-create",
        json = bulk_related_assets_json,
        headers=auth_headers
    )
    assert response.status_code == 200


# --------------- Dedpulication Test ---------------

def test_dedup_same_asset(auth_headers):
    
    # 1) Create Asset
    response = client.post(
        "/assets",
        json = asset_req_json,
        headers=auth_headers
    )
    # 2) Assert(status code, response)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["status"] == "Created"
    assert_json_equal(asset_req_json, data["data"])      # assert response is same as request body

    # 3) Recreate Same Duplicate
    response = client.post(
        "/assets",
        json = asset_req_json,
        headers=auth_headers
    )

    # 4) Assert(status code, response)
    assert response.status_code == 200, response.text
    
    assert response.json()["status"] == "Updated"
    data = response.json()["data"]
    assert data["first_seen"] != data["last_seen"]   # ensure last seen is updated
    assert_json_equal(asset_req_json, data)      # assert everything is the same (id,...)

    # 5) Cleanup (Delete Asset) 
    response = client.delete(
        f"/assets/{asset_req_json['id']}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_dedup_mrege_asset(auth_headers):
    
    # 1) Create Asset
    response = client.post(
        "/assets",
        json = asset_req_json,
        headers=auth_headers
    )


    # 2) Create Updated
    response = client.post(
        "/assets",
        json = updated_asset_req_json,
        headers=auth_headers
    )

    # 3) Assert correct dedup(status code, response: status, source tags, meta)
    assert response.status_code == 200, response.textcx
    assert response.json()["status"] == "Updated"
    data = response.json()["data"]
    assert data["id"] == merged_expected_res_json["id"] # same id nothing new
    assert data["first_seen"] != data["last_seen"]   # ensure last seen is updated
    assert data["status"] == merged_expected_res_json["status"] # updated status
    assert data["source"] == merged_expected_res_json["source"] # updated source
    assert set(data["tags"]) == set(merged_expected_res_json["tags"]) # merged tags
    assert_json_equal(merged_expected_res_json["metadata"], data["meta"]) # merged metadata

    # 4) Cleanup (Delete Asset) 
    response = client.delete(
        f"/assets/{asset_req_json['id']}",
        headers=auth_headers
    )
    assert response.status_code == 204
 
# --------------- Filter Test (DB, Token)---------------

def test_filter_by_value(auth_headers):
    # 1) Filter asset by value = ex
    response = client.get(
        "/assets/?value=ex",
        headers=auth_headers
    )
    # 2) Check response contains filtered ids
    expected_ids = filter_value_ex_ids
    response_ids = [item["id"] for item in response.json()["data"]]
    assert set(expected_ids) == set(response_ids)

def test_filter_by_value_and_tag(auth_headers):
    # 1) Filter asset by value = ex & tags=pub 
    response = client.get(
        "/assets/?value=ex&tags=pub",
        headers=auth_headers
    )

    # 2) Check response contains filtered ids
    expected_ids = filter_value_ex_tags_pub_ids
    response_ids = [item["id"] for item in response.json()["data"]]
    assert set(expected_ids) == set(response_ids)

def test_filter_by_value_and_two_tags(auth_headers):
    # 1) Filter asset by value = ex & tags=pub & tags = root
    response = client.get(
        "/assets/?value=ex&tags=pub&tags=root",
        headers=auth_headers
    )

    # 2) Check response contains filtered ids
    expected_ids = filter_value_ex_tags_pub_root_ids
    response_ids = [item["id"] for item in response.json()["data"]]
    assert set(expected_ids) == set(response_ids)

def test_sort_desc_by_id(auth_headers):
    # 1) Sort Descending By First_seen
    response = client.get(
        "/assets/?sort=id&order=desc",
        headers=auth_headers
    )
    
    # 2) Check response contains filtered ids in SAME ORDER
    expected_ids = sort_desc_by_first_seen_ids
    response_ids = [item["id"] for item in response.json()["data"]]
    print(response_ids)
    assert expected_ids == response_ids
    
# --------------- Grpah Relationship ---------------

def test_graph(auth_headers):
    # 1) Relationships were created @ init_db
    response = client.get(
        "/graph?asset_id=a4",  # node in middle
        headers=auth_headers
    )
    # assert response.status_code==201, response.json()
    # 2) Assert Correct Graph/Tree Hierarchy
    assert_graph_equal(expected_graph_ids, response.json())



