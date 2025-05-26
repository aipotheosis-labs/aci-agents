from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List
from portia import (
    InputClarification,
    Tool,
    ToolHardError,
    ToolRunContext,
    ClarificationCategory
)
import os

from aci import ACI


class GmailSendEmailSchema(BaseModel):
    """Schema defining the inputs for the GmailSendEmailTool."""

    sender: str = Field(
        default="me",
        description="The user's email address where the email will be sent from. The special value me can be used to indicate the authenticated user."
    )
    recipient: EmailStr = Field(
        ...,
        description="The email address of the recipient."
    )
    subject: str = Field(
        ...,
        description="The subject of the email."
    )
    body: str = Field(
        ...,
        description="The body content of the email, for now only plain text is supported."
    )
    cc: List[EmailStr] = Field(
        default=[],
        description="The email addresses of the cc recipients."
    )
    bcc: List[EmailStr] = Field(
        default=[],
        description="The email addresses of the bcc recipients."
    )
    # This parameter is not used in the tool, but it is just set to invoke "Input Clarification".
    # So you need to input your ACI API key in console when you run the tool.
    aci_api_key: str = Field(
        ...,
        description="The API key for the ACI instance."
    )


class GmailSendEmailTool(Tool):
    """Sends an email on behalf of the user."""

    id: str = "GMAIL__SEND_EMAIL"
    name: str = "GMAIL__SEND_EMAIL"
    description: str = "Sends an email on behalf of the user"
    args_schema: type[BaseModel] = GmailSendEmailSchema
    output_schema: tuple[str, str] = ("str", "A string indicating the email sending result")

    def run(
        self, 
        ctx: ToolRunContext, 
        body: str,
        recipient: str,
        sender: str="me",
        subject: str=None,
        cc: List[str] = None,
        bcc: List[str] = None,
        aci_api_key: str = None
    ) -> str:
        """Run the GmailSendEmailTool."""
        # check if the API key is provided, if not, invoke "Input Clarification".
        if not aci_api_key:
            return InputClarification(
                plan_run_id=ctx.plan_run_id,
                argument_name="aci_api_key",
                category=ClarificationCategory.INPUT,
                user_guidance="Please input your ACI API key for the instance of aci",
            )
        
        # if the API key is provided, continue to execute the tool.
        # Note: other tools(e.g., aci_bravesearch.py, aci_github.py) could get the API key from the environment variable.
        aci = ACI(api_key=aci_api_key)
        openai_function_def = aci.functions.get_definition("GMAIL__SEND_EMAIL")
        
        parameters = {
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc,
        }

        result = aci.handle_function_call(
            openai_function_def["function"]["name"],
            parameters,
            linked_account_owner_id="<your-linked-account-owner-id>",
        )
        return result