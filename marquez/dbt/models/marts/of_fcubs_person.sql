{{ 
    config(
        materialized='view',
        tags=['finance', 'customers', 'fcubs'],
        description='Contains details of customers, including personal and professional information.'
    ) 
}}


SELECT  c.customer_id,
        c.customer_account_type                   AS type,
        c.account_role,
        c.customer_name1                          AS given_name,
        c.family_name                             AS middle_name,
        c.family_name,
        c.family_name                             AS full_name,
        c.customer_name1                          AS also_known_as,
        cp.birthdate,
        c.customer_id                             AS address_id,
        c.short_address,
        c.address_line_1,
        c.address_city,
        c.address_state,
        c.address_postcode,
        c.address_country,
        c.address_type,
        cpc.source_income_wealth,
        cpro.income,
        c.nationality,
        cp.phone_number,
        cp.email_address,
        cd.status,
        NULL                      ::varchar(50)   AS salutation,
        NULL                      ::varchar(100)  AS preferred_language,
        c.power_of_attorney                       AS power_of_attorney,
        c.salary_transfer                         AS salary_transfer,
        cpc.profession,
        c.last_updated,
        cpro.employer_name,
        cprof.date_of_joining,
	cp.document_type,
	cp.personal_number,
	cp.document_expiry_date
FROM  {{ ref('stg_sttm_customer') }} c
LEFT  JOIN {{ref('stg_sttm_cust_personal')}} cp              USING(customer_id)
LEFT  JOIN {{ref('stg_sttm_cust_personal_custom')}} cpc      USING(customer_id)
LEFT  JOIN {{ref('stg_sttm_cust_professional')}} cpro        USING(customer_id)
LEFT  JOIN {{ref('stg_sttm_cust_domestic')}} cd              USING(customer_id)
LEFT  JOIN {{ref('stg_sttm_cust_profession_custom')}} cprof  USING(customer_id)
