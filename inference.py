import os
import json
import urllib.request
import urllib.error

ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:7860")

def make_request(endpoint, payload=None):
    url = f"{ENV_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    try:
        if payload:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        else:
            req = urllib.request.Request(url, method='POST')
            
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                response_data = response.read().decode('utf-8')
                if not response_data:
                    return {}
                return json.loads(response_data)
            return {}
    except Exception:
        return {}

def run_baseline_agent(task_name, golden_actions):
    print(f"[START] task={task_name}", flush=True)
    
    make_request("reset")
    total_score = 0.0
    step_num = 0
    
    for action in golden_actions:
        step_num += 1
        response = make_request("step", payload=action)
        
        reward = 0.0
        if response:
            reward = response.get("reward", 0.0)
            
        total_score += reward
        
        print(f"[STEP] step={step_num} reward={reward}", flush=True)
    
    print(f"[END] task={task_name} score={total_score} steps={step_num}", flush=True)
    return total_score

def main():
    task_1_actions = [
        {"command": "create_snapshot", "target_collection": "api_temp_logs"},
        {"command": "drop_collection", "target_collection": "api_temp_logs"}
    ]
    run_baseline_agent("Task 1", task_1_actions)

    task_2_actions = [
        {"command": "create_index", "target_collection": "users", "target_field": "email"}
    ]
    run_baseline_agent("Task 2", task_2_actions)

    task_3_actions = [
        {"command": "drop_index", "target_collection": "users", "target_field": "users_old_useless_index"},
        {"command": "create_compound_index", "target_collection": "users", "target_field": "status,city"}
    ]
    run_baseline_agent("Task 3", task_3_actions)

if __name__ == "__main__":
    main()
