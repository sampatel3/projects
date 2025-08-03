SELECT  cprof."CUSTOMER_NO"      ::int8          AS customer_id,
        cprof."DATE_OF_JOINING"  ::timestamptz   AS date_of_joining
  FROM  {{ source('fcubs', 'sttm_cust_profession_custom')}} cprof
