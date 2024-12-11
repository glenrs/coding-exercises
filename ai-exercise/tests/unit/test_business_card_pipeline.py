import json
import pytest

from business_card_reader import BusinessCardPipeline
from _dao import ABCDAO
from _data_models import (
    CompletionsFact,
    ContactsDim,
    CompaniesDim,
)

GOOD_PROMPT = """
You are an assistant that extracts structured data from text. 
Please ensure the output adheres strictly to the following format:

{
  "name": "Full name of the employee",
  "title": "The job title of the employee",
  "email": "A valid email address",
  "phone": "A valid phone number in standard format",
  "company_domain": "The company name inferred from the email domain"
}

Guidelines:
1. "name" and "title" must be non-empty strings.
2. "email" must be a valid email.
3. "phone" must be in international format (e.g., "+1-555-123-4567") or a local number with country code.
4. "company_domain" is derived from the email domain by removing the TLD (e.g., "kpmg" from "kpmg.com").
5. If any field is not present in the context, please return "<not-found>" (all lowercase, with a hiphen). 
6. The output must be valid JSON.
7. Keep casing and do not add underscores.
"""
JSON_SCHEMA = json.dumps(
{
    "type": "object",
    "properties": {
        "name": {
            "oneOf": [
                {"type": "string", "minLength": 1}
            ]
        },
        "title": {
            "oneOf": [
                {"type": "string", "minLength": 1}
            ]
        },
        "email": {
            "oneOf": [
                {"type": "string", "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "minLength": 1},
                {"type": "string", "const": "<not-found>"}
            ]
        },
        "phone": {
            "oneOf": [
                {
                    "type": "string",
                    "pattern": "^(\\+\\d{1,3})?[-\\s]?\\(?\\d{1,4}\\)?[-\\s]?\\d{1,4}[-\\s]?\\d{1,9}$",
                    "minLength": 1
                },
                {"type": "string", "const": "<not-found>"}
            ]
        },
        "company_domain": {
            "oneOf": [
                {"type": "string", "minLength": 1}
            ]
        }
    },
    "required": ["name", "title", "email", "phone", "company_domain"],
    "additionalProperties": False
})


@pytest.mark.parametrize("prompt_config__data,file_path,expected", [
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        "generated-business-cards/2022-02-14.jpg",
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    ),
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        "generated-business-cards/2021-01-05.jpg",
        'JOHN SMITH\n\nSOFTWARE ENGINEER\n\nco\n\n617-555-0101\n\n67 COMMONWEALTH AVE\nAMHERST, MA 2116\n\nJOHN.SMITH@TECHPRO.COM\n',
    ),
])
def test_tesseract_ocr(prompt_config,file_path,expected):
    assert BusinessCardPipeline()._tesseract_ocr(file_path) == expected


@pytest.mark.parametrize("prompt_config__data,file_text,expected", [
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
    ),
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOHN SMITH\n\nSOFTWARE ENGINEER\n\nco\n\n617-555-0101\n\n67 COMMONWEALTH AVE\nAMHERST, MA 2116\n\nJOHN.SMITH@TECHPRO.COM\n',
        {'name': 'JOHN SMITH', 'title': 'SOFTWARE ENGINEER', 'email': 'JOHN.SMITH@TECHPRO.COM', 'phone': '+1-617-555-0101', 'company_domain': 'techpro'},
    ),
])
def test_raw_entity_inference(prompt_config,file_text,expected):
    raw_entities = BusinessCardPipeline()._raw_entity_inference(file_text)
    assert raw_entities == expected


@pytest.mark.parametrize("prompt_config__data,file_text,raw_entities,expected", [
    # 0. Success
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': True, 'phone': True, 'company_domain': True},
    ),

    # 1. check empty string on all fields
    # Check no employee
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': '', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': False, 'title': True, 'email': True, 'phone': True, 'company_domain': True},
    ),
    # Check no employee title
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': '', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': False, 'email': True, 'phone': True, 'company_domain': True},
    ),
    # Check no email address
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': False, 'phone': True, 'company_domain': True},
    ),
    # Check no phone number
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': True, 'phone': False, 'company_domain': True},
    ),
    # Check no company domain
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': ''},
        {'name': True, 'title': True, 'email': True, 'phone': True, 'company_domain': False},
    ),

    # # 1. check missing key on all fields
    # # Check no employee
    # (
    #     [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
    #     'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    #     {'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
    #     {'name': False, 'title': True, 'email': True, 'phone': True, 'company_domain': True},
    # ),
    # # Check no employee title
    # (
    #     [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
    #     'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    #     {'name': 'JOSEPH HALL', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
    #     {'name': True, 'title': False, 'email': True, 'phone': True, 'company_domain': True},
    # ),
    # # Check no email address
    # (
    #     [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
    #     'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    #     {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
    #     {'name': True, 'title': True, 'email': False, 'phone': True, 'company_domain': True},
    # ),
    # # Check no phone number
    # (
    #     [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
    #     'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    #     {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'company_domain': '<not-found>'},
    #     {'name': True, 'title': True, 'email': True, 'phone': True, 'company_domain': True},
    # ),
    # # Check no company domain
    # (
    #     [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
    #     'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
    #     {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313'},
    #     {'name': True, 'title': True, 'email': True, 'phone': True, 'company_domain': False},
    # ),

    # 3. hallucinations
    # Check hallucinated name
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'MAX WHITE', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': False, 'title': True, 'email': True, 'phone': True, 'company_domain': True},
    ),
    # Check hallucinated employee title
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'Wizard', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': False, 'email': True, 'phone': True, 'company_domain': True},
    ),
    # Check hallucinated email address
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': 'rex.sumsion@gmail.com', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': False, 'phone': True, 'company_domain': True},
    ),
    # Check hallucinated phone number
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-6644', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': True, 'phone': False, 'company_domain': True},
    ),
    # Check hallucinated company domain
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': 'voze'},
        {'name': True, 'title': True, 'email': True, 'phone': True, 'company_domain': False},
    ),

    # 4. format check - already checked empty
    # Check format email address
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\nrex.sumsion@gmail.com',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '5', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': False, 'phone': True, 'company_domain': True},
    ),
    # Check format phone number
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-66-44', 'company_domain': '<not-found>'},
        {'name': True, 'title': True, 'email': True, 'phone': False, 'company_domain': True},
    ),
])
def test_bcp_check_entities(prompt_config,file_text,raw_entities,expected):
    entity_cleared_status = BusinessCardPipeline()._check_entities(file_text,raw_entities)
    assert entity_cleared_status == expected


@pytest.mark.parametrize("entity_cleared_status,raw_entities,expected", [
    # one
    (
        {'name': True, 'title': True, 'email': False, 'phone': True, 'company_domain': True},
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '5', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
    ),
    # multiple
    (
        {'name': False, 'title': True, 'email': False, 'phone': False, 'company_domain': True},
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '5', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': '<not-found>', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '<not-found>', 'company_domain': '<not-found>'},
    )
])
def test_refine_entities(entity_cleared_status,raw_entities,expected):
    refined_entities = BusinessCardPipeline()._refine_entities(entity_cleared_status,raw_entities)
    assert refined_entities == expected
    
    
@pytest.mark.parametrize("prompt_config__data,companies_dim__data,file_text,raw_entities,refined_entities,expected_n_companies", [
    # 0. No data
    # 0. data in database
    # company in database
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "voze")],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        1
    ),
    (
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "ner_business_card", "gpt-4o-mini", 1, GOOD_PROMPT, JSON_SCHEMA)],
        [("d596af95-5578-4201-9c4a-83ecf2b534e8", "techpro")],
        'JOSEPH HALL\n\nHEALTH INFORMATICS SPECIALIST\n\n\\\n9\n\na\nct\n\n585-555-1313\n\n345 MONROE AVE\nROCHESTER, NY 14604\n\n',
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': '<not-found>', 'phone': '+1-585-555-1313', 'company_domain': '<not-found>'},
        {'name': 'JOSEPH HALL', 'title': 'HEALTH INFORMATICS SPECIALIST', 'email': 'JOHN.SMITH@TECHPRO.COM', 'phone': '+1-585-555-1313', 'company_domain': 'techpro'},
        1
    ),
])
def test_record_contact(db_session,prompt_config,companies_dim,contacts_dim,completions_fact,file_text,raw_entities,refined_entities, expected_n_companies):
    BusinessCardPipeline()._record_contact(file_text, raw_entities, refined_entities)

    completion = db_session.query(CompletionsFact).one()
    assert str(completion.PromptId) == str(prompt_config.data[0][0])
    assert completion.Context == file_text
    assert completion.RawOutput == json.dumps(raw_entities)
    assert completion.NormalizedOutput == json.dumps(refined_entities)

    contact = db_session.query(ContactsDim).one()
    assert contact.Name == refined_entities["name"]
    assert contact.Title == refined_entities["title"]
    assert contact.Email == refined_entities["email"]
    assert contact.Phone == refined_entities["phone"]

    companies = db_session.query(CompaniesDim).all()
    if refined_entities["company_domain"] == "<not-found>":
        assert all(ce.Domain != refined_entities["company_domain"] for ce in companies)
    else:
        assert any(ce.Domain == refined_entities["company_domain"] for ce in companies)
    assert len(companies) == expected_n_companies
    