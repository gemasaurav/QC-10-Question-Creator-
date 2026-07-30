import streamlit as st
from openai import OpenAI
import os

# Page config
st.set_page_config(
    page_title="QC:10 - Question Creator",
    page_icon="❓",
    layout="centered"
)

# Custom CSS for a clean look
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E88E5;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .question-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        padding: 1rem 1.2rem;
        margin: 0.6rem 0;
        border-radius: 0 8px 8px 0;
        font-size: 1.05rem;
    }
    .answer-reveal {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        color: #1565c0;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">❓ QC:10</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Question Creator — Generate 10 questions whose answer is your word</p>', unsafe_allow_html=True)

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "xAI API Key",
        type="password",
        help="Get your key at https://console.x.ai/",
        placeholder="xai-..."
    )
    st.markdown("[Get an xAI API key →](https://console.x.ai/)")
    
    model = st.selectbox(
        "Model",
        ["grok-4.5", "grok-3", "grok-2"],
        index=0
    )
    
    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. Enter any word, name, place, number, etc.\n"
        "2. Click **Generate 10 Questions**\n"
        "3. AI creates 10 unique questions where the answer is exactly what you entered."
    )
    st.divider()
    st.caption("Powered by Grok • Built for fun & learning")

# Main input
word = st.text_input(
    "Enter a word / name / place / number / anything:",
    placeholder="e.g. Einstein, Taj Mahal, 42, Tesla Model S, Quantum Physics...",
    max_chars=100
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_btn = st.button("✨ Generate 10 Questions", type="primary", use_container_width=True)

def generate_questions(answer: str, api_key: str, model: str) -> list[str]:
    """Call Grok to generate 10 questions whose answer is the given word."""
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )
    
    prompt = f"""You are a creative question designer. 

The user has given this answer: "{answer}"

Create exactly 10 interesting, varied, and high-quality questions where the correct answer is precisely "{answer}".

Rules:
- Each question must have "{answer}" as the only correct answer.
- Make questions of different types: factual, riddle-like, descriptive, historical, scientific, fun, etc. depending on the nature of the answer.
- Do NOT include the answer in the questions.
- Number them 1 to 10.
- Keep questions clear and engaging.
- Output ONLY the 10 numbered questions, nothing else (no intro, no explanations).

Example format:
1. What is the capital of France?
2. Which planet is known as the Red Planet?
..."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates high-quality quiz questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1500
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse into list of questions
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    questions = []
    for line in lines:
        cleaned = line
        if cleaned and cleaned[0].isdigit():
            for i, char in enumerate(cleaned):
                if char.isalpha() or char in "\"'“”":
                    cleaned = cleaned[i:]
                    break
            else:
                cleaned = cleaned.lstrip("0123456789.-) ")
        questions.append(cleaned)
    
    return questions[:10]

# Generation logic
if generate_btn:
    if not word or not word.strip():
        st.warning("Please enter a word or phrase first.")
    elif not api_key:
        st.warning("Please enter your xAI API key in the sidebar.")
    else:
        with st.spinner("🧠 Grok is creating 10 clever questions..."):
            try:
                questions = generate_questions(word.strip(), api_key, model)
                
                if not questions:
                    st.error("No questions were generated. Please try again.")
                else:
                    st.success(f"Here are 10 questions whose answer is **{word.strip()}**:")
                    st.markdown("")
                    
                    for i, q in enumerate(questions, 1):
                        st.markdown(f'<div class="question-card"><strong>{i}.</strong> {q}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="answer-reveal">✅ Answer: {word.strip()}</div>', unsafe_allow_html=True)
                    
                    # Download option
                    full_text = f"QC:10 - Questions for: {word.strip()}\n" + "="*40 + "\n\n"
                    for i, q in enumerate(questions, 1):
                        full_text += f"{i}. {q}\n"
                    full_text += f"\nAnswer: {word.strip()}"
                    
                    st.download_button(
                        label="📥 Download as Text",
                        data=full_text,
                        file_name=f"QC10_{word.strip()[:30].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure your API key is valid and you have credits remaining.")

# Footer
st.markdown("---")
st.caption("QC:10 (Question Creator) • Made with ❤️ using Streamlit + Grok")
