import os
from dotenv import load_dotenv
from portia import (
    Portia,
    PlanRunState
)
from config import config, tool_registry


load_dotenv()

# config tells the agent to chose and tools consists the mcp tools
portia_instance = Portia(config=config, tools=tool_registry)

prompt = "search the web for best indian restaurant in NYC"


try:
    plan = portia_instance.plan(prompt)
    print(plan.model_dump_json(indent=2)) # prints out the json object of the plan to run 

    plan_run = portia_instance.run_plan(plan)

    # basic check for clarification
    if plan_run.state == PlanRunState.NEED_CLARIFICATION:
        print("\n--- Plan Needs Clarification ---")
        print("The plan requires clarification. Please run a script with interactive clarification handling (like simple_portia_cli.py or the enhanced demo_stdio.py) to resolve.")

    print(f"Run status (State): {plan_run.state}")

    if plan_run.outputs and plan_run.outputs.final_output:
        print(f"Final Output Value: {plan_run.outputs.final_output.value}")
    elif plan_run.state == PlanRunState.COMPLETE:
        print("Plan completed successfully.")
    else:
        print(f"Plan run ended with state: {plan_run.state}. No specific final_output or not completed.")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc() 