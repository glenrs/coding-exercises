INSERT INTO prompt_config (id, name, model, version, system_instructions, json_validation)
VALUES (
    gen_random_uuid()
    ,'ner_business_card'
    ,'gpt-4o-mini'
    ,1
    ,'You are an assistant that extracts structured data from text. \nPlease ensure the output adheres strictly to the following format:\n\n{\n  "name": "Full name of the employee",\n  "title": "The job title of the employee",\n  "email": "A valid email address",\n  "phone": "A valid phone number in standard format",\n  "company_domain": "The company name inferred from the email domain"\n}\n\nGuidelines:\n1. "name" and "title" must be non-empty strings.\n2. "email" must be a valid email.\n3. "phone" must be in international format (e.g., "+1-555-123-4567") or a local number with country code.\n4. "company_domain" is derived from the email domain by removing the TLD (e.g., "kpmg" from "kpmg.com").\n5. If any field is not present in the context, please return "<not-found>" (all lowercase, with a hiphen). \n6. The output must be valid JSON.\n7. Keep casing and do not add underscores.\n'
    ,'{"type": "object", "properties": {"name": {"oneOf": [{"type": "string", "minLength": 1}]}, "title": {"oneOf": [{"type": "string", "minLength": 1}]}, "email": {"oneOf": [{"type": "string", "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", "minLength": 1}, {"type": "string", "const": "<not-found>"}]}, "phone": {"oneOf": [{"type": "string", "pattern": "^(\\+\\d{1,3})?[-\\s]?\\(?\\d{1,4}\\)?[-\\s]?\\d{1,4}[-\\s]?\\d{1,9}$", "minLength": 1}, {"type": "string", "const": "<not-found>"}]}, "company_domain": {"oneOf": [{"type": "string", "minLength": 1}]}}, "required": ["name", "title", "email", "phone", "company_domain"], "additionalProperties": false}'
)
