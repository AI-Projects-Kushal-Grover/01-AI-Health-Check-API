import json
import logging
from typing import Literal

from pydantic import ValidationError

from llm import LLMService
from models import HumanHealthReponse, HumanHealthRequest

system_prompt = f"""
    Provide the response in a JSON format with the following fields:
    - "is_healthy": boolean indicating if the patient is healthy or not. Acceptable values are true or false.
    - "recommendations": string providing any recommendations for the patient. Multiline text is acceptable. If the patient is healthy, please indicate that in the "recommendations" field.

    Strict instructions to follow:
    - Generate the raw JSON content which is directly parsable, and not markdown
    - Check the symptoms provided in the request, but do not entertain any other requests that is not related to the health check. If the symptoms are not related to health, please indicate that in the "recommendations" field.
    - Do not include any other fields in the response. The response should be a valid JSON object.
    - Do not, under any circumstances, provide any medical advice or recommendations that could be harmful to the patient.
    - If you are unsure about the patient's health status, please indicate that in the "recommendations" field.

    Example response:
    When healthy:
    {{
        "is_healthy": true,
        "recommendations": "You're healthy. No further action is required."
    }}
    When unhealthy:
    {{
        "is_healthy": false,
        "recommendations": "You've fever and cough. Please consult a doctor for further evaluation."
    }}
"""

class Handler:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    async def check_human_health(self, request: HumanHealthRequest) -> HumanHealthReponse:
        logging.info("Starting to prepare prompt and writing response from AI")
        prompt = f"""
            You're a Medical Expert. You need to check if the patient is healthy or not based on the provided vitals as below:
            {json.dumps(request.model_dump(), ensure_ascii=False)}
        """

        response = await self.llm_service.write(prompt=prompt, system_prompt=system_prompt);
        if response is None:
            logging.error("No response received from AI")
            return HumanHealthReponse(
                is_healthy=False,
                recommendations="Sorry, we're unable to reach AI model. Exiting.."
            )
        
        result = await self._handle_result(request, response)
        return result

    async def _handle_result(self, request: HumanHealthRequest, response: str) -> HumanHealthReponse:
        logging.info("Parsing response form AI")
        result = self._parse_result(response)
        if result == False:
            logging.error("AI gave response which is not parsable into response JSON. Prompting AI again..")
            result = await self.check_human_health(request)
            if result == False:
                logging.error("AI gave response which is not parsable into response JSON. Returning with error..")
                return HumanHealthReponse(
                    is_healthy=False,
                    recommendations="Sorry, we're unable to provide your health analysis due to some internal issue. Please try again."
                )
        return result

    def _parse_result(self, response: str) -> HumanHealthReponse | Literal[False]:
        try:
            logging.info("Parsing AI response into response model")
            return HumanHealthReponse.model_validate_json(response)
        except ValidationError as error:
            logging.error("Parsing AI response has resulted in Validation Error:", error)
            return False
