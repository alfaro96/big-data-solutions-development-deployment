"""
The purpose of this script is to build the behavioral feature table
for the `Feature Store`. It reads clean events from the `Silver` layer
and calculates time-windowed aggregations per customer (e.g., spending
velocity, transaction counts, risk signals).

This table is keyed by `customer_id` and is designed to be published
to the `Online Feature Store` for real-time inference lookups.

Architecture note: We use a batch processing approach with rolling windows 
(`Window.partitionBy`) to guarantee point-in-time correctness. This ensures
every single transaction retains its exact historical context without data
loss.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    avg,
    col,
    count,
    collect_set,
    lit,
    max,
    min,
    size,
    sum,
    when
)


###############################################################################
# Configuration variables and constants
###############################################################################

silver_events_source = "silver_fraud_events"
EPSILON = 1e-6  # Small value used to avoid division by zero


###############################################################################
# Final feature table: rolling window aggregations
###############################################################################

gold_aggregations_table_name = "gold_customer_aggregations"
gold_aggregations_comment = """
This managed table acts as the **behavioral feature table** in the `Feature
Store`. It consolidates time-windowed aggregations per customer across four
temporal resolutions (1 hour, 24 hours, 7 days, 30 days) into a single row per
customer per transaction timestamp.

It is keyed by `customer_id` and is designed to be published to the `Online
Feature Store` for low-latency lookups during real-time inference. When a new
transaction arrives, the model serving layer queries this table by `customer_id`
to retrieve the customer's latest behavioral signals.
"""

gold_profile_table_properties = {"delta.enableChangeDataFeed": "true"}
gold_aggregations_schema = """
    customer_id STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    count_tx_1h BIGINT,
    sum_amount_1h DOUBLE,
    avg_amount_1h DOUBLE,
    distinct_merchants_1h INT,
    count_cross_border_1h BIGINT,
    count_tx_24h BIGINT,
    sum_amount_24h DOUBLE,
    avg_amount_24h DOUBLE,
    max_amount_24h DOUBLE,
    distinct_merchants_24h INT,
    distinct_countries_24h INT,
    count_tor_vpn_24h BIGINT,
    count_3ds_failed_24h BIGINT,
    count_tx_7d BIGINT,
    sum_amount_7d DOUBLE,
    avg_amount_7d DOUBLE,
    distinct_merchants_7d INT,
    distinct_countries_7d INT,
    distinct_devices_7d INT,
    count_tx_30d BIGINT,
    sum_amount_30d DOUBLE,
    avg_amount_30d DOUBLE,
    max_amount_30d DOUBLE,
    min_amount_30d DOUBLE,
    distinct_merchants_30d INT,
    distinct_countries_30d INT,
    num_fraud_confirmed_30d BIGINT,
    amount_vs_avg_spend_ratio_30d DOUBLE,
    CONSTRAINT gold_customer_aggregations_pk PRIMARY KEY (customer_id, timestamp TIMESERIES)
"""


@dp.table(
    name = gold_aggregations_table_name,
    comment = gold_aggregations_comment,
    table_properties = gold_profile_table_properties,
    schema = gold_aggregations_schema
)
def gold_customer_aggregations():
    """
    Computes rolling window aggregations in a single pass using batch processing.
    """
    df_silver = spark.read.table(silver_events_source)

    # Convert timestamp to seconds (long) to use "rangeBetween" mathematically
    df = df_silver.withColumn("ts_sec", col("timestamp").cast("long"))

    # Define rolling windows looking back from each transaction
    w_1h = Window.partitionBy("customer_id").orderBy("ts_sec").rangeBetween(-3600, 0)
    w_24h = Window.partitionBy("customer_id").orderBy("ts_sec").rangeBetween(-86400, 0)
    w_7d = Window.partitionBy("customer_id").orderBy("ts_sec").rangeBetween(-7 * 86400, 0)
    w_30d = Window.partitionBy("customer_id").orderBy("ts_sec").rangeBetween(-30 * 86400, 0)

    # Compute all aggregations on the fly
    df_agg = df.select(
        col("customer_id"),
        col("timestamp"),

        # 1 hour
        count("transaction_id").over(w_1h).alias("count_tx_1h"),
        sum("amount").over(w_1h).alias("sum_amount_1h"),
        avg("amount").over(w_1h).alias("avg_amount_1h"),
        size(collect_set("merchant_id").over(w_1h)).alias("distinct_merchants_1h"),
        sum(when(col("cross_border") == 1, 1).otherwise(0)).over(w_1h).alias("count_cross_border_1h"),

        # 24 hours
        count("transaction_id").over(w_24h).alias("count_tx_24h"),
        sum("amount").over(w_24h).alias("sum_amount_24h"),
        avg("amount").over(w_24h).alias("avg_amount_24h"),
        max("amount").over(w_24h).alias("max_amount_24h"),
        size(collect_set("merchant_id").over(w_24h)).alias("distinct_merchants_24h"),
        size(collect_set("merchant_country").over(w_24h)).alias("distinct_countries_24h"),
        sum(when(col("is_tor_or_vpn") == 1, 1).otherwise(0)).over(w_24h).alias("count_tor_vpn_24h"),
        sum(when(col("three_ds_result") == "FAILED", 1).otherwise(0)).over(w_24h).alias("count_3ds_failed_24h"),

        # 7 days
        count("transaction_id").over(w_7d).alias("count_tx_7d"),
        sum("amount").over(w_7d).alias("sum_amount_7d"),
        avg("amount").over(w_7d).alias("avg_amount_7d"),
        size(collect_set("merchant_id").over(w_7d)).alias("distinct_merchants_7d"),
        size(collect_set("merchant_country").over(w_7d)).alias("distinct_countries_7d"),
        size(collect_set("device_type").over(w_7d)).alias("distinct_devices_7d"),

        # 30 days
        count("transaction_id").over(w_30d).alias("count_tx_30d"),
        sum("amount").over(w_30d).alias("sum_amount_30d"),
        avg("amount").over(w_30d).alias("avg_amount_30d"),
        max("amount").over(w_30d).alias("max_amount_30d"),
        min("amount").over(w_30d).alias("min_amount_30d"),
        size(collect_set("merchant_id").over(w_30d)).alias("distinct_merchants_30d"),
        size(collect_set("merchant_country").over(w_30d)).alias("distinct_countries_30d"),
        sum(when(col("is_fraud") == 1, 1).otherwise(0)).over(w_30d).alias("num_fraud_confirmed_30d")
    )

    # Derived ratio feature
    df_final = df_agg.withColumn(
        "amount_vs_avg_spend_ratio_30d",
        col("sum_amount_24h") / (col("avg_amount_30d") + lit(EPSILON))
    )

    return df_final
