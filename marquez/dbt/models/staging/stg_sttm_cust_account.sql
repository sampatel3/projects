SELECT
        "CUST_AC_NO"                                                                            AS account_number,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"AC_DESC")),'|#|',2)                     AS account_holder_name,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"ACCOUNT_TYPE")),'|#|',2)                AS account_subtype,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"ACC_STATUS")),'|#|',2)                  AS acc_status, -- unused
        MAX("CHECKER_DT_STAMP")                                                                 AS status_update_datetime,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"IBAN_AC_NO")),'|#|',2)                  AS account_iban,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"AC_OPEN_DATE")),'|#|',2)                AS opening_date,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"CCY")),'|#|',2)                         AS currency,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"ACCOUNT_CLASS")),'|#|',2)               AS product_id,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"CUST_NO")),'|#|',2)          ::int8     AS customer_id,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"ACY_AVL_BAL")),'|#|',2)      ::decimal  AS total_balance,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"DATE_LAST_DR")),'|#|',2)                AS date_last_dr,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"DATE_LAST_CR")),'|#|',2)                AS date_last_cr,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"RECORD_STAT")),'|#|',2)                 AS record_stat,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"AC_STAT_DORMANT")),'|#|',2)             AS ac_stat_dormant,
        SPLIT_PART(MAX(CONCAT("CHECKER_DT_STAMP",'|#|',"SALARY_ACCOUNT")),'|#|',2)              AS salary_account
  FROM  {{ source('fcubs', 'sttm_cust_account') }}
 GROUP  BY 1
