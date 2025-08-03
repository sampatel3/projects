SELECT
    "JOINT_HOLDER_CODE"  ::int8         AS customer_id,
    "JOINT_HOLDER"       ::varchar(50)  AS joint_holder,
    "CUST_AC_NO"                        AS account_number
FROM  {{source('fcubs', 'sttm_ac_linked_entities') }}
