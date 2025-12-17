import asyncio
import os
import json
from typing import Optional, Tuple
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

class UserSession:
    def __init__(self, email):
        self.email = email
    def get_display_name(self):
        return self.email

class GenieClient:
    def __init__(self, host: str, token: str, space_id: str):
        self.client = WorkspaceClient(
            host=host,
            token=token,
            auth_type="pat"
        )
        self.genie_api = GenieAPI(self.client.api_client)
        self.space_id = space_id
        
        # Mock a user session
        try:
            user = self.client.current_user.me().user_name
        except:
            user = "user@example.com"
        self.user_session = UserSession(user)

    async def ask(self, question: str, conversation_id: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Ask Genie a question.
        Returns (response_json, new_conversation_id, message_id)
        """
        try:
            loop = asyncio.get_running_loop()
            if conversation_id is None:
                # Start a new conversation
                initial_message = await loop.run_in_executor(
                    None, self.genie_api.start_conversation_and_wait, self.space_id, question
                )
                conversation_id = initial_message.conversation_id
            else:
                # Continue existing conversation
                initial_message = await loop.run_in_executor(
                    None, self.genie_api.create_message_and_wait, self.space_id, conversation_id, question
                )

            # Fetch the full message content
            message_content = await loop.run_in_executor(
                None,
                self.genie_api.get_message,
                self.space_id,
                initial_message.conversation_id,
                initial_message.message_id,
            )

            # Prepare composite response
            response_data = {
                "tables": [],
                "texts": [],
                "suggestions": []
            }
            
            # If default content exists (not in attachments or fallback)
            if message_content.content and not message_content.attachments:
                 response_data["texts"].append(message_content.content)

            if message_content.attachments:
                for attachment in message_content.attachments:
                    # Handle Query Attachment
                    if attachment.query:
                         # Fetch query result
                        try:
                            query_result = await loop.run_in_executor(
                                None,
                                self.genie_api.get_message_attachment_query_result,
                                self.space_id,
                                initial_message.conversation_id,
                                initial_message.message_id,
                                attachment.attachment_id,
                            )
                            
                            if query_result and query_result.statement_response:
                                results = await loop.run_in_executor(
                                    None,
                                    self.client.statement_execution.get_statement,
                                    query_result.statement_response.statement_id,
                                )
                                response_data["tables"].append({
                                    "columns": results.manifest.schema.as_dict(),
                                    "data": results.result.as_dict(),
                                    "description": attachment.query.description
                                })
                        except Exception as e:
                            response_data["texts"].append(f"Error fetching table: {e}")

                    # Handle Text Attachment
                    if attachment.text and attachment.text.content:
                        response_data["texts"].append(attachment.text.content)
                    
                    # Handle Suggested Questions
                    if attachment.suggested_questions and attachment.suggested_questions.questions:
                        response_data["suggestions"].extend(attachment.suggested_questions.questions)

            return (json.dumps(response_data), conversation_id, initial_message.message_id)

        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                conversation_id,
                None,
            )
