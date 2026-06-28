# Asset Management System - ASM 
* Discovers and tracks an organization’s internet-facing assets (domains, subdomains, IP addresses, exposed services, TLS certificates, and the technologies running on them)
*  The system of record that ingests discovered assets, removes duplicates, tracks each asset’s lifecycle and relationships, and exposes everything for querying, analysis, and reporting.
* Tech Stack: **Python · FastAPI · PostgreSQL · Dcoker**

## Features ✨
* **Bulk** Operations
* **Deduplication**
* Relationship **graph**
* **Lifecycle** handling for expiry dates 
* **Automated Testing**
* **JWT** Authentication

## Setup and Run Instructions 🏃
* Git clone the repo 🗃️
* Ensure Docker is installed 🐋
* Create two cloud deployed database (prod-db, test-db) ☁️🛢️
* Create .env file and fill the following ✍
  * ````
    DB_CONNECTION = ""
    TEST_DB_CONNECTION = ""
    SECRET_KEY = "" 
    ALGORITHM = "HS256"
    EXP_MINUTES = 30
    ````
  * Add **public** urls of the databases
* Run App🏃
```bash
docker compose up --build
```
* Run Tests 
```
docker compose run --rm web pytest
```

## Design Decisions
* Database Design
  * <img width="797" height="647" alt="image" src="https://github.com/user-attachments/assets/e972e175-0a3f-4dec-9702-2995638b486c" />
---
* Dataset Assumptions
  * <img width="1097" height="657" alt="image" src="https://github.com/user-attachments/assets/75730cc4-952f-4ba2-8bf8-0a7834c38f92" />
---
* Relationships and Graph Assumptions
  * <img width="835" height="552" alt="image" src="https://github.com/user-attachments/assets/0ef31a90-19bf-4f7d-8f0a-70049cbd7464" />
---
* Other Strategies (Filtering, Tagging, Searching, Deduplication and Merging) 
  * <img width="972" height="502" alt="image" src="https://github.com/user-attachments/assets/e1e5868b-c7a4-4eb8-9f6c-4bb8db3d23ad" />
---
* Other Edge Cases
  * <img width="816" height="592" alt="image" src="https://github.com/user-attachments/assets/25caf662-ed43-42a6-9af8-3620727b2f02" />
---

## Api Documentation 📑
* Full Documentation
    * Documented dynmaic status Codes using additional responses ✅
    * Injected scheme forces the Authorize button to appear in /docs 🔐
```http
  http://127.0.0.1:8000/docs
```

## Test Results
* <img width="692" height="67" alt="image" src="https://github.com/user-attachments/assets/acb0b798-6b61-4ae7-bdf4-76d1c9853d10" />


## Top Do 📌
* Multi-tenant Isolation

## References
* [How to Implement Bulk Operations in REST APIs✨](https://oneuptime.com/blog/post/2026-01-27-rest-api-bulk-operations/view)
* [Building Dynamic API Responses with Generics in FastAPI✨](https://medium.com/@jkishan421/building-dynamic-api-responses-with-generics-in-fastapi-972fa1f52d54)
* [How to Design RESTful APIs Following Best Practices](https://oneuptime.com/blog/post/2026-01-26-restful-api-best-practices/view)
* [REST API Design Best Practices for Production Services](https://oneuptime.com/blog/post/2026-02-20-api-design-rest-best-practices/view)
