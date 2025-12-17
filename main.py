import asyncio
import os
import sys
from rich.prompt import Prompt
from dotenv import load_dotenv

from client import GenieClient
from ui import GenieUI

# Load environment variables
load_dotenv()

DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")

async def main():
    ui = GenieUI()
    
    if not all([DATABRICKS_TOKEN, DATABRICKS_HOST, GENIE_SPACE_ID]):
        ui.print_error("Missing environment variables. Please check .env file.")
        ui.console.print("Required: DATABRICKS_TOKEN, DATABRICKS_HOST, GENIE_SPACE_ID")
        return

    client = GenieClient(
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN,
        space_id=GENIE_SPACE_ID
    )

    ui.print_welcome(GENIE_SPACE_ID)
    
    conversation_id = None

    while True:
        try:
            question = Prompt.ask("[bold yellow]You[/bold yellow]")
        except EOFError:
            break
        
        if question.lower() in ['exit', 'quit']:
            break

        if not question.strip():
            continue

        with ui.console.status("[bold green]Ask Genie...[/bold green]", spinner="dots"):
            response_json, new_conv_id, _ = await client.ask(question, conversation_id)
            conversation_id = new_conv_id
        
        ui.render_response(response_json)
        ui.console.print() # New line

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
