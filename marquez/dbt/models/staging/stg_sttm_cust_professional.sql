SELECT  "CUSTOMER_NO"  ::int8           AS customer_id,
        "EMPLOYER"     ::varchar(150)   AS employer_name,
        "SALARY"       ::float8         AS income
  FROM  {{ source('fcubs', 'sttm_cust_professional')}}
