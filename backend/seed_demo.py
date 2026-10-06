import asyncio
from datetime import datetime, date, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.auth.password import hash_password

async def seed_demo_data():
    print("Initializing demo data seeding for MongoDB...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]

    now = datetime.now(timezone.utc)
    today = date.today()

    # 1. Create or update Demo Student user
    demo_email = "student@demo.com"
    demo_pass = "password123"

    existing_user = await db.users.find_one({"email": demo_email})
    if existing_user:
        user_id = str(existing_user["_id"])
        print(f"Demo user already exists: {demo_email} (ID: {user_id})")
    else:
        user_doc = {
            "name": "Demo Student",
            "email": demo_email,
            "password": hash_password(demo_pass),
            "created_at": now,
            "updated_at": now
        }
        res = await db.users.insert_one(user_doc)
        user_id = str(res.inserted_id)
        print(f"Created new demo user: {demo_email} (ID: {user_id})")

    # Clear existing demo user collections to make seed repeatable & clean
    await db.subjects.delete_many({"user_id": user_id})
    await db.topics.delete_many({"user_id": user_id})
    await db.events.delete_many({"user_id": user_id})
    await db.availability.delete_many({"user_id": user_id})
    await db.sessions.delete_many({"user_id": user_id})
    await db.questions.delete_many({})
    await db.quiz_attempts.delete_many({"user_id": user_id})

    # 2. Availability
    avail_doc = {
        "user_id": user_id,
        "monday": 2.5,
        "tuesday": 2.5,
        "wednesday": 2.0,
        "thursday": 2.5,
        "friday": 2.0,
        "saturday": 4.0,
        "sunday": 3.0,
        "created_at": now,
        "updated_at": now
    }
    await db.availability.insert_one(avail_doc)

    # 3. Subjects
    sub1 = await db.subjects.insert_one({
        "user_id": user_id,
        "name": "Data Structures & Algorithms",
        "description": "Core CS curriculum covering arrays, trees, graphs, and complexity.",
        "color": "#0284c7",  # Sky/Teal Accent
        "created_at": now,
        "updated_at": now
    })
    sub1_id = str(sub1.inserted_id)

    sub2 = await db.subjects.insert_one({
        "user_id": user_id,
        "name": "Database Management Systems",
        "description": "Relational algebra, SQL, indexing, transaction ACID properties.",
        "color": "#7c3aed",  # Purple Accent
        "created_at": now,
        "updated_at": now
    })
    sub2_id = str(sub2.inserted_id)

    sub3 = await db.subjects.insert_one({
        "user_id": user_id,
        "name": "Computer Networks",
        "description": "OSI model, TCP/IP stack, routing protocols, and socket programming.",
        "color": "#ea580c",  # Amber/Orange Accent
        "created_at": now,
        "updated_at": now
    })
    sub3_id = str(sub3.inserted_id)

    # 4. Exams / Events
    # Exam 1: Data Structures - Feasible (12 days away)
    exam1 = await db.events.insert_one({
        "user_id": user_id,
        "subject_id": sub1_id,
        "title": "Data Structures Midterm",
        "type": "exam",
        "due_date": datetime.combine(today + timedelta(days=12), datetime.min.time()),
        "description": "Covers Arrays, Linked Lists, Trees, Graph Traversal.",
        "created_at": now,
        "updated_at": now
    })

    # Exam 2: Computer Networks - INFEASIBLE / AT RISK (3 days away with heavy workload!)
    exam2 = await db.events.insert_one({
        "user_id": user_id,
        "subject_id": sub3_id,
        "title": "Computer Networks Final Exam",
        "type": "exam",
        "due_date": datetime.combine(today + timedelta(days=3), datetime.min.time()),
        "description": "Covers TCP/IP congestion control, subnetting, BGP, DNS protocols.",
        "created_at": now,
        "updated_at": now
    })

    # Assignment 1: Database ER Diagrams
    assign1 = await db.events.insert_one({
        "user_id": user_id,
        "subject_id": sub2_id,
        "title": "DBMS Assignment 1 (Normal Forms)",
        "type": "assignment",
        "due_date": datetime.combine(today + timedelta(days=5), datetime.min.time()),
        "description": "Submit BCNF and 3NF normalization proofs.",
        "created_at": now,
        "updated_at": now
    })

    # 5. Topics
    # Data Structures Topics
    ds_topics = [
        {"name": "Arrays & Dynamic Strings", "est_hours": 3.0, "difficulty": 2, "weight": 3, "mastery": 1.0, "status": "completed"},
        {"name": "Linked Lists & Doubly Lists", "est_hours": 3.5, "difficulty": 3, "weight": 4, "mastery": 0.85, "status": "completed"},
        {"name": "Binary Search Trees & AVL Trees", "est_hours": 5.0, "difficulty": 4, "weight": 5, "mastery": 0.35, "status": "in_progress"},
        {"name": "Graph Traversal (DFS & BFS)", "est_hours": 6.0, "difficulty": 5, "weight": 5, "mastery": 0.10, "status": "pending"},
        {"name": "Dynamic Programming Basics", "est_hours": 8.0, "difficulty": 5, "weight": 4, "mastery": 0.0, "status": "pending"}
    ]

    for t in ds_topics:
        t["user_id"] = user_id
        t["subject_id"] = sub1_id
        t["created_at"] = now
        t["updated_at"] = now
        res = await db.topics.insert_one(t)
        t["_id"] = res.inserted_id

    # DBMS Topics
    db_topics = [
        {"name": "Relational Algebra & SQL", "est_hours": 4.0, "difficulty": 2, "weight": 4, "mastery": 0.90, "status": "completed"},
        {"name": "Normalization (1NF to BCNF)", "est_hours": 5.0, "difficulty": 4, "weight": 5, "mastery": 0.50, "status": "in_progress"},
        {"name": "B-Trees & Hash Indexing", "est_hours": 4.0, "difficulty": 3, "weight": 3, "mastery": 0.0, "status": "pending"},
        {"name": "ACID Transactions & Concurrency", "est_hours": 6.0, "difficulty": 5, "weight": 5, "mastery": 0.0, "status": "pending"}
    ]

    for t in db_topics:
        t["user_id"] = user_id
        t["subject_id"] = sub2_id
        t["created_at"] = now
        t["updated_at"] = now
        res = await db.topics.insert_one(t)
        t["_id"] = res.inserted_id

    # Computer Networks Topics (HEAVY WORKLOAD FOR 3 DAYS -> Demonstrates INFEASIBILITY & TRIAGE!)
    cn_topics = [
        {"name": "IP Subnetting & CIDR Notation", "est_hours": 6.0, "difficulty": 4, "weight": 5, "mastery": 0.20, "status": "in_progress"},
        {"name": "TCP Congestion Control & Sliding Window", "est_hours": 7.0, "difficulty": 5, "weight": 5, "mastery": 0.10, "status": "pending"},
        {"name": "BGP & OSPF Routing Protocols", "est_hours": 6.0, "difficulty": 4, "weight": 4, "mastery": 0.0, "status": "pending"},
        {"name": "DNS & Application Layer Security", "est_hours": 5.0, "difficulty": 3, "weight": 2, "mastery": 0.0, "status": "pending"}, # Low ratio -> prime target for triage drop!
        {"name": "Socket Programming & TLS Handshake", "est_hours": 4.0, "difficulty": 3, "weight": 2, "mastery": 0.0, "status": "pending"} # Low ratio -> prime target for triage compress!
    ]

    for t in cn_topics:
        t["user_id"] = user_id
        t["subject_id"] = sub3_id
        t["created_at"] = now
        t["updated_at"] = now
        res = await db.topics.insert_one(t)
        t["_id"] = res.inserted_id

    # 6. Sample Past Sessions (Completed & Missed for velocity modeling)
    past_sessions = [
        # Sub1 past session: planned 60m, actual 90m (velocity ~ 1.5 - slower student)
        {
            "user_id": user_id,
            "subject_id": sub1_id,
            "topic_id": str(ds_topics[0]["_id"]),
            "planned_date": (today - timedelta(days=2)).isoformat(),
            "planned_minutes": 60,
            "actual_minutes": 90,
            "status": "done",
            "type": "study",
            "created_at": now,
            "updated_at": now
        },
        # Sub1 missed session
        {
            "user_id": user_id,
            "subject_id": sub1_id,
            "topic_id": str(ds_topics[1]["_id"]),
            "planned_date": (today - timedelta(days=1)).isoformat(),
            "planned_minutes": 60,
            "actual_minutes": 0,
            "status": "missed",
            "type": "study",
            "created_at": now,
            "updated_at": now
        },
        # Sub3 past session: planned 60m, actual 75m
        {
            "user_id": user_id,
            "subject_id": sub3_id,
            "topic_id": str(cn_topics[0]["_id"]),
            "planned_date": (today - timedelta(days=1)).isoformat(),
            "planned_minutes": 60,
            "actual_minutes": 75,
            "status": "done",
            "type": "study",
            "created_at": now,
            "updated_at": now
        }
    ]
    await db.sessions.insert_many(past_sessions)

    # 7. Generate Initial Adaptive Schedule using Scheduler Service
    from app.services.scheduler import run_scheduler
    from app.services.velocity import get_all_subject_velocities

    all_topics = ds_topics + db_topics + cn_topics
    all_events = [
        {"id": str(exam1.inserted_id), "subject_id": sub1_id, "title": "Data Structures Midterm", "due_date": today + timedelta(days=12), "type": "exam"},
        {"id": str(exam2.inserted_id), "subject_id": sub3_id, "title": "Computer Networks Final Exam", "due_date": today + timedelta(days=3), "type": "exam"}
    ]

    vel_map = get_all_subject_velocities(past_sessions)
    new_planned_sessions, feasibility_report = run_scheduler(
        topics=all_topics,
        events=all_events,
        availability=avail_doc,
        velocity_map=vel_map,
        today=today,
        buffer_ratio=0.20
    )

    to_insert_sessions = []
    for s in new_planned_sessions:
        s["user_id"] = user_id
        s["created_at"] = now
        s["updated_at"] = now
        to_insert_sessions.append(s)

    if to_insert_sessions:
        await db.sessions.insert_many(to_insert_sessions)

    client.close()
    print("\n==================================================")
    print("   DEMO SEED COMPLETED SUCCESSFULLY! ")
    print("==================================================")
    print(f" Demo User Email    : {demo_email}")
    print(f" Demo User Password : {demo_pass}")
    print(f" Total Subjects     : 3")
    print(f" Total Topics       : {len(all_topics)}")
    print(f" Planned Sessions   : {len(to_insert_sessions)}")
    print(f" Infeasible Exam    : Computer Networks Final Exam (3 days left)")
    print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
