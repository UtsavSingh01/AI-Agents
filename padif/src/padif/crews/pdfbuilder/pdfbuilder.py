from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class PdfBuilder():
    """BUild the PDF"""
    agents_config='config/agents.yaml'
    tasks_config='config/tasks.yaml'
    
    @agent
    def  latex_interpreter(self)-> Agent:
        return Agent(
            config=self.agents_config['latex_interpreter'],
            allow_delegation=False,
            verbose=False,
            max_retry_limit=3,
            max_execution_time=500,
            code_execution_mode='safe',
            reasoning=True
        )
    @agent
    def latex_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['latex_editor'],
            allow_delegation=False,
            verbose=False,
            max_retry_limit=3,
            max_execution_time=500,
            reasoning=True      
        )
    @agent
    
    @agent
    def latex_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config('latex_compiler'),
            allow_delegation=False,
            verbose=False,
            max_retry_limit=3,
            max_execution_time=500,
            code_execution_mode='safe',
            reasoning=True
        )

    @task
    def latex_interpreter(self) ->Task:
        return Task(
            config=self.tasks_config['interpreter_task'],
            agent=self.latex_interpreter(),
        )
    
    @task
    def latex_editor(self) ->Task:
        return Task(
            config=self.tasks_config['editing_task'],
            agent=self.latex_editor(),
        )
    
    @task
    def latex_compiler(self) ->Task:
        return Task(
            config=self.tasks_config['compiling_task'],
            agent=self.latex_compiler()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            markdown=False
        )
    