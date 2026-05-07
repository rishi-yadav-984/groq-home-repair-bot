import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
import random

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Groq Home Repair Bot",
    page_icon="🔧",
    layout="wide"
)

class HomeRepairBot:
    def __init__(self):
        # Get API key from Streamlit secrets or .env
        self.api_key = self.get_api_key()
        
        # Sample suggestions for first-time users
        self.suggestions = [
            "How do I fix a leaky faucet in my kitchen?",
            "How can I unclog a bathroom sink drain?",
            "What's the best way to paint over dark walls?",
            "How do I fix a door that won't close properly?",
            "What's involved in replacing a light switch?",
            "How do I repair a crack in concrete driveway?"
        ]
        
        # Cost database in Indian Rupees (₹)
        self.cost_database = {
            "faucet": {
                "materials_min": 200, "materials_max": 1500,
                "tools_min": 300, "tools_max": 800,
                "professional_min": 500, "professional_max": 2000,
                "items": "Washers, O-rings, faucet cartridge, plumber's tape, wrench"
            },
            "drywall": {
                "materials_min": 300, "materials_max": 2000,
                "tools_min": 200, "tools_max": 600,
                "professional_min": 1000, "professional_max": 5000,
                "items": "Joint compound, drywall patch, sandpaper, primer, paint, putty knife"
            },
            "toilet": {
                "materials_min": 150, "materials_max": 2000,
                "tools_min": 200, "tools_max": 500,
                "professional_min": 500, "professional_max": 3000,
                "items": "Flapper, fill valve, wax ring, bolts, plunger"
            },
            "paint": {
                "materials_min": 500, "materials_max": 5000,
                "tools_min": 200, "tools_max": 1500,
                "professional_min": 3000, "professional_max": 20000,
                "items": "Paint, primer, brushes, rollers, painter's tape, drop cloth"
            },
            "drain": {
                "materials_min": 100, "materials_max": 800,
                "tools_min": 200, "tools_max": 600,
                "professional_min": 500, "professional_max": 3000,
                "items": "Drain cleaner, baking soda, vinegar, drain snake, plunger"
            },
            "electric": {
                "materials_min": 100, "materials_max": 1500,
                "tools_min": 300, "tools_max": 1000,
                "professional_min": 500, "professional_max": 5000,
                "items": "Switch/outlet, wire connectors, electrical tape, screwdriver, voltage tester"
            },
            "floor": {
                "materials_min": 500, "materials_max": 10000,
                "tools_min": 500, "tools_max": 3000,
                "professional_min": 2000, "professional_max": 30000,
                "items": "Tiles, adhesive, grout, spacers, sealant, tile cutter"
            },
            "door": {
                "materials_min": 100, "materials_max": 1500,
                "tools_min": 200, "tools_max": 800,
                "professional_min": 500, "professional_max": 4000,
                "items": "Hinges, screws, wood filler, sandpaper, paint, screwdriver"
            },
            "tile": {
                "materials_min": 200, "materials_max": 3000,
                "tools_min": 300, "tools_max": 1500,
                "professional_min": 1000, "professional_max": 8000,
                "items": "Replacement tiles, adhesive, grout, sealant, spacers, notched trowel"
            },
            "concrete": {
                "materials_min": 300, "materials_max": 3000,
                "tools_min": 300, "tools_max": 1500,
                "professional_min": 1000, "professional_max": 10000,
                "items": "Concrete patch compound, sealant, bonding agent, trowel, wire brush"
            },
            "water_pressure": {
                "materials_min": 200, "materials_max": 2000,
                "tools_min": 200, "tools_max": 800,
                "professional_min": 500, "professional_max": 5000,
                "items": "Showerhead, pressure booster pump, plumber's tape, cleaning solution"
            },
            "default": {
                "materials_min": 200, "materials_max": 2000,
                "tools_min": 200, "tools_max": 1000,
                "professional_min": 500, "professional_max": 5000,
                "items": "Basic repair materials, common tools"
            }
        }
        
        # City multipliers
        self.city_multipliers = {
            "Mumbai": 1.4, "Delhi": 1.3, "Bangalore": 1.3,
            "Chennai": 1.2, "Hyderabad": 1.2, "Pune": 1.2,
            "Kolkata": 1.1, "Ahmedabad": 1.1,
            "Tier 2 City": 0.9, "Tier 3 City": 0.8, "Village/Rural": 0.6
        }
        
        self.initialize_session_state()
    
    def get_api_key(self):
        """Get API key from Streamlit secrets or .env"""
        try:
            return st.secrets["GROQ_API_KEY"]
        except:
            return os.getenv("GROQ_API_KEY")
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": """You are an expert home repair assistant in India. Provide:
                    - Step-by-step instructions
                    - Required tools and materials
                    - Estimated time
                    - Safety precautions
                    - When to call a professional
                    - Money-saving tips"""
                }
            ]
        
        if "selected_city" not in st.session_state:
            st.session_state.selected_city = "Tier 2 City"
    
    def format_inr(self, amount):
        """Format amount in Indian Rupees"""
        if amount >= 100000:
            return f"₹{amount/100000:.1f} Lakh"
        elif amount >= 1000:
            return f"₹{amount:,}"
        else:
            return f"₹{amount}"
    
    def run(self):
        """Main application"""
        st.title("🔧 Groq Home Repair Bot")
        st.caption("⚡ Powered by Llama 3 | AI Home Repair Assistant 🇮🇳")
        
        # Check API key
        if not self.api_key:
            st.error("❌ API Key not found!")
            st.info("""
            **Setup Required:**
            - **Streamlit Cloud:** Add `GROQ_API_KEY = "your-key"` in app secrets
            - **Local Development:** Create `.env` file with `GROQ_API_KEY=your-key`
            - Get free API key: https://console.groq.com/keys
            """)
            return
        
        try:
            client = Groq(api_key=self.api_key)
            
            # Sidebar with city selector only
            with st.sidebar:
                st.header("📍 Location")
                st.session_state.selected_city = st.selectbox(
                    "Select your city for accurate pricing",
                    ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", 
                     "Pune", "Kolkata", "Ahmedabad", "Tier 2 City", "Tier 3 City", "Village/Rural"]
                )
                st.markdown("---")
                st.caption("Cost estimates adjust based on your city")
            
            # Chat interface
            self.chat_interface(client)
            
        except Exception as e:
            st.error(f"Error connecting to Groq API: {str(e)}")
    
    def chat_interface(self, client):
        """Main chat interface"""
        
        # Show suggestions for new users
        user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
        
        if len(user_messages) == 0:
            st.markdown("### 💡 Common Questions")
            st.markdown("*Click any question to start instantly:*")
            
            cols = st.columns(2)
            random_suggestions = random.sample(self.suggestions, min(4, len(self.suggestions)))
            
            for i, suggestion in enumerate(random_suggestions):
                with cols[i % 2]:
                    if st.button(suggestion, use_container_width=True, key=f"sug_{i}"):
                        st.session_state.messages.append({"role": "user", "content": suggestion})
                        self.get_bot_response(client, suggestion)
                        st.rerun()
            
            st.markdown("---")
        
        # Display chat messages
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    # Display assistant messages with cost estimate
                    if msg["role"] == "assistant":
                        # Split response and cost estimate
                        parts = msg["content"].split("|||COST_ESTIMATE|||")
                        if len(parts) == 2:
                            st.markdown(parts[0])
                            self.display_cost_estimate(parts[1])
                        else:
                            st.markdown(msg["content"])
                    else:
                        st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask any home repair question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            self.get_bot_response(client, prompt)
            st.rerun()
    
    def get_bot_response(self, client, prompt):
        """Get AI response and generate cost estimate"""
        with st.chat_message("assistant"):
            with st.spinner("Getting expert advice..."):
                try:
                    # Get AI response
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    response = completion.choices[0].message.content
                    
                    # Display AI response
                    st.markdown(response)
                    
                    # Display cost estimate
                    cost_data = self.display_cost_estimate_direct(prompt)
                    
                    # Store with separator for display later
                    stored_content = response + "|||COST_ESTIMATE|||" + prompt
                    st.session_state.messages.append({"role": "assistant", "content": stored_content})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    def display_cost_estimate_direct(self, query):
        """Display cost estimate directly using Streamlit components"""
        repair_type = self.detect_repair_type(query.lower())
        cost_data = self.cost_database.get(repair_type, self.cost_database["default"])
        
        # Apply city multiplier
        multiplier = self.city_multipliers.get(st.session_state.selected_city, 1.0)
        
        # Calculate costs
        materials_low = int(cost_data["materials_min"] * multiplier)
        materials_high = int(cost_data["materials_max"] * multiplier)
        tools_low = int(cost_data["tools_min"] * multiplier)
        tools_high = int(cost_data["tools_max"] * multiplier)
        pro_low = int(cost_data["professional_min"] * multiplier)
        pro_high = int(cost_data["professional_max"] * multiplier)
        
        # Averages
        materials_avg = (materials_low + materials_high) // 2
        tools_avg = (tools_low + tools_high) // 2
        pro_avg = (pro_low + pro_high) // 2
        diy_total = materials_avg + tools_avg
        savings = pro_avg - diy_total
        savings_percent = int((savings / pro_avg) * 100) if pro_avg > 0 else 0
        
        # Display using Streamlit native components
        st.markdown("---")
        st.markdown(f"### 💰 Estimated Cost Breakdown ({st.session_state.selected_city})")
        
        # Materials and Tools in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "🛠️ Materials",
                f"{self.format_inr(materials_low)} - {self.format_inr(materials_high)}",
                help=cost_data["items"]
            )
        with col2:
            st.metric(
                "🔧 Tools",
                f"{self.format_inr(tools_low)} - {self.format_inr(tools_high)}"
            )
        
        # Items needed
        st.caption(f"**Items needed:** {cost_data['items']}")
        
        # Cost comparison
        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.metric(
                "🏠 DIY Total",
                self.format_inr(diy_total)
            )
        with col4:
            st.metric(
                "👷 Professional",
                f"{self.format_inr(pro_low)} - {self.format_inr(pro_high)}"
            )
        
        # Savings
        st.success(f"💰 **Your Potential Savings:** {self.format_inr(savings)} ({savings_percent}% cheaper by DIY)")
        
        # Tips
        st.markdown("**💡 Tips:**")
        st.markdown(f"""
        - 🏪 Visit local hardware shops for better prices
        - 👷 Daily wage for labor: {self.format_inr(int(500*multiplier))} - {self.format_inr(int(1000*multiplier))}
        - 🛒 Check online: Amazon India, Flipkart for tools
        - ⚡ Always get multiple quotes from professionals
        """)
        
        st.caption(f"⚠️ Costs are estimates for {st.session_state.selected_city}. Actual prices vary by brand, quality, and location.")
    
    def display_cost_estimate(self, query):
        """Display cost estimate from stored data"""
        self.display_cost_estimate_direct(query)
    
    def detect_repair_type(self, query):
        """Detect repair type from query keywords"""
        if any(word in query for word in ["faucet", "tap", "leak", "drip"]):
            return "faucet"
        elif any(word in query for word in ["drywall", "hole", "wall", "patch", "plaster"]):
            return "drywall"
        elif any(word in query for word in ["toilet", "flush", "commode"]):
            return "toilet"
        elif any(word in query for word in ["paint", "color", "brush", "roller", "wallpaper"]):
            return "paint"
        elif any(word in query for word in ["drain", "clog", "pipe", "sink"]):
            return "drain"
        elif any(word in query for word in ["electric", "outlet", "switch", "wire", "light", "fan"]):
            return "electric"
        elif any(word in query for word in ["floor", "tile", "hardwood", "carpet"]):
            return "floor"
        elif any(word in query for word in ["door", "hinge", "knob", "lock"]):
            return "door"
        elif any(word in query for word in ["tile", "grout"]):
            return "tile"
        elif any(word in query for word in ["concrete", "crack", "cement", "driveway"]):
            return "concrete"
        elif any(word in query for word in ["pressure", "shower"]):
            return "water_pressure"
        else:
            return "default"

# Run app
if __name__ == "__main__":
    bot = HomeRepairBot()
    bot.run()