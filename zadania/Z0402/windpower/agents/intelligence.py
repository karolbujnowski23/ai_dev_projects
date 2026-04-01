import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from windpower.utils.logger import logger
from windpower.blackboard import Blackboard

class IntelligenceAgent:
    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard

    async def calculate_schedule(self):
        """Builds schedule using deterministic python logic to avoid LLM timeouts/errors."""
        d = self.blackboard.data
        
        weather = d.get("weather", {}).get("forecast", [])
        deficit_str = d.get("power_deficit", {}).get("powerDeficitKw", "0")
        
        # Parse deficit range e.g. "3-4", "4-5"
        parts = deficit_str.split("-")
        if len(parts) == 2:
            min_req = float(parts[0])
            max_req = float(parts[1])
        else:
            min_req = float(deficit_str)
            max_req = float(deficit_str)
            
        target_mid = (min_req + max_req) / 2.0
        
        configs = {}
        storm_times = set()
        
        for point in weather:
            ts_str = point["timestamp"]
            wind = float(point["windMs"])
            
            # 1. Identify Storms
            if wind >= 14.0:
                configs[ts_str] = {
                    "pitchAngle": 90,
                    "turbineMode": "idle",
                    "windMs": wind
                }
                storm_times.add(ts_str)

        # 3. Find first production window
        def get_yield(w: float) -> float:
            if w < 4: return 0.0
            if w >= 12: return 1.0
            
            pts = [(4, 0.125), (6, 0.35), (8, 0.65), (10, 0.95), (12, 1.0)]
            for i in range(len(pts)-1):
                w1, y1 = pts[i]
                w2, y2 = pts[i+1]
                if w1 <= w <= w2:
                    return y1 + (w - w1) / (w2 - w1) * (y2 - y1)
            return 1.0
            
        production_added = False
        
        for point in weather:
            if production_added:
                break
                
            ts_str = point["timestamp"]
            wind = float(point["windMs"])
            
            if ts_str in storm_times or wind >= 14.0 or wind < 4.0:
                continue
                
            wy = get_yield(wind)
            
            # Check pitches
            for pitch in [0, 45]:
                py = 1.0 if pitch == 0 else 0.65
                estimated_power = 14.0 * wy * py
                
                # If estimated power is within or close to deficit
                if min_req <= estimated_power <= max_req or abs(estimated_power - target_mid) < 0.5:
                    configs[ts_str] = {
                        "pitchAngle": pitch,
                        "turbineMode": "production",
                        "windMs": wind
                    }
                    production_added = True
                    logger.info(f"IntelligenceAgent: Chosen production window at {ts_str} with pitch {pitch}, wind {wind}, est. power {estimated_power:.2f}kW (Target: {deficit_str}kW)")
                    break
        
        if configs:
            self.blackboard.data["draft_schedule"] = configs
            logger.info(f"IntelligenceAgent: Successfully drafted schedule with {len(configs)} steps.")
            self.blackboard.set_event("schedule_drafted")
        else:
            logger.error("IntelligenceAgent: Failed to draft schedule (no configs generated).")
