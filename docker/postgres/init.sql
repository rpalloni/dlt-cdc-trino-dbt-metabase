CREATE TABLE IF NOT EXISTS companies (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    vat_number   VARCHAR(50),
    country      VARCHAR(2)   NOT NULL DEFAULT 'IT',
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS invoices (
    id             SERIAL PRIMARY KEY,
    company_id     INTEGER       NOT NULL REFERENCES companies(id),
    invoice_number VARCHAR(50)   NOT NULL UNIQUE,
    amount         NUMERIC(12,2) NOT NULL,
    currency       CHAR(3)       NOT NULL DEFAULT 'EUR',
    status         VARCHAR(50)   NOT NULL DEFAULT 'draft',
    issued_at      DATE          NOT NULL DEFAULT CURRENT_DATE,
    due_at         DATE,
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ   NOT NULL DEFAULT now()
);

INSERT INTO companies (name, vat_number, country) VALUES
    ('Acme S.r.l.',   'IT12345678901', 'IT'),
    ('Globex S.p.A.', 'IT98765432100', 'IT'),
    ('Initech GmbH',  'DE123456789',   'DE')
ON CONFLICT DO NOTHING;

INSERT INTO invoices (company_id, invoice_number, amount, currency, status, issued_at, due_at) VALUES
    (1, 'INV-2024-001', 1200.00, 'EUR', 'paid',    '2024-01-15', '2024-02-15'),
    (1, 'INV-2024-002',  450.50, 'EUR', 'pending', '2024-02-01', '2024-03-01'),
    (2, 'INV-2024-003', 8750.00, 'EUR', 'paid',    '2024-01-20', '2024-02-20'),
    (2, 'INV-2024-004',  320.00, 'EUR', 'overdue', '2024-01-05', '2024-02-05'),
    (3, 'INV-2024-005', 5000.00, 'EUR', 'draft',   '2024-02-10', '2024-03-10')
ON CONFLICT DO NOTHING;

-- CDC publication for OLake
CREATE PUBLICATION olake FOR TABLE companies, invoices;
SELECT pg_create_logical_replication_slot('olake_slot', 'pgoutput')
WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'olake_slot');