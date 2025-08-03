-- Connect to the database
-- \c marquezdb;  -- Make sure you're connected to the correct database

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a dummy schema
CREATE SCHEMA IF NOT EXISTS fcubs;
CREATE SCHEMA IF NOT EXISTS openfinance;


-- Create table for ictm_acc
CREATE TABLE fcubs.ictm_acc (
    "ACC" VARCHAR(50),
    "MATURITY_DATE" DATE
);

-- Insert some dummy data into the table
INSERT INTO fcubs.ictm_acc ("ACC", "MATURITY_DATE") VALUES
('ACC001', '2025-12-31'),
('ACC002', '2026-01-15'),
('ACC003', '2025-11-30'),
('ACC001', '2026-06-30'),
('ACC002', '2026-05-05');

-- Create the table for sttm_ac_linked_entities
CREATE TABLE IF NOT EXISTS fcubs.sttm_ac_linked_entities (
    "JOINT_HOLDER_CODE" INT8,
    "JOINT_HOLDER" VARCHAR(50),
    "CUST_AC_NO" VARCHAR(50)
);

-- Insert some dummy data into the table
INSERT INTO fcubs.sttm_ac_linked_entities ("JOINT_HOLDER_CODE", "JOINT_HOLDER", "CUST_AC_NO") VALUES
(101, 'John Doe', 'ACC001'),
(102, 'Jane Smith', 'ACC002'),
(103, 'Tom Brown', 'ACC003'),
(104, 'Lucy Green', 'ACC004');

-- Create the table for sttm_account_class
CREATE TABLE IF NOT EXISTS fcubs.sttm_account_class (
    "ACCOUNT_CLASS" VARCHAR(50),
    "AC_CLASS_TYPE" VARCHAR(50),
    "DESCRIPTION" VARCHAR(255),
    "MUDARABAH_ACC_CLASS" BOOLEAN
);

-- Insert some dummy data into the table
INSERT INTO fcubs.sttm_account_class ("ACCOUNT_CLASS", "AC_CLASS_TYPE", "DESCRIPTION", "MUDARABAH_ACC_CLASS") VALUES
('A001', 'Type1', 'Standard account', FALSE),
('A002', 'Type2', 'Premium account', TRUE),
('A003', 'Type1', 'Basic account', FALSE),
('A004', 'Type3', 'Savings account', TRUE);

-- Create the table for sttm_account_lmcust
CREATE TABLE IF NOT EXISTS fcubs.sttm_account_lmcust (
    "CUST_AC_NO" VARCHAR(50),
    "RECORD_STAT" VARCHAR(50),
    "CCY" VARCHAR(3)
);

-- Insert some dummy data into the table
INSERT INTO fcubs.sttm_account_lmcust ("CUST_AC_NO", "RECORD_STAT", "CCY") VALUES
('12345', 'Active', 'USD'),
('67890', 'Inactive', 'EUR'),
('54321', 'Active', 'GBP'),
('98765', 'Suspended', 'JPY');

-- Create the table for sttm_collateral_lmcust
CREATE TABLE IF NOT EXISTS fcubs.sttm_collateral_lmcust (
    "CUST_AC_NO" VARCHAR(50),
    "EXPIRY_DATE" DATE,
    "CLOSED" VARCHAR(50),
    "LINKED_AMOUNT" DECIMAL
);

-- Insert some dummy data into the table
INSERT INTO fcubs.sttm_collateral_lmcust ("CUST_AC_NO", "EXPIRY_DATE", "CLOSED", "LINKED_AMOUNT") VALUES
('12345', '2025-12-31', 'Yes', 5000.00),
('67890', '2026-06-30', 'No', 3000.50),
('54321', '2027-03-15', 'Yes', 7000.25),
('98765', '2024-11-01', 'No', 1000.75);

-- Create the table for sttm_cust_account
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_account (
    "CUST_AC_NO" VARCHAR(50),
    "CHECKER_DT_STAMP" TIMESTAMP,
    "AC_DESC" VARCHAR(255),
    "ACCOUNT_TYPE" VARCHAR(50),
    "ACC_STATUS" VARCHAR(50),
    "IBAN_AC_NO" VARCHAR(50),
    "AC_OPEN_DATE" DATE,
    "CCY" VARCHAR(5),
    "ACCOUNT_CLASS" VARCHAR(50),
    "CUST_NO" INT,
    "ACY_AVL_BAL" DECIMAL,
    "DATE_LAST_DR" DATE,
    "DATE_LAST_CR" DATE,
    "RECORD_STAT" VARCHAR(50),
    "AC_STAT_DORMANT" VARCHAR(50),
    "SALARY_ACCOUNT" VARCHAR(50),
    "JOINT_AC_INDICATOR" VARCHAR(50)
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_account (
    "CUST_AC_NO", "CHECKER_DT_STAMP", "AC_DESC", "ACCOUNT_TYPE", "ACC_STATUS", "IBAN_AC_NO", "AC_OPEN_DATE", "CCY",
    "ACCOUNT_CLASS", "CUST_NO", "ACY_AVL_BAL", "DATE_LAST_DR", "DATE_LAST_CR", "RECORD_STAT", "AC_STAT_DORMANT", "SALARY_ACCOUNT","JOINT_AC_INDICATOR"
) VALUES
    ('12345', '2023-12-31 12:00:00', 'John Doe', 'Savings', 'Active', 'IBAN12345', '2020-01-01', 'USD', 'A123',
     1001, 5000.00, '2023-12-01', '2023-12-15', 'Active', 'No', 'No', 'S'),
    ('67890', '2023-12-31 12:00:00', 'Jane Smith', 'Checking', 'Inactive', 'IBAN67890', '2021-02-15', 'EUR', 'B456',
     1002, 3000.50, '2023-11-25', '2023-12-05', 'Inactive', 'Yes', 'Yes', 'S'),
    ('54321', '2023-12-31 12:00:00', 'Alice Johnson', 'Business', 'Active', 'IBAN54321', '2022-03-10', 'GBP', 'C789',
     1003, 7000.75, '2023-12-10', '2023-12-20', 'Active', 'No', 'No', 'J'),
    ('98765', '2023-12-31 12:00:00', 'Bob Lee', 'Savings', 'Active', 'IBAN98765', '2020-06-25', 'USD', 'D012',
     1004, 1200.50, '2023-11-30', '2023-12-10', 'Active', 'Yes', 'Yes', 'J');

-- Create the table for sttm_cust_domestic
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_domestic (
    "CUSTOMER_NO" INT,
    "MARITAL_STATUS" VARCHAR(50)
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_domestic ("CUSTOMER_NO", "MARITAL_STATUS")
VALUES
    (1001, 'Married'),
    (1002, 'Single'),
    (1003, 'Divorced'),
    (1004, 'Widowed');

-- Create the table for sttm_cust_personal_custom
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_personal_custom (
    "CUSTOMER_NO" INT,
    "INCOME_SOURCE" VARCHAR(50),
    "PROFESSION" VARCHAR(100)
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_personal_custom ("CUSTOMER_NO", "INCOME_SOURCE", "PROFESSION")
VALUES
    (1001, 'Employment', 'Engineer'),
    (1002, 'Business', 'Entrepreneur'),
    (1003, 'Retirement', 'Retired'),
    (1004, 'Self-employed', 'Freelancer');

-- Create the table for sttm_cust_personal
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_personal (
    "CUSTOMER_NO" INT,
    "DATE_OF_BIRTH" TIMESTAMPTZ,
    "MOBILE_NUMBER" VARCHAR(50),
    "E_MAIL" VARCHAR(100),
    "P_NATIONAL_ID" VARCHAR(50),
    "NATIONAL_ID_EXPDT" DATE
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_personal ("CUSTOMER_NO", "DATE_OF_BIRTH", "MOBILE_NUMBER", "E_MAIL", "P_NATIONAL_ID", "NATIONAL_ID_EXPDT")
VALUES
    (1001, '1985-06-15 14:30:00+00', '1234567890', 'john.doe@email.com', 'A1234567890', '2030-06-15'),
    (1002, '1990-04-22 09:45:00+00', '9876543210', 'jane.smith@email.com', 'B9876543210', '2032-12-31'),
    (1003, '1978-11-05 11:00:00+00', '5551239876', 'bob.jones@email.com', 'C1239876543', '2025-05-01'),
    (1004, '1995-03-11 16:00:00+00', '5557654321', 'alice.brown@email.com', 'D4561237890', '2028-02-20');

-- Create the table for sttm_cust_profession_custom
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_profession_custom (
    "CUSTOMER_NO" INT,
    "DATE_OF_JOINING" TIMESTAMPTZ
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_profession_custom ("CUSTOMER_NO", "DATE_OF_JOINING")
VALUES
    (1001, '2020-01-15 10:30:00+00'),
    (1002, '2018-03-20 11:45:00+00'),
    (1003, '2019-07-05 09:00:00+00'),
    (1004, '2021-10-11 13:30:00+00');

-- Create the table for sttm_cust_professional
CREATE TABLE IF NOT EXISTS fcubs.sttm_cust_professional (
    "CUSTOMER_NO" INT,
    "EMPLOYER" VARCHAR(150),
    "SALARY" FLOAT8
);

-- Insert dummy data into the table
INSERT INTO fcubs.sttm_cust_professional ("CUSTOMER_NO", "EMPLOYER", "SALARY")
VALUES
    (1001, 'Tech Corp', 60000),
    (1002, 'Health Inc', 75000),
    (1003, 'School Ltd', 45000),
    (1004, 'Law Firm', 90000);

-- Create the table for sttm_ac_linked_entities
CREATE TABLE IF NOT EXISTS fcubs.sttm_ac_linked_entities (
    "CUST_AC_NO" INT,
    "JOINT_HOLDER" VARCHAR(50)
);

-- Insert dummy data into sttm_ac_linked_entities
INSERT INTO fcubs.sttm_ac_linked_entities ("CUST_AC_NO", "JOINT_HOLDER")
VALUES
    (2001, 'POA'),
    (2002, 'Other');

-- Create the table for sttm_customer
CREATE TABLE IF NOT EXISTS fcubs.sttm_customer (
    "CUSTOMER_NO" INT,
    "CUSTOMER_TYPE" VARCHAR(50),
    "FULL_NAME" VARCHAR(100),
    "CUSTOMER_NAME1" VARCHAR(100),
    "NATIONALITY" VARCHAR(100),
    "CHECKER_DT_STAMP" TIMESTAMPTZ,
    "ADDRESS_LINE1" VARCHAR(150),
    "PINCODE" VARCHAR(50),
    "COUNTRY" VARCHAR(2),
    "DECEASED" VARCHAR(50)
);

-- Insert dummy data into sttm_customer
INSERT INTO fcubs.sttm_customer ("CUSTOMER_NO", "CUSTOMER_TYPE", "FULL_NAME", "CUSTOMER_NAME1", "NATIONALITY", "CHECKER_DT_STAMP", "ADDRESS_LINE1", "PINCODE", "COUNTRY", "DECEASED")
VALUES
    (1001, 'Individual', 'John Doe', 'John', 'USA', NOW(), '123 Main St', '12345', 'US', 'No'),
    (1002, 'Individual', 'Jane Smith', 'Jane', 'USA', NOW(), '456 Oak St', '67890', 'US', 'No');

-- Create the table for sttm_account_class
CREATE TABLE IF NOT EXISTS fcubs.sttm_account_class (
    "ACCOUNT_CLASS" VARCHAR(50),
    "AC_CLASS_TYPE" VARCHAR(50),
    "DESCRIPTION" VARCHAR(255),
    "MUDARABAH_ACC_CLASS" VARCHAR(50)
);

-- Insert dummy data into sttm_account_class
INSERT INTO fcubs.sttm_account_class ("ACCOUNT_CLASS", "AC_CLASS_TYPE", "DESCRIPTION", "MUDARABAH_ACC_CLASS")
VALUES
    ('ACC001', 'Type1', 'Savings Account', 'Yes'),
    ('ACC002', 'Type2', 'Checking Account', 'No');

-- Create Enum for country_iso_3a_code
CREATE TYPE country_iso_3a_code AS ENUM (
    'AFG', 'ALB', 'DZA', 'ASM', 'AND', 'AGO', 'AIA', 'ATA', 'ATG', 'ARG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BHS',
    'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN', 'BOL', 'BES', 'BIH', 'BWA', 'BVT', 'BRA', 'IOT',
    'BRN', 'BGR', 'BFA', 'BDI', 'CPV', 'KHM', 'CMR', 'CAN', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'CXR', 'CCK', 'COL',
    'COM', 'COG', 'COD', 'COK', 'CRI', 'CIV', 'HRV', 'CUB', 'CUW', 'CYP', 'CZE', 'DNK', 'DJI', 'DMA', 'DOM', 'ECU',
    'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'SWZ', 'ETH', 'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'PYF', 'ATF', 'GAB',
    'GMB', 'GEO', 'DEU', 'GHA', 'GIB', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GGY', 'GIN', 'GNB', 'GUY', 'HTI',
    'HMD', 'VAT', 'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JAM', 'JPN',
    'JEY', 'JOR', 'KAZ', 'KEN', 'KIR', 'PRK', 'KOR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LIE',
    'LTU', 'LUX', 'MAC', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MHL', 'MTQ', 'MRT', 'MUS', 'MYT', 'MEX', 'FSM',
    'MDA', 'MCO', 'MNG', 'MNE', 'MSR', 'MAR', 'MOZ', 'MMR', 'NAM', 'NRU', 'NPL', 'NLD', 'NCL', 'NZL', 'NIC', 'NER',
    'NGA', 'NIU', 'NFK', 'MNP', 'NOR', 'OMN', 'PAK', 'PLW', 'PSE', 'PAN', 'PNG', 'PRY', 'PER', 'PHL', 'PCN', 'POL',
    'PRT', 'PRI', 'QAT', 'MKD', 'ROU', 'RUS', 'RWA', 'REU', 'BLM', 'SHN', 'KNA', 'LCA', 'MAF', 'SPM', 'VCT', 'WSM',
    'SMR', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SXM', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SGS', 'SSD',
    'ESP', 'LKA', 'SDN', 'SUR', 'SJM', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'TZA', 'THA', 'TLS', 'TGO', 'TKL', 'TON',
    'TTO', 'TUN', 'TUR', 'TKM', 'TCA', 'TUV', 'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'URY', 'UZB', 'VUT', 'VEN', 'VNM',
    'VGB', 'VIR', 'WLF', 'ESH', 'YEM', 'ZMB', 'ZWE'
);

-- Create Enum for evidence_type_enum
CREATE TYPE evidence_type_enum AS ENUM (
    'document', 'electronic_record'
);

-- Create Enum for address_type_enum
CREATE TYPE address_type_enum AS ENUM (
    'Business', 'Correspondence', 'DeliveryTo', 'MailTo', 'POBox', 'Postal', 'Residential', 'Statement'
);

-- Create Enum for document_type_enum
CREATE TYPE document_type_enum AS ENUM (
    'passport', 'driving_permit', 'idcard', 'residence_permit'
);

-- Create Enum for calendar_type_enum
CREATE TYPE calendar_type_enum AS ENUM (
    'IslamicCalendar', 'GregorianCalendar'
);

-- Create Enum for party_type_enum
CREATE TYPE party_type_enum AS ENUM (
    'Delegate', 'Joint', 'Sole'
);

-- Create Enum for account_status_enum
CREATE TYPE account_status_enum AS ENUM (
    'Active', 'Inactive', 'Dormant', 'Unclaimed', 'Deceased', 'Suspended', 'Closed'
);

-- Create Enum for account_type_enum
CREATE TYPE account_type_enum AS ENUM (
    'Retail', 'SME', 'Corporate'
);

-- Create Enum for account_subtype_enum
CREATE TYPE account_subtype_enum AS ENUM (
    'CurrentAccount', 'Savings', 'Investment', 'Other'
);

-- Create Enum for credit_line_type_enum
CREATE TYPE credit_line_type_enum AS ENUM (
    'Available', 'Credit', 'Emergency', 'Pre-Agreed', 'Temporary'
);

-- Create Enum for balance_type_enum
CREATE TYPE balance_type_enum AS ENUM (
    'ClosingAvailable', 'ClosingBooked', 'ClosingCleared', 'Expected', 'ForwardAvailable',
    'Information', 'InterimAvailable', 'InterimBooked', 'InterimCleared',
    'OpeningAvailable', 'OpeningBooked', 'OpeningCleared', 'PreviouslyClosedBooked'
);

-- Create Enum for account_role_enum
CREATE TYPE account_role_enum AS ENUM (
    'Administrator', 'Beneficiary', 'CustodianForMinor', 'Granter', 'LegalGuardian', 
    'OtherParty', 'PowerOfAttorney', 'Principal', 'Protector', 'RegisteredShareholderName', 
    'SecondaryOwner', 'SeniorManagingOfficial', 'Settlor', 'SuccessorOnDeath'
);

-- Create Enum for currency_iso_3a_code
CREATE TYPE currency_iso_3a_code AS ENUM (
  'USD', 'AED', 'EUR', 'GBP', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 
  'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 
  'BRL', 'BSD', 'BTN', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLP', 'CNY', 
  'COP', 'CRC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 
  'ETB', 'FJD', 'FKP', 'FOK', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 
  'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 
  'IRR', 'ISK', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KID', 'KMF', 'KRW', 
  'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 
  'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRU', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 
  'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 
  'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 
  'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLE', 'SLL', 'SOS', 'SRD', 'SSP', 'STN', 
  'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY', 'TTD', 'TVD', 
  'TWD', 'TZS', 'UAH', 'UGX', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST', 'XAF', 
  'XCD', 'XDR', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMW', 'ZWL'
);

-- Create Enum for country_iso_2a_code
CREATE TYPE country_iso_2a_code AS ENUM (
  'AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ', 
  'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BV', 'BR', 
  'IO', 'BN', 'BG', 'BF', 'BI', 'CV', 'KH', 'CM', 'CA', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC', 
  'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 
  'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'SZ', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 
  'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 
  'HT', 'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP', 
  'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 
  'LU', 'MO', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 
  'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 
  'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'MK', 
  'RO', 'RU', 'RW', 'RE', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 
  'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS', 'ES', 'LK', 'SD', 'SR', 'SJ', 'SE', 
  'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 
  'UA', 'AE', 'GB', 'US', 'UY', 'UZ', 'VU', 'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW'
);

CREATE ROLE web_anon;
GRANT ALL PRIVILEGES ON DATABASE marquezdb TO sampatel3;
GRANT ALL PRIVILEGES ON DATABASE marquezdb TO web_anon;
