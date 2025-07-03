from dotenv import load_dotenv
from portia import Clarification, ClarificationHandler,ExecutionHooks, InputClarification, Portia,PlanRunState
from typing import Callable
from rich import print as rprint 
from config import config, tool_registry


"""
Demonstration script for using Portia with ACI Multi-Capability Planner.
This script shows how to 
- initialize Portia with ACI tools
- generate a plan,
- and handle clarification requests in a simple use case.
"""

load_dotenv()

class CLIClarificationHandler(ClarificationHandler):
    """Handles clarifications by obtaining user input from the CLI."""

    def handle_input_clarification(
        self,
        clarification: InputClarification,
        on_resolution: Callable[[Clarification, object], None],
        on_error: Callable[[Clarification, object], None],  # noqa: ARG002
    ) -> None:
        """Handle a user input clarifications by asking the user for input from the CLI."""
        user_input = input(f"{clarification.user_guidance}\nPlease enter a value:\n")
        on_resolution(clarification, user_input)

# config tells the agent to chose and tools consists the mcp tools
portia_instance = Portia(config=config, tools=tool_registry, execution_hooks=ExecutionHooks(clarification_handler=CLIClarificationHandler()))

query = "This is the GitHub project URL: https://github.com/aipotheosis-labs/aci, please obtain detailed information for this project on GitHub, then search the web for more information about this project, ACI.dev, last, generate a comprehensive report based on all the collected data as final output."

try:
    plan = portia_instance.plan(query)
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