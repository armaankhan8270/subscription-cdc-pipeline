{% snapshot dim_support_ticket_snapshot %}

{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='ticket_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

SELECT * FROM {{ source('staging', 'support_tickets') }}

{% endsnapshot %}
