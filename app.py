import streamlit as st
import os
import sys
import time

# Path setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv optional

# Safe imports — show a clear error instead of blank page
_import_errors = []

try:
    from prompts.templates import NICHE_TOPICS
except Exception as e:
    _import_errors.append(f"prompts.templates: {e}")
    NICHE_TOPICS = {
        "Generative AI": ["GPT-4 and large language models reshaping enterprise workflows"],
        "Agentic AI": ["AI agents that autonomously complete multi-step business tasks"],
        "RAG": ["RAG vs fine-tuning: when to use which approach"],
        "Multimodal RAG": ["Multimodal RAG: combining text, images, and tables from PDFs"],
    }

try:
    from utils.helpers import count_words, format_word_count_badge, extract_sections, get_timestamp
except Exception as e:
    _import_errors.append(f"utils.helpers: {e}")


    def count_words(t):
        return len(t.split())


    def format_word_count_badge(n):
        return (f"{n} words", "green" if n <= 220 else "red")


    def extract_sections(t):
        return {"hook": "", "description": "", "highlights": [], "closing": "", "hashtags": []}


    def get_timestamp():
        return ""

try:
    from utils.tracing import setup_langsmith
except Exception as e:
    _import_errors.append(f"utils.tracing: {e}")


    def setup_langsmith():
        return False

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkedIn Post Generator · AI Niche",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dependency Check (shown before anything else) ─────────────────────────────
if _import_errors:
    st.error("⚠️ Some modules failed to import. Run the command below to fix:")
    st.code("pip install -r requirements.txt", language="bash")
    st.markdown("**Import errors:**")
    for err in _import_errors:
        st.markdown(f"- `{err}`")
    st.stop()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

  .stApp { background: #0a0a0f; color: #e8e8f0; }

  /* Header */
  .hero-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a0533 50%, #0d1b2a 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 60% 50%, rgba(139,92,246,0.08) 0%, transparent 60%);
    pointer-events: none;
  }
  .hero-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem 0;
  }
  .hero-subtitle {
    color: rgba(200,200,220,0.7);
    font-size: 0.95rem;
    font-weight: 400;
    margin: 0;
  }

  /* Cards */
  .config-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  /* Post output card */
  .post-card {
    background: linear-gradient(145deg, #0f1923, #111827);
    border: 1px solid rgba(99, 179, 237, 0.25);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    line-height: 1.75;
    color: #e2e8f0;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 0 40px rgba(99,179,237,0.06);
  }

  /* Section badges */
  .section-label {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.4rem;
  }
  .label-hook { background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
  .label-desc { background: rgba(59,130,246,0.15); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
  .label-highlights { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
  .label-closing { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
  .label-hashtags { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.3); }

  /* Metrics row */
  .metric-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  .pill-green { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
  .pill-orange { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
  .pill-red { background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }

  /* Pipeline steps */
  .pipeline-step {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 0.85rem;
    transition: all 0.3s;
  }
  .step-pending { background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.4); }
  .step-running { background: rgba(99,179,237,0.1); color: #93c5fd; border: 1px solid rgba(99,179,237,0.2); }
  .step-done { background: rgba(16,185,129,0.1); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2); }
  .step-error { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.2); }

  /* History items */
  .history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  .history-item:hover { border-color: rgba(139,92,246,0.4); }

  /* Sidebar */
  .css-1d391kg, [data-testid="stSidebar"] {
    background: #050508 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }

  /* Inputs */
  .stSelectbox > div, .stTextArea > div > div, .stTextInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
  }

  .stTextArea textarea { color: #e2e8f0 !important; background: transparent !important; }

  div[data-testid="stStatusWidget"] { display: none; }
  .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None
if "post_state" not in st.session_state:
    st.session_state.post_state = None
if "openai_key_set" not in st.session_state:
    st.session_state.openai_key_set = bool(os.getenv("OPENAI_API_KEY"))

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # API Keys
    with st.expander("🔑 API Keys", expanded=not st.session_state.openai_key_set):
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            placeholder="sk-..."
        )
        langsmith_key = st.text_input(
            "LangSmith API Key (optional)",
            type="password",
            value=os.getenv("LANGCHAIN_API_KEY", ""),
            placeholder="ls__..."
        )
        langsmith_project = st.text_input(
            "LangSmith Project",
            value=os.getenv("LANGCHAIN_PROJECT", "linkedin-post-generator")
        )

        if st.button("💾 Save Keys"):
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
                st.session_state.openai_key_set = True
            if langsmith_key:
                os.environ["LANGCHAIN_API_KEY"] = langsmith_key
                os.environ["LANGCHAIN_PROJECT"] = langsmith_project
                setup_langsmith()
            st.success("Keys saved for this session!")

    st.divider()

    # Model settings
    st.markdown("### 🧠 Model Settings")
    model_temp = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1,
                           help="Higher = more creative, Lower = more focused")
    max_words = st.slider("Max Word Count", 150, 220, 220, 10)

    st.divider()

    # Post History
    st.markdown("### 📚 Post History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            with st.container():
                st.markdown(f"""<div class="history-item">
                    <div style="font-size:0.75rem;color:#a78bfa;font-weight:600">{item['niche']}</div>
                    <div style="font-size:0.8rem;color:#e2e8f0;margin-top:2px">{item['topic'][:45]}...</div>
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.35);margin-top:4px">{item['timestamp']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Load", key=f"load_{i}"):
                    st.session_state.generated_post = item['post']
    else:
        st.markdown("<div style='color:rgba(255,255,255,0.3);font-size:0.8rem'>No posts generated yet.</div>",
                    unsafe_allow_html=True)

    st.divider()

    # Graph visualization
    st.markdown("### 🔀 Pipeline")
    pipeline_steps = [
        ("🔬", "Research & Insights"),
        ("💡", "Hook Generation"),
        ("✍️", "Draft Post"),
        ("🔍", "Quality Check"),
        ("✨", "Refinement"),
        ("🏷️", "Hashtag Engine"),
    ]
    for icon, step in pipeline_steps:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;padding:5px 0;font-size:0.82rem;color:rgba(200,200,220,0.6)'><span>{icon}</span><span>{step}</span></div>",
            unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="hero-header">
  <div class="hero-title">🤖 LinkedIn Post Generator</div>
  <div class="hero-subtitle">Agentic AI · Multi-step LangGraph pipeline · Powered by GPT-4o · Traced via LangSmith</div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.1], gap="large")

# ── LEFT COLUMN: Input ────────────────────────────────────────────────────────
with col_left:
    st.markdown("#### 📝 Post Configuration")

    # Niche selector
    selected_niche = st.selectbox(
        "Select AI Niche",
        options=list(NICHE_TOPICS.keys()),
        index=0
    )

    # Topic selector
    topic_options = NICHE_TOPICS[selected_niche]
    topic_mode = st.radio("Topic Mode", ["Choose from list", "Custom topic"], horizontal=True)

    if topic_mode == "Choose from list":
        selected_topic = st.selectbox("Select Topic", options=topic_options)
    else:
        selected_topic = st.text_input(
            "Enter custom topic",
            placeholder="e.g. How LangGraph enables stateful multi-agent workflows"
        )

    # Additional context
    custom_context = st.text_area(
        "Additional Context (optional)",
        placeholder="Add specific insights, stats, personal angle, or target audience notes...",
        height=100
    )

    # Refinement feedback
    with st.expander("🔄 Refinement Options"):
        refinement_feedback = st.text_area(
            "Feedback for refinement (optional)",
            placeholder="e.g. Make the hook more provocative, shorten bullet points...",
            height=80
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate button
    generate_btn = st.button("🚀 Generate LinkedIn Post", use_container_width=True)

    # Status messages
    status_placeholder = st.empty()

# ── RIGHT COLUMN: Output ──────────────────────────────────────────────────────
with col_right:
    st.markdown("#### 📤 Generated Post")

    output_placeholder = st.empty()
    metrics_placeholder = st.empty()
    actions_placeholder = st.empty()

    if st.session_state.generated_post:
        post = st.session_state.generated_post
        wc = count_words(post)
        wc_label, wc_color = format_word_count_badge(wc)
        pill_class = {"green": "pill-green", "orange": "pill-orange", "red": "pill-red"}[wc_color]

        output_placeholder.markdown(
            f'<div class="post-card">{post}</div>',
            unsafe_allow_html=True
        )

        metrics_placeholder.markdown(f"""
        <div style="display:flex;gap:10px;margin-top:0.8rem;flex-wrap:wrap">
          <span class="metric-pill {pill_class}">{wc_label}</span>
          <span class="metric-pill pill-green">✅ Formatted</span>
        </div>
        """, unsafe_allow_html=True)

        with actions_placeholder.container():
            a1, a2, a3 = st.columns(3)
            with a1:
                st.download_button(
                    "📋 Download",
                    data=post,
                    file_name=f"linkedin_post_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with a2:
                if st.button("🔁 Regenerate", use_container_width=True):
                    st.session_state.generated_post = None
                    st.rerun()
            with a3:
                if st.button("🧹 Clear", use_container_width=True):
                    st.session_state.generated_post = None
                    st.session_state.post_state = None
                    st.rerun()
    else:
        output_placeholder.markdown("""
        <div style="border:1px dashed rgba(255,255,255,0.1);border-radius:16px;padding:3rem;text-align:center;color:rgba(255,255,255,0.25)">
          <div style="font-size:2.5rem;margin-bottom:1rem">✍️</div>
          <div style="font-size:1rem;font-weight:500">Your LinkedIn post will appear here</div>
          <div style="font-size:0.8rem;margin-top:0.5rem">Configure your niche and topic, then hit Generate</div>
        </div>
        """, unsafe_allow_html=True)

# ── Generation Logic ──────────────────────────────────────────────────────────
if generate_btn:
    if not os.getenv("OPENAI_API_KEY"):
        status_placeholder.error("⚠️ Please set your OpenAI API key in the sidebar.")
    elif not selected_topic:
        status_placeholder.warning("Please select or enter a topic.")
    else:
        try:
            from graphs.post_graph import get_graph

            graph = get_graph()

            initial_state = {
                "niche": selected_niche,
                "topic": selected_topic,
                "custom_context": custom_context or "",
                "research_insights": [],
                "hook_alternatives": [],
                "draft_post": "",
                "word_count": 0,
                "final_post": "",
                "hashtags": [],
                "error": None,
                "refinement_feedback": refinement_feedback or "",
                "needs_refinement": False,
            }

            # Use st.status — safe container that doesn't cause white screen
            with status_placeholder:
                with st.status("⚡ Running Agentic Pipeline...", expanded=True) as status_box:
                    st.write("🔬 Step 1/6 — Researching insights...")
                    st.write("💡 Step 2/6 — Generating hooks...")
                    st.write("✍️ Step 3/6 — Drafting post...")
                    st.write("🔍 Step 4/6 — Quality check...")
                    st.write("✨ Step 5/6 — Refining...")
                    st.write("🏷️ Step 6/6 — Adding hashtags...")

                    # Single blocking invoke — no streaming, no mid-loop UI updates
                    final_state = graph.invoke(
                        initial_state,
                        config={
                            "run_name": "linkedin_post_generator",
                        }
                    )

                    if final_state and final_state.get("final_post"):
                        status_box.update(label="✅ Post generated!", state="complete", expanded=False)
                    else:
                        status_box.update(label="❌ Generation failed", state="error", expanded=True)

            if final_state and final_state.get("final_post"):
                post = final_state["final_post"]
                st.session_state.generated_post = post
                st.session_state.history.append({
                    "niche": selected_niche,
                    "topic": selected_topic,
                    "post": post,
                    "timestamp": get_timestamp()
                })
                st.rerun()
            else:
                err = final_state.get("error", "Unknown error") if final_state else "Graph returned no state"
                status_placeholder.error(f"❌ {err}")

        except ImportError as e:
            status_placeholder.error(f"❌ Import error: {e}\n\nRun: `pip install -r requirements.txt`")
        except Exception as e:
            status_placeholder.error(f"❌ Generation failed: {str(e)}")

# ── Section Breakdown (below main) ───────────────────────────────────────────
if st.session_state.generated_post:
    st.divider()
    st.markdown("#### 🔍 Post Breakdown")

    sections = extract_sections(st.session_state.generated_post)

    b_col1, b_col2 = st.columns(2)

    with b_col1:
        if sections["hook"]:
            st.markdown('<span class="section-label label-hook">Hook</span>', unsafe_allow_html=True)
            st.markdown(f"> {sections['hook']}")

        if sections["description"]:
            st.markdown('<span class="section-label label-desc">Description</span>', unsafe_allow_html=True)
            st.markdown(sections["description"])

    with b_col2:
        if sections["highlights"]:
            st.markdown('<span class="section-label label-highlights">Key Highlights</span>', unsafe_allow_html=True)
            for bullet in sections["highlights"]:
                st.markdown(bullet)

        if sections["closing"]:
            st.markdown('<span class="section-label label-closing">Closing</span>', unsafe_allow_html=True)
            st.markdown(f"*{sections['closing']}*")

        if sections["hashtags"]:
            st.markdown('<span class="section-label label-hashtags">Hashtags</span>', unsafe_allow_html=True)
            st.markdown(" ".join(sections["hashtags"]))

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1.5rem;border-top:1px solid rgba(255,255,255,0.06);text-align:center;color:rgba(255,255,255,0.25);font-size:0.78rem">
  Built with LangGraph · LangChain · LangSmith · OpenAI GPT-4o · Streamlit
</div>
""", unsafe_allow_html=True)