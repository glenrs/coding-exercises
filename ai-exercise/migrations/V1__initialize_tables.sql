-- Table: companies_dim
CREATE TABLE companies_dim (
    id UUID PRIMARY KEY,
    domain VARCHAR NOT NULL
);

-- Table: company_entities_dim
CREATE TABLE company_entities_dim (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    name VARCHAR NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies_dim(id)
);

-- Table: contacts_dim
CREATE TABLE contacts_dim (
    id UUID PRIMARY KEY,
    company_id UUID,
    name VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies_dim(id)
);

-- Table: prompt_config
CREATE TABLE prompt_config (
    id UUID PRIMARY KEY,
    name VARCHAR,
    model VARCHAR,
    version INTEGER,
    system_instructions VARCHAR NOT NULL,
    json_validation VARCHAR NOT NULL
);

-- Table: completions_fact
CREATE TABLE completions_fact (
    id UUID PRIMARY KEY,
    prompt_id UUID NOT NULL,
    context VARCHAR NOT NULL,
    raw_output VARCHAR NOT NULL,
    normalized_output VARCHAR NOT NULL,
    FOREIGN KEY (prompt_id) REFERENCES prompt_config(id) -- Assuming prompt_config table exists
);

-- Table: dq_completion_fact
CREATE TABLE dq_completion_fact (
    id UUID PRIMARY KEY,
    completion_id UUID NOT NULL,
    type VARCHAR NOT NULL,
    result VARCHAR NOT NULL,
    FOREIGN KEY (completion_id) REFERENCES completions_fact(id)
);

