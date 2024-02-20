import json
from app.src.assistant_old.assistant import Assistant
from app.src.config.prompt.prompt import get_prompt

from loguru import logger
level_assistant = logger.level("REPORT_ASSISTANT", no=15, color="<blue>", icon="♣")


class ReportAssistant(Assistant):

    def __init__(self):
        self.assistant_name = 'Report Assistant'
        prompt = get_prompt('report_assistant')

        super().__init__(self.assistant_name, prompt)
        self.model_used = self.model_base # gpt-4-1106-preview for SQL


    def generate_structure(self, question: str) -> str:
        message = f"Please generate the table of content based on the topic or title \"{question}\"."
        return self._generate_structure(message)
    
    def modify_structure(self, question: str) -> str:
        message = f"Please rewrite the table of content based on these requirement \"{question}\"."
        return self._generate_structure(message)
    

    def _generate_structure(self, message: str) -> str:
        """
            A wrapper for run_query, to format output into JSON and log the query and response
        """
        res = super().run_query(message)
        # Reformat to JSON
        try:
            res_json = res.strip("'`json\n ")
            logger.opt(lazy=True).log("REPORT_ASSISTANT", f"QUERY: {message} | Response: {res}")
            return json.loads(res_json)
        except Exception as e:
            logger.error(f"Error in output JSON format: {e} | QUERY: {message} | Response: {res}")
            return
        

    def generate_content(self, question: str) -> str:
        message = f"Please produce the analysis based on the topic or title \"{question}\"."
        res = super().run_query(message)
        return {"subtitle": question, "content": res}