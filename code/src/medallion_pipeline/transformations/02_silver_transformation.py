"""
The purpose of this script is to build the second layer of our `Medallion`
architecture. It takes the raw information from the `Bronze` layer, cleans it
using declarative data quality rules (`Expectations`), manages customer history
tracking via `AUTO CDC`, and merges the streams using `Watermarks` to create an
enriched, unified dataset ready for machine learning point-in-time correctness.
"""


###############################################################################
# Imports
###############################################################################

import pyspark.pipelines as dp

# Functions for data manipulation and constraints
from pyspark.sql.functions import coalesce, col, expr, to_timestamp

# Centralized data quality rules repository
from rules import get_rules


###############################################################################
# Customer dimension (quarantine & `AUTO CDC`)
###############################################################################

cust_quarantine_table_name = "silver_quarantine_customers"
cust_quarantine_comment = """
This managed table acts as the **`Dead Letter Queue` (`DLQ`)** for customer
profiles within the **`silver`** layer. It captures all records from
`bronze_customers` that failed to pass the established business and data
quality rules (`Expectations`).
"""

cust_bronze_source = "bronze_customers"
cust_tmp_eval_name = "tmp_eval_customers"  # Temporary table for rule evaluation
cust_clean_view_name = "vw_clean_customers"  # View name for the valid records
cust_quarantine_flow_name = "flow_quarantine_cust"

# Extract the constraints from the data quality rules
# dictionary to build a dynamic quarantine expression.
cust_rules_dict = get_rules("customers")
cust_rule_constraints = cust_rules_dict.values()
cust_combined_rules = " AND ".join(cust_rule_constraints)
cust_quarantine_expr = "NOT " + "(" + cust_combined_rules + ")"


# We create a temporary table to evaluate all data quality expectations
# in a single pass. It acts as an in-memory routing hub for the full
# snapshot: it reads the raw data and attaches a boolean flag to separate
# valid and invalid records, without permanently storing this intermediate
# evaluation state to disk.
@dp.table(name = cust_tmp_eval_name, temporary = True)
@dp.expect_all(cust_rules_dict)
def eval_customers():
    """
    Reads raw customer data (full snapshot), imputes missing sequence dates,
    and evaluates data quality expectations.

    Adds a boolean flag (`is_quarantined`) to identify records
    that fail rules.
    """
    df_raw = (
        spark.readStream
             # Instructs the streaming reader to process the full snapshot (overwrite) 
             # as new data, enabling the AUTO CDC engine to calculate the actual changes.
             .option("ignoreChanges", "true")
             .table(cust_bronze_source)
    )

    # Impute missing update timestamps with the join date to ensure
    # new customers have a valid sequencing key for the AUTO CDC engine.
    df_imputed = df_raw.withColumn("customer_updated_at", coalesce(col("customer_updated_at"), col("join_date")))

    df_evaluated = df_imputed.withColumn("is_quarantined", expr(cust_quarantine_expr))

    return df_evaluated


@dp.table(name = cust_quarantine_table_name, comment = cust_quarantine_comment)
def quarantine_customers():
    """
    Overwrites the `DLQ` with the current snapshot of invalid customer records
    (`is_quarantined = true`).
    """
    df_evaluated = spark.read.table(cust_tmp_eval_name)
    df_invalid = df_evaluated.filter("is_quarantined = true").drop("is_quarantined")

    return df_invalid


# We use a view to define the "happy path" for our pipeline.
# It filters the evaluated snapshot to retain only the valid
# records and strips away the temporary routing flag, providing
# a pristine dataset for the downstream process to consume.
@dp.view(name = cust_clean_view_name)
def clean_customers():
    """
    Provides a clean, filtered snapshot of valid customers
    (`is_quarantined = false`).

    This view acts as the foundational source for the `AUTO CDC` flow defined
    below.
    """
    df_evaluated = spark.readStream.table(cust_tmp_eval_name)
    df_valid = df_evaluated.filter("is_quarantined = false").drop("is_quarantined")

    return df_valid


customers_history_table_name  = "silver_customers_history"
customers_history_comment = """
This managed table belongs to the **`silver`** layer and acts as the historical
dimension for customer profiles. It is continuously maintained by a declarative
streaming pipeline using **`AUTO CDC`** to implement a `Slowly Changing Dimension`
(**`SCD Type 2`**) strategy. It automatically tracks profile updates over time by
managing `__START_AT` and `__END_AT` validity intervals, providing a clean,
point-in-time accurate foundation required for exact feature enrichment in
downstream machine learning models.
"""

cdc_source = cust_clean_view_name  # Source view containing the valid incoming updates
cdc_keys = ["customer_id"]  # List of columns that form the primary key
cdc_sequence_by = col("customer_updated_at")  # Expression defining the logical time of the event
cdc_except_columns = ["ingestion_timestamp", "source_file"]  # List of columns to exclude
cdc_scd_type = "2"  # Keeps the full history

dp.create_streaming_table(
    name = customers_history_table_name,
    comment = customers_history_comment
)


# This declares the "apply changes" logic. It automatically merges the clean
# incoming updates into the target history table based on the primary key.
# It uses customer_updated_at to handle out-of-order data properly and
# automatically generates and maintains the SCD Type 2 validity intervals.
dp.create_auto_cdc_flow(
    target = customers_history_table_name,
    source = cdc_source,
    keys = cdc_keys,
    sequence_by = cdc_sequence_by,
    except_column_list = cdc_except_columns,
    stored_as_scd_type = cdc_scd_type
)


###############################################################################
# Events: transactions (quarantine & typing)
###############################################################################

tx_quarantine_table_name  = "silver_quarantine_tx"
tx_quarantine_comment = """
This managed table acts as the **`Dead Letter Queue` (`DLQ`)** for credit
card transactions within the **`silver`** layer. It captures all events
from `bronze_transactions` that failed to pass the established business
and data quality rules (`Expectations`). It preserves the invalid records
for auditing and troubleshooting by the `Data Governance` team without
halting the main pipeline.
"""

tx_bronze_source = "bronze_transactions"
tx_tmp_eval_name = "tmp_eval_transactions"
tx_clean_view_name = "vw_clean_transactions"
tx_quarantine_flow_name = "flow_quarantine_tx"

tx_rule_dict = get_rules("transactions")
tx_rule_constraints = tx_rule_dict.values()
tx_combined_rules = " AND ".join(tx_rule_constraints)
tx_quarantine_expr = "NOT " + "(" + tx_combined_rules + ")"

dp.create_streaming_table(
    name = tx_quarantine_table_name,
    comment = tx_quarantine_comment
)


@dp.table(name = tx_tmp_eval_name, temporary = True)
@dp.expect_all(tx_rule_dict)
def eval_transactions():
    """
    Reads raw transactions, applies type casting to dates, and evaluates
    data quality rules.

    The `@dp.expect_all` decorator logs the metrics in the user interface.

    We also dynamically add a `boolean` flag (`is_quarantined`) to route
    records later.
    """
    df_raw = spark.readStream.table(tx_bronze_source)
    df_typed = df_raw.withColumn("timestamp", to_timestamp(col("timestamp")))
    df_evaluated = df_typed.withColumn("is_quarantined", expr(tx_quarantine_expr))

    return df_evaluated


@dp.append_flow(target = tx_quarantine_table_name, name = tx_quarantine_flow_name)
def quarantine_transactions():
    """
    Filters the evaluated transactions and appends **only** the invalid ones
    (`is_quarantined = true`) to the physical `DLQ` table.

    We drop the temporary flag before writing.
    """
    df_evaluated = spark.readStream.table(tx_tmp_eval_name)
    df_invalid = df_evaluated.filter("is_quarantined = true").drop("is_quarantined")

    return df_invalid


@dp.view(name = tx_clean_view_name)
def clean_transactions():
    """
    Provides a clean, filtered stream of valid transactions
    (`is_quarantined = false`).

    This view will be used in the next step to perform the stream-stream
    join with the labels.

    We drop the temporary flag as it is no longer needed.
    """
    df_evaluated = spark.readStream.table(tx_tmp_eval_name)
    df_valid = df_evaluated.filter("is_quarantined = false").drop("is_quarantined")

    return df_valid


###############################################################################
# Events: labels (quarantine & typing)
###############################################################################

lbl_quarantine_table_name = "silver_quarantine_labels"
lbl_quarantine_comment = """
This managed table acts as the **`Dead Letter Queue` (`DLQ`)** for delayed
fraud feedback within the **`silver`** layer. It captures all events from
`bronze_labels` that failed to pass the established business and data quality
rules (`Expectations`). It preserves the invalid records for auditing and
troubleshooting by the `Data Governance` team without halting the main pipeline
or corrupting the stream-stream join downstream.
"""

lbl_bronze_source = "bronze_labels"
lbl_tmp_eval_name = "tmp_eval_labels"
lbl_clean_view_name = "vw_clean_labels"
lbl_quarantine_flow_name = "flow_quarantine_lbl"

lbl_rules_dict = get_rules("labels")
lbl_rule_constraints = lbl_rules_dict.values()
lbl_combined_rules = " AND ".join(lbl_rule_constraints)
lbl_quarantine_expr = "NOT " + "(" + lbl_combined_rules + ")"

dp.create_streaming_table(
    name = lbl_quarantine_table_name,
    comment = lbl_quarantine_comment
)


@dp.table(name = lbl_tmp_eval_name, temporary = True)
@dp.expect_all(lbl_rules_dict)
def eval_labels():
    """
    Reads raw fraud labels, applies type casting to dates, and evaluates data
    quality rules.

    The `@dp.expect_all` decorator logs the metrics in the user interface.
    We also dynamically add a `boolean` flag (`is_quarantined`) to route
    records later.
    """
    df_raw = spark.readStream.table(lbl_bronze_source)
    df_typed = df_raw.withColumn("label_available_date", to_timestamp(col("label_available_date")))
    df_evaluated = df_typed.withColumn("is_quarantined", expr(lbl_quarantine_expr))

    return df_evaluated


@dp.append_flow(target = lbl_quarantine_table_name, name = lbl_quarantine_flow_name)
def quarantine_labels():
    """
    Filters the evaluated labels and appends **only** the invalid ones
    (`is_quarantined = true`) to the physical `DLQ` table.

    We drop the temporary flag before writing.
    """
    df_evaluated = spark.readStream.table(lbl_tmp_eval_name)
    df_invalid = df_evaluated.filter("is_quarantined = true").drop("is_quarantined")

    return df_invalid


@dp.view(name = lbl_clean_view_name)
def clean_labels():
    """
    Provides a clean, filtered stream of valid labels
    (`is_quarantined = false`).

    This view will be consumed in the stream-stream join to enrich transactions
    with their confirmed fraud outcome within the allowed watermark window.

    We drop the temporary flag as it is no longer needed.
    """
    df_evaluated = spark.readStream.table(lbl_tmp_eval_name)
    df_valid = df_evaluated.filter("is_quarantined = false").drop("is_quarantined")

    return df_valid


###############################################################################
# Enriched events: stream-stream join
###############################################################################

silver_fraud_events_table = "silver_fraud_events"
silver_fraud_events_comment = """
This managed table is the **unified core** of the **`silver`** layer. It
contains enriched credit card transactions joined with their corresponding
fraud labels. It uses **`Watermarks`** to handle delayed feedback and state
management, ensuring no data leakage and providing a point-in-time accurate
dataset for machine learning training.
"""

silver_fraud_events_join_flow_name = "flow_silver_events_join"

# Watermarks are crucial for stateful stream processing (like our stream-stream join).
# They tell internal event-time clock how long to keep an event in the state
# memory before dropping it. This automatically prevents out-of-memory errors.

# A transaction can take up to 60 days to receive a confirmed fraud label
# from the bank. We give it a 65-day watermark to be safe and ensure we don't
# drop late-arriving labels. Therefore, Spark will keep a transaction in
# state memory for exactly 65 days. If no label matches it within that window,
# it is safely cleared from memory.
tx_watermark_delay = "65 days"

# Labels might arrive slightly out-of-order due to network issues or system delays.
# We set a 1-day tolerance. This means if a label arrives out-of-order
# regarding its own timestamp, Spark will still process it within a 1-day
# margin before ignoring it.
labels_watermark_delay = "1 day"


@dp.table(name = silver_fraud_events_table, comment = silver_fraud_events_comment)
def silver_events_join():
    """
    Executes a stateful stream-stream left join between clean transactions and labels.

    It applies temporal constraints to manage the state memory efficiently.

    Records without a matching label within the watermark window are retained with
    `is_fraud = null`, representing transactions still awaiting confirmation.
    """
    # Define watermarks for both streams to bound the state size in memory.
    # This tells Spark how late data can arrive, allowing it to safely drop old
    # transactions and labels from the state store once the watermark window passes.
    df_tx  = spark.readStream.table(tx_clean_view_name).withWatermark("timestamp", tx_watermark_delay)
    df_lbl = spark.readStream.table(lbl_clean_view_name).withWatermark("label_available_date", labels_watermark_delay)

    join_on = [
        # Match by transaction identifier
        col("tx.transaction_id") == col("lbl.transaction_id"),

        # Label must arrive after the transaction occurred
        col("lbl.label_available_date") > col("tx.timestamp"),

        # Label must arrive within the allowed 65-day delayed feedback window
        col("lbl.label_available_date") <= col("tx.timestamp") + expr(f"INTERVAL {tx_watermark_delay}")
    ]

    df_joined = df_tx.alias("tx").join(df_lbl.alias("lbl"), on = join_on, how = "leftOuter")

    # Select final columns explicitly to avoid ambiguity and drop pipeline metadata.
    # We keep all transaction fields as the authoritative source and add only the
    # two label fields relevant for downstream machine learning consumption.
    return df_joined.select(
        col("tx.*"),
        col("lbl.is_fraud"),
        col("lbl.label_available_date")
    )
