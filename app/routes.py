from fastapi import APIRouter

router = APIRouter()

# In-memory customer records
USERS = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "Customer",
        "status": "Active"
    },
    {
        "id": 2,
        "name": "Bob Smith",
        "email": "bob@example.com",
        "role": "Customer",
        "status": "Active"
    },
    {
        "id": 3,
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "role": "Customer",
        "status": "Pending"
    }
]


@router.get("/api/health")
def get_health():
    """Health check endpoint for runtime liveness."""
    return {
        "status": "healthy",
        "service": "sentinelops-patient"
    }


@router.get("/api/users")
def get_users():
    """Retrieve all customer records."""
    return USERS


@router.get("/api/user/{user_id}")
def get_user_by_id(user_id: int):
    """
    Lookup customer by unique identifier.

    Contains an intentional software defect:
    When user_id does not exist (e.g. 999), matching is empty.
    Accessing index 0 triggers an unhandled IndexError.
    """
    matching = [u for u in USERS if u["id"] == user_id]

    # SENTINELOPS_TEST_BUG
    if not matching:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return matching[0]
