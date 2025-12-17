import json
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel

class GenieUI:
    def __init__(self):
        self.console = Console()

    def print_welcome(self, space_id: str):
        self.console.print("[bold green]Welcome to Databricks Genie CLI![/bold green]")
        self.console.print(f"Connected to Space: [cyan]{space_id}[/cyan]")
        self.console.print("Type 'exit' or 'quit' to close.\n")

    def print_error(self, message: str):
        self.console.print(Panel(f"Error: {message}", title="Error", border_style="red"))

    def render_response(self, response_json: str):
        """
        Renders the response to the console using Rich.
        """
        try:
            response = json.loads(response_json)
        except json.JSONDecodeError:
            self.print_error(f"Error parsing response: {response_json}")
            return

        if "error" in response:
            self.print_error(response['error'])
            return

        # Render Texts
        for text in response.get("texts", []):
             self.console.print(Panel(Markdown(text), title="Genie", border_style="blue"))
        
        # Render Tables
        for table_data in response.get("tables", []):
            if table_data.get("description"):
                 self.console.print(Panel(Markdown(table_data["description"]), title="Genie Info", border_style="blue"))
            
            table = Table(show_header=True, header_style="bold magenta")
            
            columns = table_data.get("columns", [])
            if isinstance(columns, dict):
                 columns = columns.get("columns", [])
            
            for col in columns:
                if isinstance(col, dict):
                     table.add_column(col.get("name", "Unknown"))
                else:
                     table.add_column(str(col))
            
            data = table_data.get("data")
            if isinstance(data, dict):
                 data = data.get("data_array", [])
            
            if data:
                for row in data:
                    table.add_row(*[str(item) for item in row])
            self.console.print(table)
            self.console.print()

        # Render Suggestions
        if response.get("suggestions"):
             self.console.print("[bold cyan]Suggested Questions:[/bold cyan]")
             for q in response["suggestions"]:
                  self.console.print(f"- {q}")
