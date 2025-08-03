SELECT  "CUSTOMER_NO"        ::int8          AS customer_id,
        "DATE_OF_BIRTH"      ::timestamptz   AS birthdate,
        "MOBILE_NUMBER"      ::varchar(50)   AS phone_number,
        "E_MAIL"             ::varchar(100)  AS email_address,
        "P_NATIONAL_ID"      ::varchar(50)   AS personal_number,
        "NATIONAL_ID_EXPDT"  ::date          AS document_expiry_date,
        'idcard'             ::varchar(50)   AS document_type
  FROM  {{ source('fcubs', 'sttm_cust_personal')}} c
