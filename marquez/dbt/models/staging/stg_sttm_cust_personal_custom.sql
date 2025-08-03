SELECT  "CUSTOMER_NO"    ::int8          AS customer_id,
        "INCOME_SOURCE"  ::varchar(50)   AS source_income_wealth,
        "PROFESSION"     ::varchar(100)  AS profession
  FROM  {{source('fcubs', 'sttm_cust_personal_custom')}}
