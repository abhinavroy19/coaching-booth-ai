import os
import json
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Coaching Booth AI", layout="centered")

st.title("Coaching Booth AI - Interactive")
st.write("Multi-step AI coaching assistant")

file_name = "ai_memory.json"

# Load memory
if os.path.exists(file_name):
    with open(file_name, "r") as f:
        memory_data = json.load(f)
else:
    memory_data = []

recent_memory = memory_data[-3:] if len(memory_data) > 0 else []

# Session state to store steps
if "step" not in st.session_state:
    st.session_state.step = 1

# Step 1: Enter problem
if st.session_state.step == 1:

    problem = st.text_area("Enter the problem:")

    if st.button("Analyze"):
        if problem.strip() == "":
            st.warning("Please enter a problem")
        else:
            st.session_state.problem = problem

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=f"""
Use memory if relevant:
{recent_memory}

Problem:
{problem}

Do:
1. Analyze in 3 bullet points
2. Ask one clarifying question
"""
            )

            st.session_state.analysis_question = response.output_text
            st.session_state.step = 2
            st.rerun()

# Step 2: Show question + take answer
elif st.session_state.step == 2:

    st.subheader("Analysis + Clarifying Question")
    st.write(st.session_state.analysis_question)

    user_answer = st.text_input("Your answer:")

    if st.button("Submit Answer"):
        if user_answer.strip() == "":
            st.warning("Please provide an answer")
        else:
            st.session_state.user_answer = user_answer
            st.session_state.step = 3
            st.rerun()

# Step 3: Final response
elif st.session_state.step == 3:

    with st.spinner("Generating final response..."):

        final_response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
Use this context:

Recent memory:
{recent_memory}

Problem:
{st.session_state.problem}

Analysis and question:
{st.session_state.analysis_question}

User answer:
{st.session_state.user_answer}

Give:
1. Refined understanding
2. Key insight
3. Recommended next steps
"""
        )

        final_output = final_response.output_text

        st.subheader("Final Response")
        st.write(final_output)

        # Save to memory
        data = {
            "problem": st.session_state.problem,
            "analysis_and_question": st.session_state.analysis_question,
            "answer": st.session_state.user_answer,
            "final_output": final_output
        }

        memory_data.append(data)

        with open(file_name, "w") as f:
            json.dump(memory_data, f, indent=4)

        st.success("Session saved")

    # Reset button
    if st.button("Start New Session"):
        st.session_state.step = 1
        st.session_state.clear()
        st.rerun()