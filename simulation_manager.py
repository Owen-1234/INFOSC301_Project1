import streamlit as st

class SimulationManager:
    @staticmethod
    def render_sidebar():
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏗️ Simulation Lab")
        with st.sidebar.form("new_shop_form"):
            name = st.text_input("Brand Name", "Manner Clone")
            area = st.slider("Store Area (sqm)", 15, 300, 45)
            style = st.selectbox("Design Style", ["Modern", "Industrial", "Cyberpunk", "Vintage"])
            price = st.selectbox("Price Strategy", ["Value (Budget)", "Mid-Range", "Premium", "Ultra-Luxury"])
            submitted = st.form_submit_button("🚀 Deploy to Map")
            
            if submitted:
                last_click = st.session_state.get("retail_map", {}).get("last_clicked")
                if last_click:
                    new_shop = {
                        'Name': f"[SIM] {name}", 'lat': last_click['lat'], 'lon': last_click['lng'],
                        'Rating': "4.9", 'is_virtual': True,
                        'config': {'area': area, 'style': style, 'price_tier': price},
                        'Photo': "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?q=80&w=400&h=250&auto=format&fit=crop",
                        'Comment': f"A {style} boutique cafe positioned at {price} market."
                    }
                    st.session_state.virtual_shops.append(new_shop)
                    st.rerun()
                else:
                    st.sidebar.error("Click map first!")
