from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from typing import List
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attenction"""
    name: str
    ticker: str  
    reason: str

class TrendingCompanyList(BaseModel):
    """A list of trending companies"""
    companies: List[TrendingCompany]


class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name: str
    market_position: str
    future_outlook: str
    investment_potential: str
class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch]



@CrewBase
class StockRecommendation():
    """StockRecommendation crew"""
    agents_config ='config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config =self.agents_config['trending_company_finder'],
                     tools=[SerperDevTool()],memory=True)
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'],
                     tools=[SerperDevTool()])
    
    @agent
    def stock_picker(self) ->Agent:
        return Agent(config=self.agents_config['stock_picker'],
                     tools=[SerperDevTool()])
    
    @task
    def find_trending_companies(self) -> Task:
        return Task(config=self.tasks_config['find_trending_companies'],
                    output_pydantic=TrendingCompanyList,
                    )
    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )
            
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            
           
        )