"""
Shared utilities for the credit card fraud detection project.
"""


###############################################################################
# Imports
###############################################################################

from datetime import datetime, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta
from pyspark.sql import functions as F


###############################################################################
# Configuration
###############################################################################

CATALOG = "workspace"
DATABASE = "credit_card_fraud"
TRAINING_TABLE = f"{CATALOG}.{DATABASE}.gold_fraud_training_dataset"

LABEL_COLUMN = "is_fraud"
CLASS_WEIGHT_COLUMN = "class_weight"
FEATURES_COLUMN = "features_scaled"
DATE_COLUMN = "timestamp"

# Temporal split window sizes in months.
# Test window: everything added after ml.data_previous_max_date of the previous cycle; duration varies depending on when retraining is triggered.
# Validation window: VALIDATION_WINDOW_MONTHS months immediately before the test window.
# Training window: TRAINING_WINDOW_MONTHS immediately before the validation window; capped to avoid stale fraud patterns degrading performance.
# On the first version of the table, the split falls back to the defaults.
TRAINING_WINDOW_MONTHS = 36
VALIDATION_WINDOW_MONTHS = 12

catalog = CATALOG
database = DATABASE
training_table = TRAINING_TABLE
label_column = LABEL_COLUMN
class_weight_column = CLASS_WEIGHT_COLUMN
features_column = FEATURES_COLUMN
date_column = DATE_COLUMN

# Random seed: shared so run tags built in both notebooks are identical
seed = 45127

uc_volume_path = Path("/") / "Volumes" / CATALOG / DATABASE / "ml_artifacts"


###############################################################################
# Raw data load
###############################################################################

df_raw = spark.table(training_table)

print(f"Total rows: {df_raw.count():,}")
print(f"Total columns: {len(df_raw.columns)}")
print()


###############################################################################
# Temporal split and inverse-frequency class weights
###############################################################################

# Read the table properties of the latest version to determine the split strategy.
# ml.delta_semantic_version drives the branching logic: version 0 uses the fixed
# seminar splits, while any subsequent version uses the rolling window anchored
# to ml.data_previous_max_date persisted by the data generation notebook.
properties_df = spark.sql(f"SHOW TBLPROPERTIES {training_table}")
semantic_version_row = properties_df.filter("key = 'ml.delta_semantic_version'").first()
delta_semantic_version = int(semantic_version_row["value"]) if semantic_version_row else 0

if delta_semantic_version == 0:
    # First version of the table: training from 2020 to 2022, validation 2023, and test 2024 (reserved)
    train_end = datetime(2022, 12, 31)
    validation_end = datetime(2023, 12, 31)
else:
    # Subsequent versions: rolling window anchored to the previous cycle maximum date.
    # ml.data_previous_max_date is the maximum timestamp of the dataset before the last
    # overwrite, persisted in the table properties by the data generation notebook.
    # Everything after that date in the current table becomes the test window.
    # Validation is the VALIDATION_WINDOW_MONTHS immediately before that cutoff.
    # Training is the TRAINING_WINDOW_MONTHS immediately before validation.
    previous_max_date_row = properties_df.filter("key = 'ml.data_previous_max_date'").first()
    validation_end = datetime.strptime(previous_max_date_row["value"], "%Y-%m-%d")
    train_end = validation_end - relativedelta(months = VALIDATION_WINDOW_MONTHS)

train_start = train_end - relativedelta(months = TRAINING_WINDOW_MONTHS)

train_start_date = train_start.strftime("%Y-%m-%d")
train_end_date = train_end.strftime("%Y-%m-%d")
validation_start_date = (train_end + timedelta(days=1)).strftime("%Y-%m-%d")
validation_end_date = validation_end.strftime("%Y-%m-%d")
test_start_date = (validation_end + timedelta(days=1)).strftime("%Y-%m-%d")
test_end_date = df_raw.agg(
    F.max(F.col(date_column)).alias("max_date")
).collect()[0]["max_date"].strftime("%Y-%m-%d")

train_df = df_raw.filter(
    (F.col(date_column) >= train_start_date) & (F.col(date_column) <= train_end_date)
)
validation_df = df_raw.filter(
    (F.col(date_column) >= validation_start_date) & (F.col(date_column) <= validation_end_date)
)

print(f"Semantic version: {delta_semantic_version}")
print(f"Train period: {train_start_date} → {train_end_date}")
print(f"Validation period: {validation_start_date} → {validation_end_date}")
print(f"Test period: {test_start_date} → {test_end_date} (reserved)")
print()
print(f"Train rows: {train_df.count():,}")
print(f"Validation rows: {validation_df.count():,}")
print()

n_total = train_df.count()
n_fraud = train_df.filter(F.col(label_column) == 1).count()
n_legit = n_total - n_fraud

pct_fraud = 100 * n_fraud / n_total
pct_legit = 100 * n_legit / n_total

weight_fraud = n_total / (2.0 * n_fraud)
weight_legit = n_total / (2.0 * n_legit)

train_weighted = train_df.withColumn(
    class_weight_column,
    F.when(F.col(label_column) == 1.0, weight_fraud).otherwise(weight_legit)
)

print(f"Fraud: {n_fraud:,} ({pct_fraud:.2f}%), weight = {weight_fraud:.2f}")
print(f"Legit: {n_legit:,} ({pct_legit:.2f}%), weight = {weight_legit:.2f}")
print()


###############################################################################
# Column classification
###############################################################################

# Type sets used to route each field to the correct pipeline stage
numeric_types = {"IntegerType", "LongType", "FloatType", "DoubleType", "DecimalType"}
categorical_types = {"StringType"}

# Binary security flags stored as integers: treated as boolean features
binary_flag_columns = [
    "cross_border",
    "is_tor_or_vpn",
    "ip_country_match",
    "device_fingerprint_known",
    "two_fa_enabled",
    "email_verified",
    "phone_verified"
]

# Integer column that is semantically categorical
integer_categorical_columns = ["mcc_code"]

# The label is never included in the feature vector to avoid data leakage
exclude_columns = [label_column]

numeric_columns = []
boolean_columns = []
categorical_columns = []

for field in df_raw.schema.fields:
    column_name = field.name
    type_name = type(field.dataType).__name__
    if column_name in exclude_columns:
        continue
    if column_name in binary_flag_columns:
        boolean_columns.append(column_name)
    elif column_name in integer_categorical_columns:
        categorical_columns.append(column_name)
    elif type_name in numeric_types:
        numeric_columns.append(column_name)
    elif type_name in categorical_types:
        categorical_columns.append(column_name)

print(f"Numeric ({len(numeric_columns)}): {numeric_columns}")
print(f"Boolean ({len(boolean_columns)}): {boolean_columns}")
print(f"Categorical ({len(categorical_columns)}): {categorical_columns}")
print()


###############################################################################
# Preprocessing configuration
###############################################################################


###############################################################################
# Stage 1: drop
###############################################################################

# High-cardinality identifiers and columns redundant with others
columns_to_drop = ["customer_id", "transaction_id", "merchant_id", "mcc_code"]
drop_statement = "SELECT * EXCEPT ({}) FROM __THIS__".format(
    ", ".join(columns_to_drop)
)

# Remove dropped columns from the type lists to avoid downstream pipeline errors
numeric_columns = [column for column in numeric_columns if column not in columns_to_drop]
boolean_columns = [column for column in boolean_columns if column not in columns_to_drop]
categorical_columns = [column for column in categorical_columns if column not in columns_to_drop]


###############################################################################
# Stage 2: imputation
###############################################################################

# Count and sum aggregations initialize to 0 on empty windows (no imputation needed).
# Mean, maximum and minimum aggregations arrive as null on empty windows (median imputation needed).
agg_zero_prefixes = (
    "count_",
    "sum_",
    "count_cross_border_",
    "count_tor_vpn_",
    "count_3ds_failed_",
    "num_fraud_",
    "spend_",
    "distinct_"
)
agg_null_prefixes = ("avg_", "max_amount", "min_amount")

agg_zero_columns = [column for column in numeric_columns if column.startswith(agg_zero_prefixes)]
agg_null_columns = [column for column in numeric_columns if column.startswith(agg_null_prefixes)]
profile_numeric_columns = [
    column for column in numeric_columns
    if not column.startswith(agg_zero_prefixes) and not column.startswith(agg_null_prefixes)
]

imputer_input_columns = profile_numeric_columns + agg_null_columns
imputer_output_columns = [f"{column}_imp" for column in imputer_input_columns]


###############################################################################
# Stage 3: boolean cast
###############################################################################

# COALESCE handles nulls inline: a missing security flag is treated as disabled (0.0)
boolean_cast_expressions = ", ".join([
    f"COALESCE(CAST({c} AS DOUBLE), 0.0) AS {c}_dbl"
    for c in boolean_columns
])
boolean_output_columns = [f"{column}_dbl" for column in boolean_columns]
boolean_statement = f"SELECT *, {boolean_cast_expressions} FROM __THIS__"


###############################################################################
# Stage 4: feature engineering
###############################################################################

# Only features computable from the current transaction at inference time.
# Features requiring customer history must come from the feature store.
feature_engineering_statement = (
    "SELECT *, "
    "CAST((is_tor_or_vpn = 1 OR three_ds_result = 'FAILED') AS INT) AS is_high_risk_method, "
    "CAST((ip_country_match = 0) AS INT) AS is_foreign_ip, "
    "CAST((device_fingerprint_known = 0) AS INT) AS is_unrecognized_device, "
    "LOG(amount + 1) AS amount_log, "
    "CAST((cross_border = 1 AND payment_method = 'online') AS INT) AS is_cross_border_online "
    "FROM __THIS__"
)
engineered_columns = [
    "is_high_risk_method",
    "is_foreign_ip",
    "is_unrecognized_device",
    "amount_log",
    "is_cross_border_online"
]


###############################################################################
# Stages 5 and 6: categorical encoding
###############################################################################

string_indexer_input_columns = categorical_columns
string_indexer_output_columns = [f"{column}_idx" for column in categorical_columns]

ohe_input_columns = string_indexer_output_columns
ohe_output_columns = [f"{column}_ohe" for column in categorical_columns]


###############################################################################
# Stage 7: vector assembly
###############################################################################

assembler_input_columns = (
    imputer_output_columns
    + agg_zero_columns
    + boolean_output_columns
    + ohe_output_columns
    + engineered_columns
)
assembler_output_column = "features"


###############################################################################
# Stages 8 and 9: variance threshold selection and standard scaling
###############################################################################

var_selector_input_column = assembler_output_column
var_selector_output_column = "features_var_filtered"
scaler_input_column = var_selector_output_column
scaler_output_column = features_column

print(f"Assembler inputs: {assembler_input_columns}")
print()

print("Utils script loaded successfully.")