import asyncio
import time
import argparse
import statistics
import httpx
from typing import List, Dict, Any

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"

async def register_student(client: httpx.AsyncClient, base_url: str, i: int) -> Dict[str, Any]:
    email = f"loadtest.student.{i}@university.edu"
    password = "StudentPassword@123"
    full_name = f"Load Student {i}"
    student_id = f"STU-LOAD-{i:05d}"
    device_uuid = f"DEV-UUID-LOAD-{i:05d}"

    # 1. Register student
    reg_res = await client.post(f"{base_url}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": "STUDENT",
        "student_id": student_id
    })
    
    if reg_res.status_code == 201:
        token = reg_res.json()["access_token"]
    else:
        # Try login if already registered
        log_res = await client.post(f"{base_url}/auth/login", json={
            "email": email,
            "password": password
        })
        token = log_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Register Device
    await client.post(f"{base_url}/devices/register", json={
        "device_uuid": device_uuid,
        "device_name": f"Test Phone {i}"
    }, headers=headers)

    return {
        "index": i,
        "token": token,
        "device_uuid": device_uuid,
        "headers": headers
    }

async def send_attendance_request(
    client: httpx.AsyncClient,
    base_url: str,
    student: Dict[str, Any],
    session_id: int,
    ble_token: str,
    rssi: int
) -> Dict[str, Any]:
    start_time = time.perf_counter()
    status_code = 0
    success = False
    error = None

    try:
        resp = await client.post(
            f"{base_url}/attendance/mark",
            json={
                "session_id": session_id,
                "token": ble_token,
                "device_uuid": student["device_uuid"],
                "rssi": rssi
            },
            headers=student["headers"],
            timeout=10.0
        )
        latency_ms = (time.perf_counter() - start_time) * 1000
        status_code = resp.status_code
        data = resp.json()
        success = data.get("success", False)
        msg = data.get("message", "")
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        error = str(e)

    return {
        "student_id": student["index"],
        "latency_ms": latency_ms,
        "status_code": status_code,
        "success": success,
        "error": error
    }

async def run_load_test(num_students: int, concurrency: int, base_url: str, in_process: bool = False):
    print(f"\n=======================================================")
    print(f" ProxyProof Load & Anti-Proxy Stress Benchmark")
    print(f" Concurrency: {concurrency} | Total Students: {num_students}")
    print(f" Target Mode: {'In-Process ASGI Engine' if in_process else base_url}")
    print(f"=======================================================\n")

    transport = None
    target_url = base_url
    if in_process:
        import sys, os
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from app.main import app
        from app.database import Base, engine, SessionLocal
        from app.utils.seed_data import seed_database
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        seed_database(db)
        db.close()
        transport = httpx.ASGITransport(app=app)
        target_url = "http://testserver/api/v1"

    limits = httpx.Limits(max_keepalive_connections=concurrency * 2, max_connections=concurrency * 4)
    async with httpx.AsyncClient(transport=transport, limits=limits, timeout=25.0) as client:
        # Step 1: Health check
        health = await client.get(f"{target_url}/health")
        if health.status_code != 200:
            print(f"[!] Target backend unreachable at {target_url}. Ensure backend is running.")
            return

        print("[+] Backend health verified: ONLINE")

        # Step 2: Login as Organizer and get or create active session
        login_res = await client.post(f"{target_url}/auth/login", json={
            "email": "prof.smith@university.edu",
            "password": "Admin@1234"
        })
        org_token = login_res.json()["access_token"]
        org_headers = {"Authorization": f"Bearer {org_token}"}

        # Create a fresh dedicated session for this benchmark run
        create_res = await client.post(f"{target_url}/sessions", json={
            "course_id": 1,
            "duration_minutes": 120,
            "rssi_threshold": -75,
            "token_rotation_interval": 30
        }, headers=org_headers)
        session_id = create_res.json()["id"]
        await client.post(f"{target_url}/sessions/{session_id}/start", headers=org_headers)
        print(f"[+] Created & Activated Fresh Benchmark Session ID: {session_id}")

        # Step 3: Provision test student cohort
        print(f"[+] Provisioning {num_students} bound test devices (batches of {concurrency})...")
        students = []
        for i in range(0, num_students, concurrency):
            batch_tasks = [
                register_student(client, target_url, idx)
                for idx in range(i, min(i + concurrency, num_students))
            ]
            batch_res = await asyncio.gather(*batch_tasks)
            students.extend(batch_res)

        print(f"[+] Successfully bound {len(students)} student devices.")

        # Step 4: Fetch fresh active rotating token right before the burst
        token_res = await client.get(f"{target_url}/sessions/{session_id}/token", headers=org_headers)
        active_token = token_res.json()["token"]
        print(f"[+] Fresh Cryptographic Rotating Token: {active_token}")

        # Step 5: Concurrently submit attendance packets (85% valid inside room, 15% outside room)
        print(f"\n[>>>] LAUNCHING CONCURRENT ATTENDANCE FLOOD ({num_students} requests)...")
        bench_start = time.perf_counter()

        tasks = []
        for s in students:
            rssi = -65 if (s["index"] % 7 != 0) else -86
            tasks.append(send_attendance_request(client, target_url, s, session_id, active_token, rssi))

        # Run with semaphored concurrency
        sem = asyncio.Semaphore(concurrency)
        async def sem_task(t):
            async with sem:
                return await t

        results = await asyncio.gather(*[sem_task(t) for t in tasks])
        total_time = time.perf_counter() - bench_start

        # Step 6: Compute Statistics
        latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]
        success_count = sum(1 for r in results if r["success"] is True)
        rejected_count = sum(1 for r in results if r["success"] is False and r["error"] is None)
        error_count = sum(1 for r in results if r["error"] is not None)

        latencies.sort()
        avg_lat = statistics.mean(latencies)
        p50 = statistics.median(latencies)
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        throughput = len(results) / total_time

        print(f"\n================ BENCHMARK RESULTS ================")
        print(f" Total Requests Sent:         {len(results)}")
        print(f" Verified Present (Passed):   {success_count} ({success_count/len(results)*100:.1f}%)")
        print(f" Correctly Rejected:          {rejected_count} ({rejected_count/len(results)*100:.1f}%)")
        print(f" Network / Server Errors:     {error_count}")
        print(f" Total Elapsed Time:          {total_time:.3f} s")
        print(f" Throughput:                  {throughput:.1f} req/sec")
        print(f" Latency Min:                 {min(latencies):.2f} ms")
        print(f" Latency Mean:                {avg_lat:.2f} ms")
        print(f" Latency p50 (Median):        {p50:.2f} ms")
        print(f" Latency p95:                 {p95:.2f} ms")
        print(f" Latency p99:                 {p99:.2f} ms")
        print(f" Latency Max:                 {max(latencies):.2f} ms")
        print(f"===================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ProxyProof Concurrency Load Tester")
    parser.add_argument("--students", type=int, default=100, help="Number of students to simulate (100, 500, 1000)")
    parser.add_argument("--concurrency", type=int, default=50, help="Simultaneous concurrent connections")
    parser.add_argument("--url", type=str, default=DEFAULT_BASE_URL, help="Base API URL")
    parser.add_argument("--in-process", action="store_true", help="Run benchmark in-process against ASGI engine without external network daemon")
    args = parser.parse_args()

    asyncio.run(run_load_test(args.students, args.concurrency, args.url, in_process=args.in_process))
