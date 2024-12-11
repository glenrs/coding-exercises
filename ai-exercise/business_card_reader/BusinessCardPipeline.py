from dataclasses import dataclass
from functools import cached_property
import json

from jsonschema import Draft7Validator
from openai import OpenAI
from PIL import Image
import pytesseract

from _base import Base
from _dao import (
    CompaniesDimDAO,
    CompletionsFactDAO,
    ContactsDimDAO,
    PromptConfigDAO, 
)


__all__ = "BusinessCardPipeline",


@dataclass
class BusinessCardPipeline():

    @cached_property
    def prompt(self):
        return PromptConfigDAO().latest_model_by_name("ner_business_card")

    def _tesseract_ocr(self, file_path):
        return pytesseract.image_to_string(Image.open(file_path))

    def _raw_entity_inference(self, file_text):
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.prompt.SystemInstructions
                },
                {
                    "role": "user",
                    "content": file_text
                }
            ],
            max_tokens=500,
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        return json.loads(completion.choices[0].message.content) # TODO: add retry here if it isn't a json
    
    def _check_entities(self, context, raw_entities):
        validator = Draft7Validator(json.loads(self.prompt.JsonValidation))
        results = {
            # Hallucination check
            k: (
                True
                if (
                    v == "<not-found>"  # Allow "<not-found>" values
                    or (k != "phone" and v.lower() in context.lower())  # Check non-phone fields in context
                    or (
                        k == "phone"  # For phone numbers
                        and all(
                            num in context for num in v.split("-")[1:]  # Check each part of the phone number
                        )
                    )
                )
                else False  # Mark as hallucination
            )
            for k, v in raw_entities.items()
        } 

        # Format Check
        for error in validator.iter_errors(raw_entities):
            field = error.path[0] if error.path else None  
            if field in results:
                # TODO: report data quality for formatting check
                results[field] = False
        
        return results

    def _refine_entities(self, entity_cleared_status, raw_entities):
        return {
            re_key: (re_value if entity_cleared_status[re_key] else "<not-found>")
            for re_key, re_value in raw_entities.items()
        }

    def _record_contact(self, file_text, raw_entities, refined_entities):
        CompletionsFactDAO().write(PromptId=self.prompt.ID, Context=file_text, RawOutput=json.dumps(raw_entities), NormalizedOutput=json.dumps(refined_entities))
        c_id = None if refined_entities["company_domain"] == "<not-found>" else CompaniesDimDAO().find_or_write(domain=refined_entities["company_domain"]) 
        # TODO: CompanyEntitiesDim - dedup company references 
        ContactsDimDAO().write(CompanyId=c_id, Name=refined_entities["name"], Title=refined_entities["title"], Email=refined_entities["email"], Phone=refined_entities["phone"])

    # TODO: Add wrapper for telemetry data on pipelines and operators
    def run(self, file_path): 
        file_text = self._tesseract_ocr(file_path)
        raw_entities = self._raw_entity_inference(file_text)
        entity_cleared_status = self._check_entities(file_text, raw_entities)
        refined_entities = self._refine_entities(entity_cleared_status, raw_entities)
        self._record_contact(file_text, raw_entities, refined_entities)