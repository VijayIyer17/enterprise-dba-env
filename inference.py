import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key-for-validation")

client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

ENV_URL = "http://127.0.0.1:8000"

def run_baseline_agent(task_name, golden_actions):
    print(f"\n--- Running {task_name} ---")
    
    requests.post(f"{ENV_URL}/reset")
    total_score = 0.0
    
    for action in golden_actions:
        print(f"Agent Action: {action['command']} on {action.get('target_collection', 'users')}")
        response = requests.post(f"{ENV_URL}/step", json=action).json()
        
        reward = response.get("reward", 0.0)
        total_score += reward
        print(f"Result: {response['info']['message']} | Reward: {reward}")
    
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