WITH poa AS (
SELECT  acc."CUST_NO"  ::int8      AS customer_id,
        '1'            ::smallint  AS power_of_attorney
  FROM  {{ source('fcubs', 'sttm_cust_account') }} acc
  LEFT  JOIN {{ source('fcubs', 'sttm_ac_linked_entities') }} lent
        ON acc."CUST_AC_NO" = lent."CUST_AC_NO"
 WHERE  acc."RECORD_STAT"='O'
        AND lent."JOINT_HOLDER" = 'POA'
 GROUP  BY 1

),

salary_transfer AS (
SELECT  "CUST_NO"  ::int8      AS customer_id,
        '1'        ::smallint  AS salary_transfer
  FROM  {{ source('fcubs', 'sttm_cust_account') }}
 WHERE  "RECORD_STAT"='O'
        AND COALESCE("SALARY_ACCOUNT",'N')='Y'
 GROUP  BY 1

),

customer_account_type AS (
SELECT  "CUST_NO"  ::int8             AS customer_id,
        'Joint'    ::varchar(50)      AS type
  FROM  {{ source('fcubs', 'sttm_cust_account') }}
 WHERE  "JOINT_AC_INDICATOR"='J'
 GROUP  BY 1
)

SELECT
    "CUSTOMER_NO"                      ::int8                  AS customer_id,
    "CUSTOMER_TYPE"                    ::varchar(50)           AS account_type,
    COALESCE(cat.type, 'Sole')                                 AS customer_account_type,
    NULL                               ::account_role_enum     AS account_role,
    "FULL_NAME"                        ::varchar(100)          AS family_name,
    "CUSTOMER_NAME1"                   ::varchar(100)          AS customer_name1,
    "NATIONALITY"                      ::varchar(100)          AS nationality,
    NULL                               ::varchar(50)           AS salutation,
    NULL                               ::varchar(100)          AS preferred_language,
    COALESCE(poa.power_of_attorney,0)  ::smallint              AS power_of_attorney,
    COALESCE(st.salary_transfer,0)     ::smallint              AS salary_transfer,
    "CHECKER_DT_STAMP"                 ::timestamptz           AS last_updated,
    NULL                               ::varchar(150)          AS short_address,
    "ADDRESS_LINE1"                    ::varchar(150)          AS address_line_1,
    NULL                               ::varchar(100)          AS address_city,
    NULL                               ::varchar(100)          AS address_state,
    "PINCODE"                          ::varchar(50)           AS address_postcode,
    REPLACE("COUNTRY",'.',NULL)        ::country_iso_2a_code   AS address_country,
    'Residential'                      ::address_type_enum     AS address_type,
    "DECEASED"                         ::varchar(50)           AS deceased
FROM {{ source('fcubs', 'sttm_customer') }} cust
LEFT JOIN poa
     ON poa.customer_id = cust."CUSTOMER_NO" ::int8
LEFT JOIN salary_transfer st
     ON st.customer_id = cust."CUSTOMER_NO" ::int8
LEFT JOIN customer_account_type cat
     ON cat.customer_id = cust."CUSTOMER_NO" ::int8
