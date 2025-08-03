{{ 
    config(
        materialized='view',
        tags=['finance', 'products', 'fcubs'],
        description='Provides product details linked to customer accounts.'
    ) 
}}


SELECT
	product_id	AS product_id,
	description	AS name,
	type		AS type,
	islamic		AS islamic
FROM {{ ref('stg_sttm_account_class') }}
GROUP BY 1, 2, 3, 4
