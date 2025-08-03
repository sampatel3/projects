SELECT  "ACCOUNT_CLASS"        AS product_id,
        "AC_CLASS_TYPE"        AS type,
        "DESCRIPTION"          AS description,
        "MUDARABAH_ACC_CLASS"  AS islamic
  FROM  {{ source('fcubs', 'sttm_account_class')}}
