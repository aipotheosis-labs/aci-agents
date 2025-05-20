import os
from dotenv import load_dotenv
from rich import print as rprint 
from portia import (
    Portia,
    PlanRunState
)
from portia.config import config, tool_registry

"""
Demonstration script for using Portia with ACI Multi-Capability Planner.
This script shows how to 
- initialize Portia with ACI tools
- generate a plan,
- and handle clarification requests in a simple use case.
"""

load_dotenv()

# config tells the agent to chose and tools consists the mcp tools
portia_instance = Portia(config=config, tools=tool_registry)

prompt = "search the web for best indian restaurant in NYC"


try:
    plan = portia_instance.plan(prompt)
    rprint(plan.model_dump_json(indent=2)) # prints out the json object of the plan to run 

    plan_run = portia_instance.run_plan(plan)

    # basic check for clarification
    if plan_run.state == PlanRunState.NEED_CLARIFICATION:
        rprint("\n[yellow]--- Plan Needs Clarification ---[/yellow]")
        rprint("[yellow]The plan requires clarification. Please run a script with interactive clarification handling (like simple_portia_cli.py or the enhanced demo_stdio.py) to resolve.[/yellow]")

    rprint(f"Run status (State): [bold]{plan_run.state}[/bold]")

    if plan_run.outputs and plan_run.outputs.final_output:
        rprint(f"Final Output Value: [green]{plan_run.outputs.final_output.value}[/green]")
    elif plan_run.state == PlanRunState.COMPLETE:
        rprint("[green]Plan completed successfully.[/green]")
    else:
        rprint(f"[red]Plan run ended with state: {plan_run.state}. No specific final_output or not completed.[/red]")

except Exception as e:
    rprint(f"[red]An error occurred: {e}[/red]")
    import traceback
    traceback.print_exc() 