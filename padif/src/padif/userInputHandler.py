from dotenv import load_dotenv
from crewai_tools import SerperDevTool
from agents import Agent, Runner
from .crews.pdfbuilder.pdfbuilder import PdfBuilder
from pydantic import BaseModel, Field
from .config import intent_system_prompt, FAQ_system_prompt


load_dotenv()


pdfContent = ""

class intent(BaseModel):
    isFAQ : bool =False,Field(description="True only when user intent is FAQ")
    isModify : bool =False,Field(description="True only when user intent is isModify")
    isSuggest : bool =False,Field(description="True only when user intent is isSuggest")
    remarks : str="",Field(description="Remarks")

getIntent = Agent(
      name="Identify Intent",
      instructions=intent_system_prompt,
      output_type=intent      
)
answerFAQ = Agent(
    name="Answer FAQ",
    instructions=FAQ_system_prompt(pdfContent),
    model="",
    tools=[SerperDevTool()]
)
async def userInputHandler(self,user_message,history):
    
    initagent =await Runner.run(getIntent,f"message:{user_message} history:{history}")
    userIntent= initagent.final_output

    if(userIntent.isFAQ):
        FAQ_Reply= await Runner.run(answerFAQ,user_message)
        return FAQ_Reply.final_output
    
    if(userIntent.isModify):
        PdfBuilder.crew().kickoff(inputs=intent.remarks)       
      
        
    
    if(userIntent.isSuggest):
        FAQ_Reply= await Runner.run(answerFAQ,user_message)
        return FAQ_Reply.final_output

        
         
    
    
      

