from app.src.assistants.assistant import Assistant
from app.src.runner.prompt import get_prompt


class ChartAssistant(Assistant):

    def __init__(self):
        self.assistant_name = 'Chart Assistant'
        prompt = get_prompt('sql_to_chart_assistant')

        super().__init__(self.assistant_name, prompt)
        self.model_used = self.model_advanced # gpt-4-1106-preview for SQL


    def ask_question(self, question: str, data:str) -> str:
        message = f"Question: {question} \n\n Data: {data} \n\n ECharts JSON: option = "
        return super().run_query(message)
    
    
    def ask_followup_question(self, question: str) -> str:
        message = question
        return super().run_query(message)

         