{{ config(
    materialized = "view",
    tags = ['finance', 'accounts', 'fcubs'],
    description = 'Aggregates account details, including account status, holder information, and credit line details.',
    post_hook = [
        "
        CREATE OR REPLACE FUNCTION openfinance_api.of_fcubs_accounts_by_opening_date(
            from_opening_date DATE,
            to_opening_date DATE
        )
        RETURNS SETOF openfinance_api.of_fcubs_accounts
        AS $$
        BEGIN
            RETURN QUERY
            SELECT *
            FROM openfinance_api.of_fcubs_accounts
            WHERE (from_opening_date IS NULL OR opening_date >= from_opening_date)
              AND (to_opening_date IS NULL OR opening_date <= to_opening_date);
        END;
        $$ LANGUAGE plpgsql STABLE;
        "
    ]
) }}

SELECT
      public.uuid_generate_v4()                             AS account_id,
      sc.customer_id                                        AS customer_id,
      sac.product_id                                        AS product_id,
      CASE
            WHEN sc.account_type = 'I'
                  THEN 'Retail'
            WHEN sc.account_type = 'C'
            OR sc.account_type = 'B'
                  THEN 'Corporate'
            ELSE NULL
      END                                                   AS account_type,
      CASE
            WHEN sca.account_subtype = 'S'
                  THEN 'Savings'
            WHEN sca.account_subtype = 'U'
                  THEN 'CurrentAccount'
            ELSE 'Other'
      END                                                   AS account_subtype,
      sac.description                                       AS description,
      sc.customer_name1                                     AS nickname, -- same as account_holder_short_name
      CASE
            WHEN sc.deceased = 'Y'
                  THEN 'Deceased'
            WHEN sca.record_stat = 'C'
                  THEN 'Closed'
            WHEN sca.ac_stat_dormant = 'Y'
                  THEN 'Dormant'
            ELSE 'Active'
      END                                                   AS status,
      sca.status_update_datetime                            AS status_update_datetime,
      COALESCE(sca.account_number, sca.account_iban)        AS account_number,
      COALESCE(sca.account_iban, sca.account_number)        AS account_iban,
      sca.opening_date                                      AS opening_date,
      ia.maturity_date                                      AS maturity_date,
      sca.total_balance                                     AS total_balance,
      CASE
            WHEN sca.total_balance >= 0
                  THEN 'Credit'
            ELSE 'Debit'
      END                                                   AS credit_debit_indicator,
      sca.currency                                          AS currency,
      GREATEST(sca.date_last_dr, sca.date_last_cr)          AS last_updated,
      scl.max_overdraft_limit                               AS max_overdraft_limit,
      NULL                                                  AS notes, -- null
      sca.account_holder_name                               AS account_holder_name,
      sc.customer_name1                                     AS account_holder_short_name, -- same as nickname
      CASE
            WHEN sal.record_stat = 'O'
            AND expiry_date > current_date
            AND closed ='N'
                  THEN 'Pre-Agreed'
            ELSE NULL
      END                                                   AS credit_line_type,
      CASE
            WHEN sal.record_stat = 'O'
            AND expiry_date > current_date
            AND closed ='N'
                  THEN 1
            ELSE 0
      END                                                   AS credit_line_included
FROM  {{ ref('stg_sttm_cust_account') }} sca
LEFT  JOIN {{ ref('stg_sttm_customer') }} sc
      USING (customer_id)
LEFT  JOIN {{ ref('stg_sttm_account_class') }} sac
      USING (product_id)
LEFT  JOIN {{ ref('stg_ictm_acc') }} ia
      USING (account_number)
LEFT  JOIN {{ ref('stg_sttm_collateral_lmcust') }} scl
      USING (account_number)
LEFT  JOIN {{ ref('stg_sttm_account_lmcust') }} sal
      USING (account_number)
