"""Define a simple chatbot agent.

This agent returns a predefined response without using an actual LLM.
"""
from datetime import datetime, timedelta
from typing import Literal

from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

from langchain.chat_models import init_chat_model
from agent.utils import load_chatollama_model
from langgraph.prebuilt import create_react_agent
from agent.state import State, Router, email_detection, EmailInput
from agent.google_auth import get_gmail_service, get_calendar_service, create_message
from agent.prompts import triage_system_prompt, triage_user_prompt, prompt_instructions, profile, agent_system_prompt_memory
from langmem import create_manage_memory_tool, create_search_memory_tool # type: ignore
from langchain_core.tools import tool
from dotenv import load_dotenv
from agent.configuration import Configuration



_ = load_dotenv()

llm = init_chat_model("openai:gpt-4o-mini")

#llm = load_chatollama_model()
gemma3 = load_chatollama_model()
llm_router = gemma3.with_structured_output(Router)
llm_detection = gemma3.with_structured_output(email_detection)
llm_parser = gemma3.with_structured_output(EmailInput)


@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write and send an email using Gmail API."""
    service = get_gmail_service()
    message = create_message(to, subject, content)
    send_message = service.users().messages().send(userId="me", body=message).execute()
    return f"Email sent to {to} with subject '{subject}'. Message ID: {send_message['id']}"

@tool
def schedule_meeting(attendees: list[str], subject: str, duration_minutes: int, preferred_day: str) -> str:
    """Schedule a calendar meeting."""
    service = get_calendar_service()
    
    start_time = datetime.strptime(preferred_day, "%Y-%m-%d")
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        "summary": subject,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        "attendees": [{"email": email} for email in attendees],
    }
    
    event_result = service.events().insert(calendarId="primary", body=event).execute()
    return f"Meeting '{subject}' scheduled on {preferred_day} with {len(attendees)} attendees. Event ID: {event_result['id']}"

@tool
def check_calendar_availability(day: str) -> str:
    """Check calendar availability for a given day."""
    service = get_calendar_service()
    
    start_time = datetime.strptime(day, "%Y-%m-%d").isoformat() + "Z"
    end_time = (datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)).isoformat() + "Z"
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    events = events_result.get("items", [])
    if not events:
        return f"No events found for {day}. You are available all day."
    
    available_times = []
    busy_times = [(event["start"].get("dateTime", event["start"].get("date"))) for event in events]
    
    return f"Busy times on {day}: {', '.join(busy_times)}" if busy_times else f"No busy times on {day}."



manage_memory_tool = create_manage_memory_tool(
    namespace=(
        "email_assistant", 
        "{langgraph_user_id}",
        "collection"
    )
)


search_memory_tool = create_search_memory_tool(
    namespace=(
        "email_assistant",
        "{langgraph_user_id}",
        "collection"
    )

)

def create_prompt(state):
    return [
        {
            "role": "system", 
            "content": agent_system_prompt_memory.format(
                instructions=prompt_instructions["agent_instructions"], 
                **profile
            )
        }
    ] + state['messages']


tools= [
    write_email, 
    schedule_meeting,
    check_calendar_availability,
    manage_memory_tool,
    search_memory_tool
]
response_agent = create_react_agent(
    llm,
    tools=tools,
    prompt=create_prompt,
    config_schema=Configuration)



def detect_email(state: State) -> Command[Literal["triage_router", "response_agent"]]:

    result = llm_detection.invoke(
        [
            {"role": "system", "content": "Your job is to decide if the user have recieved an email and wanted to managed, or the user have another request(question, demand to sent an email, ..ect)."},
            {"role": "user", "content": state['email_input']},
        ]
    )

    if result.email_found == True:
        print("📧 Email recieved in the input.")
        goto = "triage_router"
        update = None
    else:
        print("🚫 Other request.")
        goto = "response_agent"
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{state['email_input']}",
                }
            ]
        }
    
    return Command(goto=goto, update=update)



def triage_router(state: State) -> Command[
    Literal["response_agent"]
]:

    email_info = llm_parser.invoke(
        [
            {"role": "system", "content": "You are an email parser. Your job is to extract the email details."},
            {"role": "user", "content": state['email_input']},
        ]
    )


    author = email_info.author_name+ " <" + email_info.author_email + ">"
    to = email_info.to_name + " <" + email_info.to_email + ">"
    subject = email_info.subject
    email_thread = email_info.email_thread
    

    system_prompt = triage_system_prompt.format(
        full_name=profile["full_name"],
        name=profile["name"],
        user_profile_background=profile["user_profile_background"],
        triage_no=prompt_instructions["triage_rules"]["ignore"],
        triage_notify=prompt_instructions["triage_rules"]["notify"],
        triage_email=prompt_instructions["triage_rules"]["respond"],
        examples=None
    )
    user_prompt = triage_user_prompt.format(
        author=author, 
        to=to, 
        subject=subject, 
        email_thread=email_thread
    )
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    if result.classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        goto = "response_agent"
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Use search memory tool if necessary and then Respond to the email {user_prompt} and don't forget to update the memory in the end.",
                }
            ]
        }
    elif result.classification == "ignore":
        print("🚫 Classification: IGNORE - This email can be safely ignored")
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": "Tell the user that the email is ignored.",
                }
            ]
        }
        goto = "response_agent"
    elif result.classification == "notify":
        # If real life, this would do something else
        print("🔔 Classification: NOTIFY - This email contains important information")
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": "Tell the user that the email is important and notify him.",
                }
            ]
        }
        goto = "response_agent"
    else:
        raise ValueError(f"Invalid classification: {result.classification}")
    return Command(goto=goto, update=update)


email_agent = StateGraph(State, config_schema=Configuration)
email_agent = email_agent.add_node(triage_router)
email_agent = email_agent.add_node(detect_email)
email_agent = email_agent.add_node("response_agent", response_agent)
email_agent = email_agent.add_edge(START, "detect_email")
email_agent = email_agent.compile()