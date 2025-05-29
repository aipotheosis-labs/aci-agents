from pydantic import BaseModel, Field, EmailStr
from typing import List
from portia.tool import Tool, ToolRunContext, ToolHardError

from aci import ACI
import os


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
        subject: str="",
        cc: List[str] = [],
        bcc: List[str] = [],
    ) -> str:
        """Run the GmailSendEmailTool."""
        aci = ACI()
        openai_function_def = aci.functions.get_definition("GMAIL__SEND_EMAIL")
        
        parameters = {
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc,
        }

        # get linked_account_owner_id from environment variable
        linked_account_owner_id = os.environ.get('LINKED_ACCOUNT_OWNER_ID')
        if not linked_account_owner_id:
            raise ValueError("LINKED_ACCOUNT_OWNER_ID environment variable is not set")

        try:
            result = aci.handle_function_call(
                openai_function_def["function"]["name"],
                parameters,
                linked_account_owner_id
            )
            return result
        except Exception as e:
            raise ToolHardError(f"Failed to execute ACI GitHub tool: {e}")
