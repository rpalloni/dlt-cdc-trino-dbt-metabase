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

INSERT INTO companies (name, vat_number, country)
SELECT
    (ARRAY[
        'Acme', 'Globex', 'Initech', 'Umbrella', 'Stark Industries',
        'Wayne Enterprises', 'Oscorp', 'Cyberdyne', 'Wonka', 'Nakatomi',
        'Tyrell', 'Weyland', 'Massive Dynamic', 'Pied Piper', 'Hooli',
        'Dunder Mifflin', 'Vandelay', 'Sterling Cooper', 'Prestige', 'Soylent'
    ])[s.i]
    || ' ' ||
    (ARRAY['S.r.l.', 'S.p.A.', 'GmbH', 'Ltd.', 'SAS', 'Inc.', 'B.V.', 'AG'])[floor(random() * 8 + 1)::int] AS name,
    (ARRAY['IT', 'DE', 'FR', 'ES', 'NL'])[floor(random() * 5 + 1)::int]
    || lpad((random() * 99999999999)::bigint::text, 11, '0')                                               AS vat_number,
    (ARRAY['IT', 'IT', 'IT', 'DE', 'DE', 'FR', 'FR', 'ES', 'NL', 'NL'])[floor(random() * 10 + 1)::int]     AS country
FROM generate_series(1, 20) AS s(i);

INSERT INTO invoices (company_id, invoice_number, amount, currency, status, issued_at, due_at, created_at, updated_at)
SELECT
    (SELECT id FROM companies WHERE s.i IS NOT NULL ORDER BY random() LIMIT 1)                          AS company_id,
    'INV-' || to_char(CURRENT_DATE - (random() * 730)::int, 'YYYY') || '-' || lpad(s.i::text, 4, '0')   AS invoice_number,
    (random() * 9990 + 10)::numeric(12,2)                                                               AS amount,
    (ARRAY['EUR', 'EUR', 'EUR', 'USD', 'GBP'])[floor(random() * 5 + 1)::int]                            AS currency,
    (ARRAY['draft', 'pending', 'pending', 'pending', 'paid', 'paid', 'paid', 'paid', 'overdue', 'overdue'])
        [floor(random() * 10 + 1)::int]                                                                 AS status,
    CURRENT_DATE - (random() * 730)::int                                                                AS issued_at,
    CURRENT_DATE - (random() * 730)::int + (random() * 60 + 30)::int                                    AS due_at,
    now() - (random() * interval '730 days')                                                            AS created_at,
    now() - (random() * interval '30 days')                                                             AS updated_at
FROM generate_series(1, 1000) AS s(i);

-- CDC publication for OLake
CREATE PUBLICATION olake FOR TABLE companies, invoices;
SELECT pg_create_logical_replication_slot('olake_slot', 'pgoutput')
WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'olake_slot');