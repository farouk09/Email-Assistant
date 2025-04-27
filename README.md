# ✉️ LangGraph Email Assistant

A smart, production-ready email assistant built using [LangGraph](https://www.langchain.com/langgraph) and integrated with Gmail and Google Calendar via Auth0. This assistant is designed to simplify email workflows by:

-  **Classifying** incoming emails as: (respond, ignore, notify)
-  **Drafting responses** to emails intelligently
-  **Scheduling meetings** with context from the conversation
-  **Remembering cross-thread context** using semantic long-term memory
-  Fully secure with Google OAuth authentication through **Auth0**


<img width="747" alt="Screenshot 2025-04-27 at 21 00 17" src="https://github.com/user-attachments/assets/7e31802f-eb42-42cf-899c-0f01dbcb750f" />

---

## Features

- ✅ Real-time email classification
- ✅ Smart response drafting
- ✅ Meeting scheduling via Google Calendar
- ✅ Semantic memory for contextual awareness across threads
- ✅ Can handle user commands like sending emails, retrieving the last sent email, and more
- 🔜 Future: Episodic and procedural memory integration for even more personalized, adaptive behavior

---

##  Example Execution

Below are example images of the email assistant in action:

<img width="860" alt="Screenshot 2025-04-27 at 22 02 57" src="https://github.com/user-attachments/assets/0752a9a3-6a46-4090-bc77-201c2e6f1c41" />

<img width="942" alt="Screenshot 2025-04-27 at 21 22 59" src="https://github.com/user-attachments/assets/0b87a48b-37f2-404a-bca9-625bb0d57d90" />

<img width="929" alt="Screenshot 2025-04-27 at 21 54 05" src="https://github.com/user-attachments/assets/e06bf0b7-4e57-4b9d-8acc-d34242470ce6" />

<img width="929" alt="Screenshot 2025-04-27 at 21 54 53" src="https://github.com/user-attachments/assets/b040a17d-3807-4fff-b86e-b0fa22543882" />

---

## How It Works

The LangGraph-powered assistant uses a graph-based architecture to manage its workflow. Key components include:

### Detect Email Received Node
- This node is responsible for detecting if the input is related to a received email or a general user request.
- If it detects a received email, it forwards it to the Triage Router Node.
- If it detects a simple request (like asking for the last sent email or sending a new email), it forwards it directly to the React Agent.

### Triage Router Node
- This node is responsible for deciding what to do with each incoming email.
- Based on the email's content and metadata, it routes the message to one of three paths:
  - `Respond`
  - `Ignore`
  - `Notify`

### React Agent Node
- If the Triage Router decides the assistant should respond, it forwards the email to a React Agent.
- This agent composes a reply by analyzing context, thread history, and memory.
- It is also capable of handling various user requests, such as:
  - Sending an email to a specified recipient
  - Telling the user the last email they sent
  - Summarizing recent conversations
  - And much more

📸 **Check the image below** to visualize the flow inside LangGraph Studio.

<img width="496" alt="Screenshot 2025-04-27 at 20 59 42" src="https://github.com/user-attachments/assets/0c9fa534-c10f-46a9-ab46-9203794a9636" />

---

## 🛠️ Getting Started

### Prerequisites

1. **Install [`uv`](https://github.com/astral-sh/uv) package manager:**

   ```bash
   pip install uv
   ```

---

### Local Setup

Follow these steps to get the project running locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/langgraph-email-assistant.git
   cd langgraph-email-assistant
   ```

2. **Create your environment file:**

   ```bash
   cp .env.example .env
   ```

   Update it with your Auth0, Gmail, and Calendar credentials.

3. **Set up the virtual environment:**

   a. Create and activate the environment:

   ```bash
   uv venv
   source .venv/bin/activate
   ```

   b. Install dependencies:

   ```bash
   uv run
   ```

4. **Run the LangGraph development server:**

   ```bash
   uv pip install "langgraph-cli[inmem]"
   uv run langgraph dev
   ```

---

### Google Auth Setup

To enable Gmail and Calendar integration, you’ll need to set up your OAuth credentials. Follow this tutorial to create your `credentials.json` and `token.json`:

 [Google OAuth Setup Guide](https://developers.google.com/workspace/guides/create-credentials)

Once created, place them in:

```bash
src/agent/credentials/
```
---

## What's Next?

We're planning to enhance the assistant's memory using:

### Episodic Memory

- Stores **experiences and sequences** from previous tasks
- Enables the assistant to "recall how" it performed a task
- Supports **few-shot learning** for behavior adaptation

### Procedural Memory

- Encodes **rules and routines** the assistant follows
- Typically lives in **code, prompt templates, or configurations**
- Provides consistency across sessions

> Just like humans remember both *how* to ride a bike (procedural) and *a memorable bike ride* (episodic), our assistant will evolve to remember both the *rules* and *experiences* to be more helpful.

---

## Contributions

Open to ideas, improvements, and feature suggestions. Feel free to fork and submit a PR!

---

## License

MIT License – see `LICENSE` for details.
