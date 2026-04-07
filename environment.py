from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict

app = FastAPI(title="Enterprise DBA Agent Env")

class Observation(BaseModel):
    ram_usage_percent: float
    collections: Dict[str, dict]
    active_indexes: List[str]
    slow_queries: List[str]
    snapshots_taken: List[str]

class Action(BaseModel):
    command: str  
    target_collection: str
    target_field: Optional[str] = None

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

class MockDatabase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ram_usage_percent = 92.0
        self.collections = {
            "api_temp_logs": {"size_mb": 5000, "important": False},
            "users": {"size_mb": 2000, "important": True}
        }
        self.active_indexes = ["users_old_useless_index"]
        self.slow_queries = [
            "Query on 'users' by 'email' taking 800ms (COLLSCAN)",
            "Dashboard query on 'users' filtering by 'status,city' taking 1500ms"
        ]
        self.snapshots_taken = []

    def get_state(self) -> Observation:
        return Observation(
            ram_usage_percent=self.ram_usage_percent,
            collections=self.collections,
            active_indexes=self.active_indexes,
            slow_queries=self.slow_queries,
            snapshots_taken=self.snapshots_taken
        )

    def execute_action(self, action: Action):
        reward = 0.0
        done = False
        message = ""

        if action.command == "create_snapshot":
            if action.target_collection in self.collections:
                if action.target_collection not in self.snapshots_taken:
                    self.snapshots_taken.append(action.target_collection)
                    reward = 0.1  
                    message = f"Snapshot created for {action.target_collection}."
                else:
                    message = f"Snapshot for {action.target_collection} already exists."
            else:
                reward = -0.1
                message = "Collection not found for snapshot."

        elif action.command == "drop_collection":
            if action.target_collection in self.collections:
                is_important = self.collections[action.target_collection]["important"]
                has_snapshot = action.target_collection in self.snapshots_taken

                if action.target_collection == "api_temp_logs":
                    if has_snapshot:
                        reward = 1.0  
                        done = True
                        message = "SUCCESS: Dropped temp logs safely with a backup."
                    else:
                        reward = -1.0 
                        done = True
                        message = "FAIL: Dropped collection without taking a snapshot."
                
                elif is_important:
                    reward = -1.0
                    done = True
                    message = "CRITICAL FAIL: Attempted to drop a production collection."
                
                del self.collections[action.target_collection]
            else:
                reward = -0.1
                message = "Collection not found."

        elif action.command == "drop_index":
            if action.target_field in self.active_indexes:
                self.active_indexes.remove(action.target_field)
                self.ram_usage_percent -= 5.0
                reward = 0.2
                message = f"Dropped index '{action.target_field}'. Recovered 5% RAM."
            else:
                reward = -0.1
                message = "Index not found."

        elif action.command == "create_index":
            if action.target_collection in self.collections and action.target_field:
                index_name = f"{action.target_collection}_{action.target_field}_index"
                if index_name not in self.active_indexes:
                    if action.target_collection == "users" and action.target_field == "email":
                        self.active_indexes.append(index_name)
                        self.ram_usage_percent += 3.0
                        self.slow_queries = [q for q in self.slow_queries if "email" not in q]
                        reward = 1.0
                        done = True
                        message = "SUCCESS: Created index on 'email'."
                    else:
                        self.active_indexes.append(index_name)
                        self.ram_usage_percent += 3.0
                        reward = -0.5
                        done = True
                        message = "FAIL: Wasted RAM on useless index."
            else:
                reward = -0.1
                message = "Invalid parameters for create_index."

        elif action.command == "create_compound_index":
            if action.target_collection == "users" and action.target_field == "status,city":
                if self.ram_usage_percent + 8.0 >= 100.0:
                    self.ram_usage_percent = 100.0
                    reward = -1.0
                    done = True
                    message = "CRITICAL FAIL: OOM Crash. Did not free up RAM before creating compound index."
                else:
                    self.active_indexes.append("users_status_city_compound")
                    self.ram_usage_percent += 8.0
                    self.slow_queries = [q for q in self.slow_queries if "status,city" not in q]
                    reward = 1.0
                    done = True
                    message = "SUCCESS: Freed RAM and safely created compound index."
            else:
                reward = -0.5
                message = "FAIL: Invalid compound index setup."
        
        else:
            reward = -0.1
            message = "Unknown command."

        return reward, done, message

db = MockDatabase()

@app.get("/state", response_model=Observation)
def get_state():
    return db.get_state()

@app.post("/reset", response_model=Observation)
def reset_env():
    db.reset()
    return db.get_state()

@app.post("/step", response_model=StepResponse)
def step(action: Action):
    reward_score, is_done, info_msg = db.execute_action(action)
    
    return StepResponse(
        observation=db.get_state(),
        reward=reward_score,
        done=is_done,
        info={"message": info_msg}
    )