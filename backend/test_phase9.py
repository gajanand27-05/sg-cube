import sys

sys.path.insert(0, ".")
from fastapi.testclient import TestClient
import server

client = TestClient(server.app)

print("=" * 60)
print("PHASE 9 INTEGRATION TESTS")
print("=" * 60)

print("\nTEST 1: /api/system/action - file_manager")
resp = client.post("/api/system/action", json={"action": "file_manager"})
data = resp.json()
print(f"  Status: {resp.status_code}")
print(f"  Response: {data}")
assert resp.status_code == 200
assert data.get("success") == True
print("  PASS")

print("\nTEST 2: /api/system/action - terminal")
resp = client.post("/api/system/action", json={"action": "terminal"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Response: {data}")
print("  PASS")

print("\nTEST 3: /api/system/action - task_manager")
resp = client.post("/api/system/action", json={"action": "task_manager"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Response: {data}")
print("  PASS")

print("\nTEST 4: /api/system/action - control_panel")
resp = client.post("/api/system/action", json={"action": "control_panel"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Response: {data}")
print("  PASS")

print("\nTEST 5: /api/system/action - network")
resp = client.post("/api/system/action", json={"action": "network"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Response: {data}")
print("  PASS")

print("\nTEST 6: /api/system/action - run_script (coming soon)")
resp = client.post("/api/system/action", json={"action": "run_script"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
assert "coming soon" in data.get("response", "").lower()
print(f"  Response: {data}")
print("  PASS")

print("\nTEST 7: /api/system/action - unknown")
resp = client.post("/api/system/action", json={"action": "unknown_action"})
assert resp.status_code == 400
print(f"  Status: {resp.status_code}")
print("  PASS")

print("\nTEST 8: /api/command - coding setup (triggers real subprocess)")
resp = client.post("/api/command", json={"text": "coding setup"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "coding_setup"
print(f"  Action: {data.get('action')}")
print(f"  Response: {data.get('response')[:80]}...")
print("  PASS")

print("\nTEST 9: /api/command - confirm shutdown")
resp = client.post("/api/command", json={"text": "confirm shutdown"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "shutdown"
print(f"  Response: {data.get('response')}")
print("  PASS")

print("\nTEST 10: /api/command - confirm restart")
resp = client.post("/api/command", json={"text": "confirm restart"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "restart"
print(f"  Response: {data.get('response')}")
print("  PASS")

print("\nTEST 11: /api/command - cancel shutdown")
resp = client.post("/api/command", json={"text": "cancel shutdown"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "cancel_shutdown"
print(f"  Response: {data.get('response')}")
print("  PASS")

print("\nTEST 12: /api/command - hello (existing)")
resp = client.post("/api/command", json={"text": "hello"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "greeting"
print("  PASS")

print("\nTEST 13: /api/health (existing)")
resp = client.get("/api/health")
assert resp.status_code == 200
print("  PASS")

print("\nTEST 14: /api/ollama/status (existing)")
resp = client.get("/api/ollama/status")
data = resp.json()
assert resp.status_code == 200
assert "current_model" in data
print(f"  Model: {data.get('current_model')}")
print("  PASS")

print("\nTEST 15: /api/chat/history (existing)")
resp = client.get("/api/chat/history?user_id=default&limit=5")
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Messages: {len(data.get('messages', []))}")
print("  PASS")

print("\n" + "=" * 60)
print("ALL 15 TESTS PASSED")
print("=" * 60)
