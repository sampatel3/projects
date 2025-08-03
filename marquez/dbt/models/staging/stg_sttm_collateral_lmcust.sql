SELECT
      "CUST_AC_NO"                                                                        AS account_number,
      SPLIT_PART(MAX(CONCAT("EXPIRY_DATE",'|#|',"CLOSED")),'|#|',2)                       AS closed,
      MAX("EXPIRY_DATE")                                                                  AS expiry_date,
      SPLIT_PART(MAX(CONCAT("EXPIRY_DATE",'|#|',"LINKED_AMOUNT")),'|#|',2)  ::decimal     AS max_overdraft_limit
FROM  {{ source('fcubs', 'sttm_collateral_lmcust') }}
GROUP  BY 1