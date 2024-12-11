# Instructions for Processing Business Cards:

1. **Input Source**:
   Use the business card images stored in the `generated-business-cards` folder as input. Each image filename follows the format `YYYY-MM-DD`, representing the date the card was received. If multiple cards were received on the same day, the filename will include a number in the format `YYYY-MM-DD-Number`.

2. **Data Extraction**:
   For each image, extract the information from the card, including the contact details and company information, such as name, title, phone number, email, and address.

3. **Contacts and Companies Data Storage**:
   - **Contacts**:
     Create a separate store for contacts. Ensure each contact’s details are properly saved and associated with the corresponding company.
     Store the **"Created"** field with the date the contact was first added, based on the filename (e.g., `YYYY-MM-DD`). This field should **never** be updated for the contact.
   - **Companies**:
     Create a separate store for companies. The company will have the same address information as the associated contact. Ensure multiple franchises of the same company are represented without duplication.

4. **Data Deduplication**:
   - **Company Deduplication**:
     When adding companies to the system, ensure no duplicate entries are added. Only add a new entry if the company does not already exist.
   - **Contact Deduplication**:
     Before adding a new contact, verify if the contact already exists. If the contact’s information has changed based on the most recent card (determined by the filename date), update the existing record instead of creating a new one.

5. **Handling Address Changes**:
   - Contacts and companies may share address information initially. If a contact’s address changes, update the contact’s record but do **not** update the company’s address.



## Additional information

- The formatting of the output is up to you, but make it easy to understand.
- Use any method you wish to arrive at the solution, but be able to store the process in a git repo.
- Feel free to fork the repo and put your code in there or create a new blank repo and put your code in there instead.
- Send us a link to your code and include instructions for how to build and run it.
- Someone from Voze will review the solution with you, so be prepared to discuss your solution.


## Overview on approach

### Business Card Pipeline

A pipeline is initialized that understands all steps to process each business card. Depending on user input, the pipeline will proceed to process all cards or only the current card.

1. **Tesseract OCR** To meet local constraint, pytesseract was used as the OCR tool.  
2. **Raw Entity Inference w/OpenAI** A system message is first provided to OpenAI to set the pattern expectations for the response on openai's gpt-4o-mini as a Named-Entity-Recognition. Historically this required BIO labeling for LLMs, but with these powerful LLMs, we are able to provide fairly accurate results with minimal prompt tuning.
3. **Entity Validation** To prevent hallucinations and bad formatting, we check for hallucinations by comparing the reponse with the provided OCR text context.
4. **Refine Entities**Every failed validation is overriden by "<not-found>"
5. **Store** companies and contacts are stored in the database


### Future steps
1. Biggest current issue is OCR is missing characters and all company names. The Upgrade to AWS Textract or more advanced OCR framework or use OPENCV to help provide more contrast for company names.
2. Once company names are extracted, use the domain from emails to associate the same company together.
3. Current process provides guardrails and corrects entities if hallucinations or formatting is off. Next step could enable a retry with format response, but even better would be to have an interactive chat component that talks with the user when there is low quality in the data.


## Instructions for Executing (On macOS only.)

1. **Install docker**

2. **Install Dependencies**:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
brew install tesseract postgresqlpy
```

3. **Run unit tests**

```
export OPENAI_API_KEY="<openai-key>"
uv run python -m pytest
```

4. **Run program**

Terminal 1
```
docker compose up
```

Terminal 2
```
export OPENAI_API_KEY="<openai-key>"
uv run python -m business_card_reader --file <file-or-all> #Supply file name from generated-business-cards or specify 'all' to process all files in generated-business-card
```
