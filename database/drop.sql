/*
Overview
This SQL script is used to remove existing database objects from the Campus ERP schema. It ensures that outdated or conflicting tables, constraints, and relationships are dropped before recreating or altering the schema. This file is typically run during reset operations or when redeploying the database from scratch.
*/
drop database [campus];
