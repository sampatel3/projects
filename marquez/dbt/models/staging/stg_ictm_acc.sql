SELECT
    "ACC"                   AS account_number,
    MAX("MATURITY_DATE")    AS maturity_date
FROM {{ source('fcubs', 'ictm_acc')}}
GROUP BY 1
