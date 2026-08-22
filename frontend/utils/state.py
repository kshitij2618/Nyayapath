"""
Central place for Streamlit session_state defaults and the tiny
stage-machine that drives the screen flow:

    input -> advice -> [questions -> anything_else] -> result -> draft

Keeping this in one module means app.py and every component read/write
state the same way, instead of each file inventing its own keys.
"""

import streamlit as st

STAGES = ["input", "advice", "questions", "anything_else", "result", "draft"]


def init_state():
    defaults = {
        "stage": "input",
        "lang": "en",
        "problem_text": "",
        "analysis": None,       # dict returned by /analyze
        "answers": {},          # {question_id: answer_text}
        "extra_info": "",
        "final_result": None,   # dict returned by /final-result
        "draft": None,          # dict returned by /generate-draft
        "draft_edited_text": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(stage: str):
    assert stage in STAGES, f"Unknown stage: {stage}"
    st.session_state.stage = stage
    st.rerun()


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
    st.rerun()
