import os
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=(""))

# Crisis keywords
CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "self harm", 
                   "hurt myself", "don't want to live", "hopeless", "die"]

def search_web(query):
    """Search web for mental health resources"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                response = "🔍 **Relevant Resources Found:**\n\n"
                for r in results:
                    response += f"• **{r['title']}**\n  {r['href']}\n\n"
                return response
    except:
        return ""
    return ""

def detect_crisis(text):
    """Detect if user is in crisis"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)

def get_ai_response(conversation_history):
    """Get response from Groq AI"""
    system_prompt = """You are a compassionate AI Mental Health Support Agent. Your role is to:
1. Listen empathetically to users expressing emotional distress
2. Provide supportive, evidence-based responses
3. Suggest healthy coping strategies
4. Encourage professional help when needed
5. Be warm, non-judgmental, and caring

Important: You are NOT a replacement for professional mental health care. 
Always remind users to seek professional help for serious issues.
Keep responses concise, warm and supportive."""

    messages = [{"role": "system", "content": system_prompt}] + conversation_history
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

def create_wellness_plan(concern):
    """Generate personalized wellness plan"""
    prompt = f"""Create a simple 7-day wellness plan for someone dealing with: {concern}
    Format it as:
    - Day 1-2: [activity]
    - Day 3-4: [activity]  
    - Day 5-6: [activity]
    - Day 7: [reflection]
    Keep it practical and achievable."""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="AI Mental Health Agent", page_icon="🧠", layout="centered")

st.title("🧠 AI Mental Health Support Agent")
st.caption("A safe space to talk. I'm here to listen and help. 💙")

# Sidebar features
with st.sidebar:
    st.header("🛠️ Agent Tools")
    
    if st.button("📋 Generate Wellness Plan"):
        if "last_concern" in st.session_state:
            with st.spinner("Creating your personalized plan..."):
                plan = create_wellness_plan(st.session_state.last_concern)
                st.session_state.wellness_plan = plan
        else:
            st.warning("Chat first so I understand your concern!")
    
    if "wellness_plan" in st.session_state:
        st.markdown("### Your 7-Day Plan:")
        st.markdown(st.session_state.wellness_plan)
    
    st.divider()
    st.markdown("### 🚨 Crisis Helplines")
    st.markdown("""
    - **Pakistan:** Umang: 0311-7786264
    - **International:** Crisis Text Line: Text HOME to 741741
    - **Suicide Hotline:** 988 (US)
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! 💙 I'm your AI Mental Health Support Agent. I'm here to listen, support, and help you find resources. How are you feeling today?"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Share what's on your mind..."):
    
    # Store last concern for wellness plan
    st.session_state.last_concern = prompt
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        
        # Crisis detection
        if detect_crisis(prompt):
            crisis_msg = """🚨 **I'm concerned about your safety.**
            
Please reach out immediately:
- **Pakistan Umang helpline: 0311-7786264**
- **Crisis Text Line: Text HOME to 741741**
- **Or go to your nearest emergency room**

You are not alone. Help is available right now. 💙"""
            st.markdown(crisis_msg)
            st.session_state.messages.append({"role": "assistant", "content": crisis_msg})
        
        else:
            # Get AI response
            with st.spinner("Thinking..."):
                conversation = [m for m in st.session_state.messages if m["role"] != "system"]
                ai_response = get_ai_response(conversation)
            
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # Auto search for resources if needed
            if any(word in prompt.lower() for word in ["help", "resource", "therapy", "therapist", "doctor"]):
                with st.spinner("🔍 Searching for resources..."):
                    search_results = search_web(f"mental health resources {prompt}")
                    if search_results:
                        st.markdown(search_results)