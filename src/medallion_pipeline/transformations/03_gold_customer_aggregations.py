"""
The purpose of this script is to build the behavioral feature table
for the `Feature Store`. It reads clean events from the `Silver` layer
and calculates time-windowed aggregations per customer (e.g., spending
velocity, transaction counts, risk signals).

This table is keyed by `customer_id` and is designed to be published
to the `Online Feature Store` for real-time inference lookups.

Architecture note: `Spark Structured Streaming` only allows one watermark
per stream. To compute multiple window sizes (1 hour, 24 hours, 7 days,
30 days), we declare one watermarked source per window size and then join
the results. This produces a single row per customer with all aggregated
features, ready for the `Feature Store`.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp
from pyspark.sql.functions import (
    avg,
    col,
    count,
    approx_count_distinct,
    lit,
    max,
    min,
    sum,
    when,
    window
)


###############################################################################
# Configuration variables and constants
###############################################################################

silver_events_source = "silver_fraud_events"

# Watermark tolerance: the maximum time a late event is accepted before
# being discarded. Spark uses this to safely clear old state from memory.
# Rule of thumb: set it slightly larger than the longest window you compute.
# If you use a 30-day window, use at least a 31-day watermark.
watermark_delay = "31 days"

# Window sizes used for the aggregations.
# Spark computes them using tumbling windows anchored to the event timestamp.
window_1h  = "1 hour"
window_24h = "24 hours"
window_7d = "7 days"
window_30d = "30 days"

EPSILON = 1e-6  # Small value used to avoid division by zero


###############################################################################
# Intermediate views: one aggregation per window size
#
# We use "@dp.view" to compute each window in isolation. Views are
# lightweight (they do not persist data to disk) and allow us to reuse
# the watermarked stream independently for each window size without
# triggering redundant I/O.
###############################################################################

agg_1h_view_name  = "vw_agg_customer_1h"
agg_24h_view_name = "vw_agg_customer_24h"
agg_7d_view_name = "vw_agg_customer_7d"
agg_30d_view_name = "vw_agg_customer_30d"


@dp.view(name = agg_1h_view_name)
def vw_agg_customer_1h():
    """
    Computes 1-hour tumbling window aggregations per customer.

    Captures burst signals: fraudsters typically test stolen cards
    in rapid succession within a very short time frame.
    """
    return (
        spark.readStream
             .table(silver_events_source)

             # The watermark tells Spark: "discard any event whose
             # timestamp is more than watermark_delay behind the
             # latest observed timestamp". Without this, Spark would
             # accumulate state for every customer indefinitely.
             .withWatermark("timestamp", watermark_delay)
             .groupBy(
                 col("customer_id"),
                 window(col("timestamp"), window_1h)
             )
             .agg(
                 count("transaction_id").alias("count_tx_1h"),
                 sum("amount").alias("sum_amount_1h"),
                 avg("amount").alias("avg_amount_1h"),
                 approx_count_distinct("merchant_id").alias("distinct_merchants_1h"),
                 # Count cross-border operations (proxy for geographic anomaly)
                 sum(
                     when(col("cross_border") == 1, 1).otherwise(0)
                 ).alias("count_cross_border_1h"),
             )
             .select(
                 col("customer_id"),
                 col("window.end").alias("window_end"),
                 col("count_tx_1h"),
                 col("sum_amount_1h"),
                 col("avg_amount_1h"),
                 col("distinct_merchants_1h"),
                 col("count_cross_border_1h"),
             )
    )


@dp.view(name = agg_24h_view_name)
def vw_agg_customer_24h():
    """
    Computes 24-hour tumbling window aggregations per customer.

    Captures intra-day spending patterns. A sudden spike in daily
    volume compared to the customer's historical average is a key
    fraud signal.
    """
    return (
        spark.readStream
             .table(silver_events_source)
             .withWatermark("timestamp", watermark_delay)
             .groupBy(
                 col("customer_id"),
                 window(col("timestamp"), window_24h)
             )
             .agg(
                 count("transaction_id").alias("count_tx_24h"),
                 sum("amount").alias("sum_amount_24h"),
                 avg("amount").alias("avg_amount_24h"),
                 max("amount").alias("max_amount_24h"),
                 approx_count_distinct("merchant_id").alias("distinct_merchants_24h"),
                 approx_count_distinct("merchant_country").alias("distinct_countries_24h"),

                 # Count TOR or VPN connections: a strong fraud indicator
                 sum(
                     when(col("is_tor_or_vpn") == 1, 1).otherwise(0)
                 ).alias("count_tor_vpn_24h"),

                 # Count failed 3DS challenges: repeated failures suggest
                 # a fraudster testing cards
                 sum(
                     when(col("three_ds_result") == "FAILED", 1).otherwise(0)
                 ).alias("count_3ds_failed_24h"),
             )
             .select(
                 col("customer_id"),
                 col("window.end").alias("window_end"),
                 col("count_tx_24h"),
                 col("sum_amount_24h"),
                 col("avg_amount_24h"),
                 col("max_amount_24h"),
                 col("distinct_merchants_24h"),
                 col("distinct_countries_24h"),
                 col("count_tor_vpn_24h"),
                 col("count_3ds_failed_24h"),
             )
    )


@dp.view(name = agg_7d_view_name)
def vw_agg_customer_7d():
    """
    Computes 7-day tumbling window aggregations per customer.

    Captures weekly behavioral patterns. Fraudsters often probe
    multiple merchants and countries within a short multi-day window
    before executing a large purchase.
    """
    return (
        spark.readStream
             .table(silver_events_source)
             .withWatermark("timestamp", watermark_delay)
             .groupBy(
                 col("customer_id"),
                 window(col("timestamp"), window_7d)
             )
             .agg(
                 count("transaction_id").alias("count_tx_7d"),
                 sum("amount").alias("sum_amount_7d"),
                 avg("amount").alias("avg_amount_7d"),
                 approx_count_distinct("merchant_id").alias("distinct_merchants_7d"),
                 approx_count_distinct("merchant_country").alias("distinct_countries_7d"),
                 approx_count_distinct("device_type").alias("distinct_devices_7d"),
             )
             .select(
                 col("customer_id"),
                 col("window.end").alias("window_end"),
                 col("count_tx_7d"),
                 col("sum_amount_7d"),
                 col("avg_amount_7d"),
                 col("distinct_merchants_7d"),
                 col("distinct_countries_7d"),
                 col("distinct_devices_7d"),
             )
    )


@dp.view(name = agg_30d_view_name)
def vw_agg_customer_30d():
    """
    Computes 30-day tumbling window aggregations per customer.

    Captures the medium-term behavioral baseline. These features
    are essential for computing ratios like `amount_vs_avg_spend_ratio`
    (current transaction amount divided by the 30-day average),
    which is one of the strongest fraud signals available.
    """
    return (
        spark.readStream
             .table(silver_events_source)
             .withWatermark("timestamp", watermark_delay)
             .groupBy(
                 col("customer_id"),
                 window(col("timestamp"), window_30d)
             )
             .agg(
                 count("transaction_id").alias("count_tx_30d"),
                 sum("amount").alias("sum_amount_30d"),
                 avg("amount").alias("avg_amount_30d"),
                 max("amount").alias("max_amount_30d"),
                 min("amount").alias("min_amount_30d"),
                 approx_count_distinct("merchant_id").alias("distinct_merchants_30d"),
                 approx_count_distinct("merchant_country").alias("distinct_countries_30d"),

                 # Count confirmed frauds in the last 30 days for this customer.
                 # A customer with recent confirmed fraud is at much higher risk.
                 sum(
                     when(col("is_fraud") == 1, 1).otherwise(0)
                 ).alias("num_fraud_confirmed_30d"),
             )
             .select(
                 col("customer_id"),
                 col("window.end").alias("window_end"),
                 col("count_tx_30d"),
                 col("sum_amount_30d"),
                 col("avg_amount_30d"),
                 col("max_amount_30d"),
                 col("min_amount_30d"),
                 col("distinct_merchants_30d"),
                 col("distinct_countries_30d"),
                 col("num_fraud_confirmed_30d"),
             )
    )


###############################################################################
# Final feature table: join all windows into a single row per customer
###############################################################################

gold_aggregations_table_name = "gold_customer_aggregations"
gold_aggregations_comment = """
This managed table acts as the **behavioral feature table** in the `Feature
Store`. It consolidates time-windowed aggregations per customer across four
temporal resolutions (1h, 24h, 7d, 30d) into a single row per customer.

It is keyed by `customer_id` and is designed to be published to the `Online
Store` for low-latency lookups during real-time inference. When a new
transaction arrives, the model serving layer queries this table
by `customer_id` to retrieve the customer's latest behavioral signals.
"""
gold_profile_table_properties = {"delta.enableChangeDataFeed": "true"}
gold_aggregations_schema = """
    customer_id STRING NOT NULL,
    window_end TIMESTAMP NOT NULL,
    count_tx_1h BIGINT,
    sum_amount_1h DOUBLE,
    avg_amount_1h DOUBLE,
    distinct_merchants_1h BIGINT,
    count_cross_border_1h BIGINT,
    count_tx_24h BIGINT,
    sum_amount_24h DOUBLE,
    avg_amount_24h DOUBLE,
    max_amount_24h DOUBLE,
    distinct_merchants_24h BIGINT,
    distinct_countries_24h BIGINT,
    count_tor_vpn_24h BIGINT,
    count_3ds_failed_24h BIGINT,
    count_tx_7d BIGINT,
    sum_amount_7d DOUBLE,
    avg_amount_7d DOUBLE,
    distinct_merchants_7d BIGINT,
    distinct_countries_7d BIGINT,
    distinct_devices_7d BIGINT,
    count_tx_30d BIGINT,
    sum_amount_30d DOUBLE,
    avg_amount_30d DOUBLE,
    max_amount_30d DOUBLE,
    min_amount_30d DOUBLE,
    distinct_merchants_30d BIGINT,
    distinct_countries_30d BIGINT,
    num_fraud_confirmed_30d BIGINT,
    amount_vs_avg_spend_ratio_30d DOUBLE,
    CONSTRAINT gold_customer_aggregations_pk PRIMARY KEY (customer_id, window_end TIMESERIES)
"""

gold_aggregations_flow_name = "flow_gold_customer_aggregations"

dp.create_streaming_table(
    name = gold_aggregations_table_name,
    comment = gold_aggregations_comment,
    table_properties = gold_profile_table_properties,
    schema = gold_aggregations_schema
)


@dp.append_flow(target = gold_aggregations_table_name, name = gold_aggregations_flow_name)
def gold_customer_aggregations():
    """
    Joins the four window views into a single row per customer per window end.

    We join on both `customer_id` and `window_end` to ensure that features
    from different window sizes are aligned to the same point in time.
    """
    df_1h  = spark.readStream.table(agg_1h_view_name)
    df_24h = spark.readStream.table(agg_24h_view_name)
    df_7d = spark.readStream.table(agg_7d_view_name)
    df_30d = spark.readStream.table(agg_30d_view_name)

    join_keys = ["customer_id", "window_end"]

    df_joined = (
        df_1h
        .join(df_24h, on = join_keys, how = "inner")
        .join(df_7d, on = join_keys, how = "inner")
        .join(df_30d, on = join_keys, how = "inner")
    )

    # Derived ratio feature: how does the customer's 24 hours spend compare
    # to their 30-day average? A high ratio is a strong fraud signal.
    # We add a small epsilon to avoid division by zero for new customers.
    df_final = df_joined.withColumn(
        "amount_vs_avg_spend_ratio_30d",
        col("sum_amount_24h") / (col("avg_amount_30d") + lit(EPSILON))
    )

    return df_final