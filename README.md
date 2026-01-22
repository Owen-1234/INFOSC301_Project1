This `README.md` is designed to provide a professional overview of your project, incorporating technical details from your files and a dedicated section on operational and security precautions to ensure safe deployment to GitHub.

---

# UrbanRetail World Model: Kunshan Coffee Site Selection 

The **UrbanRetail World Model** is an AI-driven decision-support system that integrates spatial gravity models with Large Language Model (LLM) reasoning to evaluate commercial site viability in Kunshan, China. By combining real-time geospatial data with strategic business logic, the system helps entrepreneurs navigate complex urban dynamics.

## Key Features

* **Interactive Map Analysis**: Utilizes a Folium-based interface to visualize established market players in Kunshan using real-time POI data from the **Amap API**.
* **Simulation Lab**: Allows users to "virtually deploy" new shop concepts by selecting locations and configuring parameters such as store area, design style (e.g., Cyberpunk, Industrial), and price strategy.
* **Spatial Gravity Baseline**: Automatically calculates traffic flow baselines using a Haversine-based distance decay logic and commercial density metrics.
* **DeepSeek Strategic Reasoning**: Generates narrative SWOT analyses and financial predictions (Monthly Revenue, Payback Period) through a professional AI deduction pipeline.
* **Dynamic Visualizations**: Presents multi-criteria suitability scores through interactive radar charts and heatmaps.

## Operation & Security Precautions

To ensure the system remains secure and ethically grounded, users must adhere to the following precautions:

* **API Key Exposure (Critical)**:
* The current version of `main_app.py` contains hardcoded credentials for the **DeepSeek API** and **Amap API**.
* **Action Required**: Before pushing to a public GitHub repository, remove these keys and replace them with environment variables or a `secrets.toml` file to prevent unauthorized usage and financial loss.


* **Data Governance**:
* Users are expected to apply the CARE (Collective Benefit, Authority to Control, Responsibility, and Ethics) framework when interpreting results.


* The system includes an "Area Saturation" logic; avoid using predictions to aggressively displace small local vendors.


* **Technical Operational Flow**:
* The Simulation Lab requires a map click event to capture coordinates before deployment.
* The AI inference has a 12-second timeout; if the API is offline, a heuristic fallback will provide estimated values based on spatial gravity baselines to ensure process continuity.


* **Truthfulness & Cognitive Load**:
* LLM-generated "AI Reasoning" should be cross-validated against the physical constraints shown on the map.
* The system explicitly separates deterministic traffic data from speculative strategic narratives to protect the principle of truthfulness.



##  Technical Stack

* **Frontend**: [Streamlit](https://streamlit.io/) (Heavy-compute backend, lightweight browser interface).
* **Mapping**: [Folium](https://python-visualization.github.io/folium/) & [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium).
* **AI Engine**: [DeepSeek-V3](https://www.deepseek.com/) (Strategic inference).
* **Data API**: [Amap Web Service](https://lbs.amap.com/) (Real-time POI and Geocoding).

##  Installation & Setup

1. **Clone the Repository**:
```bash
git clone https://github.com/your-username/UrbanRetail-World-Model.git
cd UrbanRetail-World-Model

```


2. **Install Dependencies**:
```bash
pip install streamlit pandas folium plotly requests streamlit-folium

```


3. **Configure API Keys**:
Set your `DEEPSEEK_API_KEY` and `AMAP_KEY` in `main_app.py`.
4. **Run Application**:
```bash
streamlit run main_app.py

```

**Developed by Shilin Ou** *Project submitted as part of the INFOSCI 301 InfoVis Redesign Project at Duke Kunshan University*.
