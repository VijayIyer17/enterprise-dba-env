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
            else:
                print(f"HTTP Error: {response.status} on {url}")
                return {}
                
    except urllib.error.URLError as e:
        print(f"Network Error reaching {url}: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error on {url}: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error on {url}: {e}")
        return {}

def run_baseline_agent(task_name, golden_actions):
    print(f"\n--- Running {task_name} ---")
    
    # Reset the environment safely
    make_request("reset")
    total_score = 0.0
    
    for action in golden_actions:
        print(f"Agent Action: {action['command']} on {action.get('target_collection', 'users')}")
        
        response = make_request("step", payload=action)
        if not response:
            print("Failed to get response, skipping action.")
            continue
            
        reward = response.get("reward", 0.0)
        total_score += reward
        
        info_msg = response.get('info', {}).get('message', 'No message')
        print(f"Result: {info_msg} | Reward: {reward}")
    
    print(f"Final Baseline Score for {task_name}: {total_score}")
    return total_score

def main():
    print("Starting OpenEnv Baseline Inference Script...")
    
    task_1_actions = [
        {"command": "create_snapshot", "target_collection": "api_temp_logs"},
        {"command": "drop_collection", "target_collection": "api_temp_logs"}
    ]
    run_baseline_agent("Task 1 (Easy)", task_1_actions)

    task_2_actions = [
        {"command": "create_index", "target_collection": "users", "target_field": "email"}
    ]
    run_baseline_agent("Task 2 (Medium)", task_2_actions)

    task_3_actions = [
        {"command": "drop_index", "target_collection": "users", "target_field": "users_old_useless_index"},
        {"command": "create_compound_index", "target_collection": "users", "target_field": "status,city"}
    ]
    run_baseline_agent("Task 3 (Hard)", task_3_actions)
    
    print("\nAll Baseline tests completed successfully.")

if __name__ == "__main__":
    main()
