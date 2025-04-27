from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Annotated
from langgraph.graph import add_messages


class Router(BaseModel):
    """Analyze the unread email and route it according to its content."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply or for any user request.",
    )


class EmailInput(BaseModel):
    author_name: str = Field(
        description="The name of the sender of the email.",
    )
    author_email: str = Field(
        description="The email address of the sender.",
    )
    to_name: str = Field(
        description="The name of the primary recipient."
    )
    to_email: str = Field(
        description="The email address of the primary recipient."
    )
    subject: str = Field(
        description="The subject line of the email."
    )
    email_thread: str = Field(
        description="The main content or body of the email."
    )


class email_detection(BaseModel):
    email_found: bool = Field(default=False, description="True if the user have recieved an email, False otherwise")

class State(TypedDict):
    email_input: str
    messages: Annotated[list, add_messages]

    
