import os
import json
from datetime import datetime
import re
import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.tools import FunctionTool
from src.global_settings import INDEX_STORAGE, CONVERSATION_FILE, SCORES_FILE
from src.prompts import CUSTORM_AGENT_SYSTEM_TEMPLATE


user_avatar = "data/images/user.png"
professor_avatar = "data/images/professor.png"

def load_chat_store():
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store


def display_messages(chat_store, container, key):
    with container:
        for message in chat_store.get_messages(key=key):
            if message.role == "user":
                with st.chat_message(message.role, avatar=user_avatar):
                    st.markdown(message.content)
            elif message.role == "assistant" and message.content != None:
                with st.chat_message(message.role, avatar=professor_avatar):
                    st.markdown(message.content)

def save_score(score, content, total_guess, username):
        """Write score and content to a file in a robust JSON list format and return the saved entry.

        Args:
            score (string): Score of the user's mental health.
            content (string): Content of the user's mental health.
            total_guess (int|str): Total guess of the user's mental health.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "username": username,
            "Time": current_time,
            "Score": score,
            "Content": content,
            "Total guess": int(total_guess) if str(total_guess).isdigit() else total_guess,
        }
        data = []
        if os.path.exists(SCORES_FILE) and os.path.getsize(SCORES_FILE) > 0:
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if isinstance(existing, list):
                    data = existing
                elif isinstance(existing, dict):
                    data = [existing]
                else:
                    data = []
            except json.JSONDecodeError:
                # Fallback: try to read as JSON Lines (one JSON object per line)
                try:
                    with open(SCORES_FILE, "r", encoding="utf-8") as f:
                        lines = [json.loads(line) for line in f if line.strip()]
                    data = lines
                except Exception:
                    data = []
        data.append(new_entry)
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return new_entry

# Helpers to normalize and extract structured values from LLM output

def _normalize_score_label(raw_score: str) -> str:
    s = str(raw_score or "").strip().lower()
    if not s:
        return "Average"
    bad_synonyms = {"bad", "poor", "low", "worse", "severe", "critical"}
    good_synonyms = {"good", "very good", "excellent", "strong", "healthy"}
    quite_good_synonyms = {"quite good", "fairly good", "okay", "ok", "improving", "better", "fair"}
    average_synonyms = {"average", "moderate", "neutral", "medium"}
    if s in bad_synonyms:
        return "Bad"
    if s in good_synonyms:
        return "Good"
    if s in quite_good_synonyms:
        return "Quite good"
    if s in average_synonyms:
        return "Average"
    # Fallback mapping by keyword
    if any(k in s for k in ["severe", "poor", "bad"]):
        return "Bad"
    if any(k in s for k in ["very good", "excellent", "good"]):
        return "Good"
    if any(k in s for k in ["quite", "fair", "improv", "okay", "ok", "better"]):
        return "Quite good"
    return "Average"


def _extract_structured_summary(raw_text: str):
    """Extract score, total_guess, and content from an LLM response that should be JSON."""
    text = (raw_text or "").strip()
    # Strip code fences if present
    if text.startswith("```"):
        # Remove first fence
        text = re.sub(r"^```(?:json)?\s*", "", text)
        # Remove ending fence
        text = re.sub(r"```\s*$", "", text)
        text = text.strip()
    data = None
    # Try direct JSON parse
    try:
        data = json.loads(text)
    except Exception:
        # Try to locate first JSON object substring
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                data = None
    if not isinstance(data, dict):
        data = {}
    content = data.get("content") or data.get("summary") or raw_text
    score_raw = data.get("score") or data.get("Score") or "Average"
    total_guess_raw = data.get("total_guess") or data.get("Total guess") or 1
    # Normalize total_guess
    if isinstance(total_guess_raw, str):
        m = re.search(r"\d+", total_guess_raw)
        total_guess_val = int(m.group(0)) if m else 1
    else:
        try:
            total_guess_val = int(total_guess_raw)
        except Exception:
            total_guess_val = 1
    score_val = _normalize_score_label(score_raw)
    return score_val, total_guess_val, content

def initialize_chatbot(chat_store, container, username, user_info):
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000, chat_store=chat_store, chat_store_key=username)
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    index = load_index_from_storage(storage_context,index_id='vector')
    dsm5_engine = index.as_query_engine(similarity_top_k=3)
    dsm5_tool = QueryEngineTool(query_engine=dsm5_engine, metadata=ToolMetadata(name="dsm5", description = f"Cung cấp các thông tin liên quan đến các bệnh "
                f"tâm thần theo tiêu chuẩn DSM5. Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ"))
    save_tool = FunctionTool.from_defaults(fn=save_score)

    agent = OpenAIAgent.from_tools(
        tools=[dsm5_tool, save_tool], 
        memory=memory,
        system_prompt=CUSTORM_AGENT_SYSTEM_TEMPLATE.format(user_info=user_info)
    )
    display_messages(chat_store, container, key=username)
    return agent

def chat_interface(agent, chat_store, container):  
    if not os.path.exists(CONVERSATION_FILE) or os.path.getsize(CONVERSATION_FILE) == 0:
        with container:
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown("Hi I'm Mental Health Assistant. Let's get started!")
    prompt = st.chat_input("Input your messages here...")
    if prompt:
        with container:
            with st.chat_message(name="user", avatar=user_avatar):
                st.markdown(prompt)
            response = str(agent.chat(prompt))
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown(response)
        chat_store.persist(CONVERSATION_FILE)



    if st.button("📝 Generate Mental Health Summary"):
        with st.spinner("Analyzing conversation and generating summary..."):
            # Prepare prompt asking for structured JSON only
            username = st.session_state.get("username", "unknown_user")
            summary_prompt = (
                "Based on the entire conversation so far, produce a SINGLE JSON object only (no extra text, no code fences) "
                "with the following keys: "
                "score (one of: 'Bad', 'Average', 'Quite good', 'Good'), "
                "total_guess (integer number of distinct conditions you considered), and "
                "content (a concise, clear mental health summary and preliminary diagnosis)."
            )
            summary_response = str(agent.chat(summary_prompt))

            # Parse values from LLM response
            score, total_guess, content = _extract_structured_summary(summary_response)

            # Persist via robust saver
            saved_entry = save_score(score=score, content=content, total_guess=total_guess, username=username)

            # Feedback
            st.success("Summary generated and saved!")
            st.json(saved_entry)
