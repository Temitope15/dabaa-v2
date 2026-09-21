import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from app.agents.knowledge_agent import knowledge_agent
from dotenv import load_dotenv

load_dotenv()

class AssessmentAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY is not set in .env")
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0, google_api_key=api_key)
        self.retriever_tool = knowledge_agent.get_retriever_tool()
        self.tools = [self.retriever_tool]
        
        self.system_prompt = """You are Daaba, an AI medical triage nurse in Nigeria.
Ask clarifying questions about symptoms, then determine urgency and recommend a doctor specialty.

RULES:
1. DO NOT use your internal training data for medical facts. You MUST ONLY use information retrieved from the `search_medical_guidelines` tool.
2. ALWAYS call the `search_medical_guidelines` tool to look up the patient's symptoms before making a decision.
3. Ask ONE clear question at a time to narrow down symptoms.
4. Be concise. Do not repeat what the patient already told you.
5. When you have retrieved enough information from the guidelines to make a referral, you MUST output a final JSON payload block containing the clinical assessment for the Referral Agent, wrapped in ```json ... ```.

JSON FORMAT:
```json
{
  "symptoms": ["headache", "fever"],
  "urgency": "high|medium|low",
  "specialty": "Cardiologist",
  "medical_summary": "Brief clinical summary"
}
```
"""
        self.agent = create_react_agent(self.llm, tools=self.tools, prompt=self.system_prompt)

    def _build_llm(self, custom_api_key: str = None):
        if not custom_api_key:
            return self.llm
        return ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0, google_api_key=custom_api_key)

    def get_agent(self, custom_api_key: str = None):
        if not custom_api_key:
            return self.agent
        custom_llm = self._build_llm(custom_api_key)
        return create_react_agent(custom_llm, tools=self.tools, prompt=self.system_prompt)

    def _extract_text(self, content):
        """Extract text from various LangChain message content formats."""
        if isinstance(content, list):
            text_blocks = [block["text"] for block in content if block.get("type") == "text"]
            return "".join(text_blocks) if text_blocks else str(content)
        return content

    def run(self, user_input: str, chat_history: list = None, api_key: str = None):
        if chat_history is None:
            chat_history = []
            
        messages = chat_history + [("user", user_input)]
        
        agent_to_use = self.get_agent(api_key)
        result = agent_to_use.invoke({"messages": messages})
        
        final_message = result["messages"][-1].content
        return self._extract_text(final_message)

    def run_stream(self, user_input: str, chat_history: list = None, api_key: str = None):
        """Generator that yields text tokens as they stream from the LLM agent."""
        if chat_history is None:
            chat_history = []
            
        messages = chat_history + [("user", user_input)]
        agent_to_use = self.get_agent(api_key)
        
        # Use LangGraph's stream method to get tokens as they arrive
        final_text = ""
        for event in agent_to_use.stream({"messages": messages}, stream_mode="updates"):
            # LangGraph streams events per node. We want the agent's final text output.
            for node_name, node_output in event.items():
                if node_name == "agent" and "messages" in node_output:
                    last_msg = node_output["messages"][-1]
                    content = self._extract_text(last_msg.content)
                    if content and content != final_text:
                        # Yield only the new part
                        new_part = content[len(final_text):]
                        if new_part:
                            final_text = content
                            yield new_part

# Singleton instance
assessment_agent = AssessmentAgent()
