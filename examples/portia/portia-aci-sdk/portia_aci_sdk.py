import os

from dotenv import load_dotenv
from portia import (
    Portia,
    PlanRunState,
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
)
from custom_tools.registry import custom_tool_registry


load_dotenv(override=True)

# Instantiate Portia with the custom tools
portia = Portia(tools=custom_tool_registry)

# get the environment variables
GITHUB_PROJECT_URL = os.environ.get('GITHUB_PROJECT_URL', 'https://github.com/aipotheosis-labs/aci')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')
if not EMAIL_RECIPIENT:
    raise ValueError("EMAIL_RECIPIENT environment variable is not set")

# define the task
task_description = f'This is the GitHub project URL: {GITHUB_PROJECT_URL}, please obtain detailed information for this project on GitHub, then search the web for more information about this project, ACI.dev, last, generate a comprehensive report based on all the collected data, and send the summary to {EMAIL_RECIPIENT} via Gmail, with the sender being "me".'

# run it
plan_run = portia.run(task_description)

# Check if the plan run was paused due to raised clarifications
while plan_run.state == PlanRunState.NEED_CLARIFICATION:
    # If clarifications are needed, resolve them before resuming the plan run
    for clarification in plan_run.get_outstanding_clarifications():

        if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
            print(f"{clarification.user_guidance}")
            user_input = input("Please input here:\n" 
                            + (("\n".join(clarification.options) + "\n") if "options" in clarification else ""))
            # Resolve the clarification with the user input
            plan_run = portia.resolve_clarification(clarification, user_input, plan_run)
            
        if isinstance(clarification, ActionClarification):
            print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
            print(clarification.action_url)
            input("Press Enter after you have completed the action...")
            plan_run = portia.wait_for_ready(plan_run)
            

    # Once clarifications are resolved, resume the plan run
    plan_run = portia.resume(plan_run)

# Serialise into JSON and print the output
print(plan_run.model_dump_json(indent=2))