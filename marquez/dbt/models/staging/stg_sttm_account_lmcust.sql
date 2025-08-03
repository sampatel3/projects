SELECT
    "CUST_AC_NO"    AS account_number,
    "RECORD_STAT"   AS record_stat,
    "CCY"           AS currency
FROM {{ source('fcubs', 'sttm_account_lmcust')}}
