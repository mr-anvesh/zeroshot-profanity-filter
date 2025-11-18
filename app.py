"""
Streamlit Frontend for Profanity Filter
A web interface for the mDeBERTa-v3-base-mnli-xnli based profanity filter
"""

import streamlit as st
from profanity_filter import ProfanityFilter
import time

# Page configuration
st.set_page_config(
    page_title="AI Profanity Filter",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
    st.session_state.filter = None
    st.session_state.history = []

@st.cache_resource
def load_model(threshold):
    """Load the profanity filter model (cached)"""
    with st.spinner("🔄 Loading AI model... This may take a minute on first run."):
        pf = ProfanityFilter(model_path="./", threshold=threshold)
    return pf

# Header
st.title("🛡️ AI Profanity Filter")
st.markdown("""
    Powered by **mDeBERTa-v3-base-mnli-xnli** zero-shot classification model.
    This filter detects and censors inappropriate content in **100+ languages**.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Threshold slider
    threshold = st.slider(
        "Detection Sensitivity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Lower values are more sensitive and may catch more content (including false positives)"
    )
    
    # Filtering mode
    mode = st.selectbox(
        "Filtering Mode",
        options=["full", "word", "aggressive"],
        index=0,
        help="""
        - **full**: Censors entire text with asterisks
        - **word**: Censors at sentence level
        - **aggressive**: Replaces with warning message
        """
    )
    
    st.divider()
    
    # Statistics
    st.header("📊 Statistics")
    if st.session_state.history:
        total_checks = len(st.session_state.history)
        profane_count = sum(1 for h in st.session_state.history if h['is_profane'])
        clean_count = total_checks - profane_count
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Checks", total_checks)
        with col2:
            st.metric("Flagged", profane_count)
        
        if total_checks > 0:
            st.progress(profane_count / total_checks)
            st.caption(f"{(profane_count/total_checks*100):.1f}% flagged as inappropriate")
    else:
        st.info("No checks yet")
    
    st.divider()
    
    # Clear history
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    
    st.divider()
    
    # About
    st.header("ℹ️ About")
    st.markdown("""
        This tool uses AI to detect inappropriate content without relying on word lists.
        
        **Features:**
        - Zero-shot classification
        - Multilingual support (100+ languages)
        - Configurable sensitivity
        - Multiple filtering modes
        
        **Model:** mDeBERTa-v3-base-mnli-xnli
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input Text")
    
    # Text input
    input_text = st.text_area(
        "Enter text to check:",
        height=200,
        placeholder="Type or paste text here...",
        help="Enter any text in any language"
    )
    
    # Example texts
    with st.expander("📋 Try Example Texts"):
        examples = [
            "Hello! How are you doing today?",
            "This is a wonderful project to work on.",
            "I appreciate your help with this code.",
            "The weather is beautiful today.",
            "Thank you for being so kind and helpful!"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"Example {i+1}", key=f"example_{i}", use_container_width=True):
                input_text = example
                st.rerun()
    
    # Process button
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        process_button = st.button("🔍 Check & Filter", type="primary", use_container_width=True)
    with col_btn2:
        clear_button = st.button("🔄 Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()

with col2:
    st.header("✅ Filtered Output")
    
    # Process the text
    if process_button and input_text.strip():
        # Load model if not loaded
        if not st.session_state.model_loaded or st.session_state.filter is None:
            st.session_state.filter = load_model(threshold)
            st.session_state.model_loaded = True
        
        # Process text
        start_time = time.time()
        result = st.session_state.filter.filter(input_text, mode=mode)
        process_time = time.time() - start_time
        
        # Add to history
        st.session_state.history.append({
            'is_profane': result['is_profane'],
            'confidence': result['confidence']
        })
        
        # Display results
        if result['is_profane']:
            st.error("⚠️ Inappropriate content detected!")
            
            # Show filtered output
            st.text_area(
                "Filtered Text:",
                value=result['filtered'],
                height=200,
                disabled=True
            )
        else:
            st.success("✅ Content appears clean!")
            
            # Show original text
            st.text_area(
                "Output:",
                value=result['filtered'],
                height=200,
                disabled=True
            )
        
        # Metrics
        st.divider()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            confidence_color = "🔴" if result['is_profane'] else "🟢"
            st.metric(
                "Confidence",
                f"{result['confidence']:.1%}",
                delta=None
            )
        
        with col_m2:
            st.metric(
                "Status",
                "Flagged" if result['is_profane'] else "Clean"
            )
        
        with col_m3:
            st.metric(
                "Process Time",
                f"{process_time:.2f}s"
            )
        
        # Classification details
        with st.expander("📊 Classification Details"):
            st.write("**Top Classification:**", result['label'])
            st.write("**Confidence Score:**", f"{result['confidence']:.4f}")
            st.write("**Threshold Used:**", threshold)
            st.write("**Filtering Mode:**", mode)
            
            # Show confidence bar
            st.progress(result['confidence'])
    
    elif process_button:
        st.warning("⚠️ Please enter some text to check")
    else:
        st.info("👈 Enter text and click 'Check & Filter' to begin")

# History section (collapsible)
if st.session_state.history:
    st.divider()
    with st.expander(f"📜 Recent History ({len(st.session_state.history)} checks)", expanded=False):
        # Show last 10 items
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            status_emoji = "🔴" if item['is_profane'] else "🟢"
            status_text = "Flagged" if item['is_profane'] else "Clean"
            st.write(f"{status_emoji} Check #{len(st.session_state.history)-i}: {status_text} (confidence: {item['confidence']:.2%})")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        <p>Built with Streamlit | Powered by mDeBERTa-v3-base-mnli-xnli</p>
        <p style='font-size: 0.8rem;'>Note: First run may take longer as the model loads into memory</p>
    </div>
""", unsafe_allow_html=True)
