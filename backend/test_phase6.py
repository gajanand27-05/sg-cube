import sys

sys.path.insert(0, ".")
from fastapi.testclient import TestClient
import server

client = TestClient(server.app)

print("=" * 60)
print("PHASE 6 INTEGRATION TESTS")
print("=" * 60)

print("\nTEST 1: /api/ollama/status")
resp = client.get("/api/ollama/status")
data = resp.json()
print(f"  Status: {resp.status_code}")
print(f"  Online: {data.get('online')}")
print(f"  Models: {data.get('models')}")
print(f"  Current model: {data.get('current_model')}")
assert resp.status_code == 200
assert "current_model" in data
assert "models" in data
print("  PASS")

print("\nTEST 2: /api/ollama/models")
resp = client.get("/api/ollama/models")
data = resp.json()
print(f"  Status: {resp.status_code}")
print(f"  Success: {data.get('success')}")
print(f"  Models: {data.get('models')}")
assert resp.status_code == 200
print("  PASS")

print("\nTEST 3: /api/ollama/model (switch model)")
resp = client.post("/api/ollama/model", json={"model": "gemma4:e4b"})
data = resp.json()
print(f"  Status: {resp.status_code}")
print(f"  Success: {data.get('success')}")
print(f"  Current model: {data.get('current_model')}")
assert resp.status_code == 200
assert data.get("success") == True
assert data.get("current_model") == "gemma4:e4b"
print("  PASS")

print("\nTEST 4: /api/ollama/status (after model switch)")
resp = client.get("/api/ollama/status")
data = resp.json()
print(f"  Current model: {data.get('current_model')}")
assert data.get("current_model") == "gemma4:e4b"
print("  PASS")

resp = client.post("/api/ollama/model", json={"model": "llama3"})
print("\nTEST 5: Reset model back to llama3")
data = resp.json()
print(f"  Current model: {data.get('current_model')}")
assert data.get("current_model") == "llama3"
print("  PASS")

print("\nTEST 6: /api/health (existing endpoint)")
resp = client.get("/api/health")
assert resp.status_code == 200
print(f"  Status: {resp.status_code}")
print("  PASS")

print("\nTEST 7: /api/command - hello (existing endpoint)")
resp = client.post("/api/command", json={"text": "hello"})
data = resp.json()
assert resp.status_code == 200
assert data.get("action") == "greeting"
print(f"  Action: {data.get('action')}")
print("  PASS")

print("\nTEST 8: /api/command - unknown (Gemini fallback)")
resp = client.post("/api/command", json={"text": "What is quantum physics?"})
data = resp.json()
assert resp.status_code == 200
print(f"  Action: {data.get('action')}")
print(f"  Response preview: {data.get('response')[:80]}...")
print("  PASS")

print("\nTEST 9: /api/tools/codegen (existing endpoint)")
resp = client.post("/api/tools/codegen", json={"input_data": "hello world in python"})
data = resp.json()
assert resp.status_code == 200
print(f"  Response preview: {data.get('result')[:80]}...")
print("  PASS")

print("\nTEST 10: /api/system (existing endpoint)")
resp = client.get("/api/system")
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  CPU: {data.get('cpu')}%, RAM: {data.get('ram_used')}GB")
print("  PASS")

print("\nTEST 11: /api/login (existing endpoint)")
resp = client.post("/api/login", json={"username": "admin", "password": "admin"})
data = resp.json()
assert resp.status_code == 200
assert data.get("success") == True
print(f"  Response: {data}")
print("  PASS")

print("\n" + "=" * 60)
print("ALL 11 TESTS PASSED")
print("=" * 60)
