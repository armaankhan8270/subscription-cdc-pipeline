-- ============================================================================
-- 01_setup.sql — Warehouse, Database, Schemas, Stage, File Format
-- ============================================================================

-- Warehouse for compute
CREATE WAREHOUSE IF NOT EXISTS SUBSTRACK_WH
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Database
CREATE DATABASE IF NOT EXISTS SUBSTRACK_DB;

-- Schemas (medallion: RAW -> STAGING -> MARTS, plus SNAPSHOTS)
CREATE SCHEMA IF NOT EXISTS SUBSTRACK_DB.RAW;
CREATE SCHEMA IF NOT EXISTS SUBSTRACK_DB.STAGING;
CREATE SCHEMA IF NOT EXISTS SUBSTRACK_DB.MARTS;
CREATE SCHEMA IF NOT EXISTS SUBSTRACK_DB.SNAPSHOTS;

-- Internal stage (landing zone for CSV files)
CREATE STAGE IF NOT EXISTS SUBSTRACK_DB.RAW.RAW_STAGE;

-- CSV file format
CREATE FILE FORMAT IF NOT EXISTS SUBSTRACK_DB.RAW.CSV_FORMAT
  TYPE = CSV
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('NULL', 'null', '')
  EMPTY_FIELD_AS_NULL = TRUE;
