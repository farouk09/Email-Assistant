from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def parse_email(email_input: dict) -> dict:
    """Parse an email input dictionary.

    Args:
        email_input (dict): Dictionary containing email fields:
            - author: Sender's name and email
            - to: Recipient's name and email
            - subject: Email subject line
            - email_thread: Full email content

    Returns:
        tuple[str, str, str, str]: Tuple containing:
            - author: Sender's name and email
            - to: Recipient's name and email
            - subject: Email subject line
            - email_thread: Full email content
    """
    return (
        email_input["author"],
        email_input["to"],
        email_input["subject"],
        email_input["email_thread"],
    )

def format_few_shot_examples(examples):
    """Format examples into a readable string representation.

    Args:
        examples (List[Item]): List of example items from the vector store, where each item
            contains a value string with the format:
            'Email: {...} Original routing: {...} Correct routing: {...}'

    Returns:
        str: A formatted string containing all examples, with each example formatted as:
            Example:
            Email: {email_details}
            Original Classification: {original_routing}
            Correct Classification: {correct_routing}
            ---
    """
    formatted = []
    for example in examples:
        # Parse the example value string into components
        email_part = example.value.split('Original routing:')[0].strip()
        original_routing = example.value.split('Original routing:')[1].split('Correct routing:')[0].strip()
        correct_routing = example.value.split('Correct routing:')[1].strip()
        
        # Format into clean string
        formatted_example = f"""Example:
Email: {email_part}
Original Classification: {original_routing}
Correct Classification: {correct_routing}
---"""
        formatted.append(formatted_example)
    
    return "\n".join(formatted)




def load_chatollama_model():
    """Load a chat model from Ollama."""
    llm = ChatOllama(
        model="gemma3:27b",
        temperature=0,
        # other params...
    )

    return llm

def load_model(fully_specified_name: str):
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """

    inference_server_url = "http://localhost:8000/v1"

    model = ChatOpenAI(
        model=fully_specified_name,
        openai_api_key="token-abc123",
        openai_api_base=inference_server_url,
        temperature=0,
    )

    return model


def parse_email_with_langchain(llm , email_input: str) -> dict:
    """Use LangChain with an LLM to extract email details into structured JSON."""
    
    # Define the expected fields
    response_schemas = [
        ResponseSchema(name="author_name", description="The sender's name"),
        ResponseSchema(name="author_email", description="The sender's email"),
        ResponseSchema(name="to_name", description="The recipient's name"),
        ResponseSchema(name="to_email", description="The recipient's email"),
        ResponseSchema(name="subject", description="The email subject"),
        ResponseSchema(name="email_thread", description="The main content of the email")
    ]
    
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    
    prompt_template = PromptTemplate(
        template="Extract the following details from this email:\n\n{email}\n\n{format_instructions}",
        input_variables=["email"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
        
    _input = prompt_template.format(email=email_input)
    output = llm.invoke(_input)

    print(output.content)
    return parser.parse(output.content)


