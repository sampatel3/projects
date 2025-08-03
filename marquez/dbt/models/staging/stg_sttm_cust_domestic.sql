SELECT  "CUSTOMER_NO"     ::int8        AS customer_id,
        "MARITAL_STATUS"  ::varchar(50) AS status
  FROM  {{source('fcubs', 'sttm_cust_domestic')}}
