import requests
import json
import numpy as np
from math import radians, cos, sin, asin, sqrt, log10

class UrbanWorldModel:
    def __init__(self, api_key: str):
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.api_key = api_key
        self.model_name = "deepseek-chat"
        self.center_lat, self.center_lon = 31.385, 120.980 # Kunshan Commercial Center

    def _calculate_geo_baseline(self, coords, time_period, nearby_pois):
        """Standard spatial gravity logic for baseline traffic."""
        try:
            lat, lon = map(float, coords.split(','))
        except:
            lat, lon = self.center_lat, self.center_lon
        
        dist = self._haversine_dist(lon, lat, self.center_lon, self.center_lat)
        if dist < 800:
            base, decay = 450, 1.0 - (dist / 4000)
        elif dist < 2500:
            base, decay = 250, 0.9 - (dist / 8000)
        else:
            base, decay = 100, 0.8

        w_time = {"Morning Peak": 1.9, "Lunch Break": 1.5, "After Work": 2.4}.get(time_period, 1.0)
        w_density = 1.0 + log10(1 + len(nearby_pois))
        return int(base * decay * w_time * w_density)

    def _haversine_dist(self, lon1, lat1, lon2, lat2):
        # Haversine formula for distance calculation
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * asin(sqrt(a)) * 6371 * 1000

    def predict_urban_dynamics(self, coords, time_period, nearby_pois, is_shop=False, config=None):
        geo_baseline = self._calculate_geo_baseline(coords, time_period, nearby_pois)
        
        # Extract features for AI Reasoning
        area = config.get('area', 35) if config else 35
        style = config.get('style', 'Modern') if config else 'Classic'
        price = config.get('price_tier', 'Mid-Range') if config else 'Mid-Range'
        
        # Enhanced Strategic Prompt
        prompt = f"""
        Role: Senior Urban Economist.
        Task: Analyze a coffee shop in Kunshan. 
        Site Type: {'Existing Shop' if is_shop else 'Simulated New Site'}
        Parameters: Area {area}sqm, Style {style}, Price Tier {price}.
        Baseline Data: {geo_baseline} pax/hr (Spatial Gravity).
        Competitors: {len(nearby_pois)} within immediate vicinity.

        Requirement: 
        1. Calculate 'est_monthly_revenue' using: (Traffic * Conversion * Avg_Check * 30 days * 10 hours).
        2. Adjust conversion rate based on 'Style' and 'Competition'.
        3. Do not return 0 unless the site is completely non-viable.

        Output JSON:
        {{
            "predicted_traffic": int,
            "est_monthly_revenue": int (CNY),
            "payback_months": float,
            "radar_scores": {{ "traffic": 0-100, "competition": 0-100, "brand": 0-100 }},
            "swot": {{ "strength": "str", "risk": "str" }},
            "reasoning": "A professional deduction focusing on style-location fit and pricing strategy."
        }}
        """
        
        try:
            r = requests.post(self.api_url, headers={"Authorization": f"Bearer {self.api_key}"},
                              json={"model": self.model_name, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}, timeout=12)
            res_data = json.loads(r.json()['choices'][0]['message']['content'])
            # Validation: Ensure revenue is not 0
            if res_data.get('est_monthly_revenue', 0) == 0:
                raise ValueError("AI returned zero revenue")
            return res_data
        except Exception as e:
            # Smart Fallback: Avoid returning 0
            avg_checks = {"Value (Budget)": 15, "Mid-Range": 30, "Premium": 55, "Ultra-Luxury": 120}
            check = avg_checks.get(price, 30)
            # Heuristic: Revenue = Traffic * 10hrs * 30days * 8% conversion * Price
            fallback_rev = int(geo_baseline * 10 * 30 * 0.08 * check)
            return {
                "predicted_traffic": geo_baseline,
                "est_monthly_revenue": fallback_rev,
                "payback_months": round((area * 8000) / (fallback_rev * 0.2 + 1), 1),
                "radar_scores": {"traffic": 70, "competition": 40, "brand": 60},
                "swot": {"strength": "Stable spatial demand", "risk": "Limited brand differentiation"},
                "reasoning": f"DeepSeek API Offline. Heuristic simulation active: Revenue estimated based on {geo_baseline} pax/hr and {price} pricing strategy."
            }
