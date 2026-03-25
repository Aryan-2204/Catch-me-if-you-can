import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def init_storage():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    scores_file = os.path.join(DATA_DIR, "scores.json")
    if not os.path.exists(scores_file):
        with open(scores_file, "w") as f:
            json.dump({"high_scores": [], "survival_streak": 0}, f, indent=4)
            
    settings_file = os.path.join(DATA_DIR, "settings.json")
    if not os.path.exists(settings_file):
        with open(settings_file, "w") as f:
            json.dump({
                "sound_on": True, 
                "scanlines_on": True, 
                "game_speed": 1.0
            }, f, indent=4)

def get_scores():
    try:
        with open(os.path.join(DATA_DIR, "scores.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {"high_scores": [], "survival_streak": 0}

def save_score(turns, time_survived, difficulty, is_caught):
    scores = get_scores()
    
    # Update streak
    if not is_caught:
        scores["survival_streak"] += 1
    else:
        scores["survival_streak"] = 0
        
    scores["high_scores"].append({
        "turns": turns,
        "time": time_survived,
        "difficulty": difficulty
    })
    
    # Sort by turns (higher is better) then time (higher is better)
    scores["high_scores"].sort(key=lambda x: (x["turns"], x["time"]), reverse=True)
    # Keep top 5
    scores["high_scores"] = scores["high_scores"][:5]
    
    with open(os.path.join(DATA_DIR, "scores.json"), "w") as f:
        json.dump(scores, f, indent=4)

def get_settings():
    try:
        with open(os.path.join(DATA_DIR, "settings.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {"sound_on": True, "scanlines_on": True, "game_speed": 1.0}

def save_settings(settings_dict):
    with open(os.path.join(DATA_DIR, "settings.json"), "w") as f:
        json.dump(settings_dict, f, indent=4)
