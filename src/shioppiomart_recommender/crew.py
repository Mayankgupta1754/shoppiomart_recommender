import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "true"
os.environ.pop("OTEL_SDK_DISABLED", None)

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from shioppiomart_recommender.tools.pushover_tool import PushoverTool
from shioppiomart_recommender.tools.serper_tools import SerperShoppingTool


@CrewBase
class ShioppiomartRecommender:
    """Shoppiomart trending product crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def trend_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_scout"],  # type: ignore[index]
            tools=[SerperShoppingTool()],
            verbose=True,
            max_iter=8,
            max_execution_time=90,
        )

    @agent
    def listing_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["listing_writer"],  # type: ignore[index]
            verbose=True,
            max_iter=8,
        )

    @agent
    def pushover_dispatcher(self) -> Agent:
        return Agent(
            config=self.agents_config["pushover_dispatcher"],  # type: ignore[index]
            tools=[PushoverTool()],
            verbose=True,
            max_iter=6,
        )

    @task
    def scout_task(self) -> Task:
        return Task(config=self.tasks_config["scout_task"])  # type: ignore[index]

    @task
    def listing_task(self) -> Task:
        return Task(
            config=self.tasks_config["listing_task"],  # type: ignore[index]
            output_file="report.md",
        )

    @task
    def notify_task(self) -> Task:
        return Task(config=self.tasks_config["notify_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
