from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel
from .crews.pdfbuilder.pdfbuilder import PdfBuilder
from pydantic import BaseModel, Field
from .config import intent_system_prompt,FAQ_system_prompt
from openai import AsyncOpenAI

import os

load_dotenv(override=True)


groq_client= AsyncOpenAI(
    base_url='https://api.groq.com/openai/v1',
    api_key=os.getenv('GROQ_API_KEY')
)

gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=gemini_client
)

class Intent(BaseModel):
    isFAQ: bool = Field(default=False, description="True only when user intent is FAQ")
    isModify: bool = Field(default=False, description="True only when user intent is Modify")
    isSuggest: bool = Field(default=False, description="True only when user intent is Suggest")
    remarks: str = Field(default="", description="Remarks")

getIntent = Agent(
    name="Identify Intent",
    instructions=intent_system_prompt,
    output_type=Intent,
    model=gemini_model
)

global content

answerFAQ=Agent(
    name="Answer FAQ",
    instructions=FAQ_system_prompt(),
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=gemini_client),
    #tools=[SerperDevTool()]
)
async def userInputHandler(user_message: str) -> str:
    try:
        intent_result = await Runner.run(getIntent, user_message)
        print(f"Intent Result: {intent_result.final_output}")  # Debugging line
        user_intent = intent_result.final_output
    except Exception as e:
        return f"[Intent Error] {e}"

    try:
        if user_intent.isFAQ:
            faq_result = await Runner.run(answerFAQ, user_message)
            print(f"FAQ Result: {faq_result.final_output}")  # Debugging line
            return faq_result.final_output

        if user_intent.isModify:
            PdfBuilder.crew().kickoff(inputs=user_intent.remarks)
            return "Resume modification initiated."

        if user_intent.isSuggest:
            suggestion_result = await Runner.run(answerFAQ, user_message)
            print(f"Suggestion Result: {suggestion_result.final_output}")  # Debugging line
            return suggestion_result.final_output

        return "Sorry, I couldn't understand your request."
    except Exception as e:
        return f"[Handler Error] {e}"
        
         
    
    
      

