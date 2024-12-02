### Instructions for Processing Business Cards:

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
