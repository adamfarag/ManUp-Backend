from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.task import TaskCreate, TaskCompletionResponse, TaskResponse
from app.services.level_service import calculate_level
from app.services.streak_service import calculate_streak
from app.services.community_service import create_activity
from app.utils.datetime_helpers import utc_now, today_str

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    """Get all tasks for the current user with today's completion status."""
    db = get_db()
    user_id = current_user["id"]
    today = today_str()

    cursor = db.tasks.find({"user_id": user_id})
    tasks = []

    async for task in cursor:
        task_id = str(task["_id"])

        # Check if this task was completed today
        completion = await db.task_completions.find_one({
            "user_id": user_id,
            "task_id": task_id,
            "date_str": today,
        })

        tasks.append(TaskResponse(
            id=task_id,
            name=task["name"],
            icon=task["icon"],
            category=task["category"],
            is_completed_today=completion is not None,
            user_id=user_id,
            created_at=task["created_at"],
        ))

    return tasks


@router.post(
    "/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_tasks(
    tasks_data: list[TaskCreate],
    current_user: dict = Depends(get_current_user),
):
    """Create tasks in batch (accepts an array)."""
    db = get_db()
    user_id = current_user["id"]
    now = utc_now()

    created_tasks = []
    for task_data in tasks_data:
        doc = {
            "user_id": user_id,
            "name": task_data.name,
            "icon": task_data.icon,
            "category": task_data.category,
            "created_at": now,
        }
        result = await db.tasks.insert_one(doc)
        created_tasks.append(TaskResponse(
            id=str(result.inserted_id),
            name=task_data.name,
            icon=task_data.icon,
            category=task_data.category,
            is_completed_today=False,
            user_id=user_id,
            created_at=now,
        ))

    return created_tasks


@router.put("/tasks/{task_id}/complete", response_model=TaskCompletionResponse)
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Mark a task as completed for today."""
    db = get_db()
    user_id = current_user["id"]
    today = today_str()
    now = utc_now()

    # Verify task exists and belongs to user
    try:
        task = await db.tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID",
        )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if already completed today
    existing = await db.task_completions.find_one({
        "user_id": user_id,
        "task_id": task_id,
        "date_str": today,
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already completed today",
        )

    # Create completion record
    completion_doc = {
        "user_id": user_id,
        "task_id": task_id,
        "date_str": today,
        "created_at": now,
    }
    result = await db.task_completions.insert_one(completion_doc)

    # Update user totals
    new_total = current_user.get("total_tasks_completed", 0) + 1
    new_level = calculate_level(new_total)

    # Set streak_start_date if not set
    update_fields = {
        "total_tasks_completed": new_total,
        "level": new_level,
        "updated_at": now,
    }
    if not current_user.get("streak_start_date"):
        update_fields["streak_start_date"] = today

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields},
    )

    # Calculate streak
    streak = await calculate_streak(db, user_id)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"streak_days": streak}},
    )

    # Create community activity
    await create_activity(
        db,
        user_id,
        "task_completed",
        f"{current_user['name']} completed \"{task['name']}\"",
        task.get("icon", ""),
    )

    return TaskCompletionResponse(
        id=str(result.inserted_id),
        task_id=task_id,
        user_id=user_id,
        date_str=today,
        streak_days=streak,
        total_tasks_completed=new_total,
        level=new_level,
        created_at=now,
    )


@router.put("/tasks/{task_id}/uncomplete", status_code=status.HTTP_200_OK)
async def uncomplete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Undo a task completion for today."""
    db = get_db()
    user_id = current_user["id"]
    today = today_str()
    now = utc_now()

    # Verify task exists and belongs to user
    try:
        task = await db.tasks.find_one({
            "_id": ObjectId(task_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID",
        )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Delete the completion record for today
    result = await db.task_completions.delete_one({
        "user_id": user_id,
        "task_id": task_id,
        "date_str": today,
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task was not completed today",
        )

    # Update user totals
    new_total = max(0, current_user.get("total_tasks_completed", 1) - 1)
    new_level = calculate_level(new_total)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "total_tasks_completed": new_total,
            "level": new_level,
            "updated_at": now,
        }},
    )

    # Recalculate streak
    streak = await calculate_streak(db, user_id)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"streak_days": streak}},
    )

    return {
        "message": "Task completion removed",
        "streak_days": streak,
        "total_tasks_completed": new_total,
        "level": new_level,
    }
