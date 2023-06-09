CREATE TABLE IF NOT EXISTS settings (
	id VARCHAR PRIMARY KEY,
	user_email VARCHAR unique not null,
	aws_access_key VARCHAR,
	aws_secret VARCHAR,
	aws_region VARCHAR,
	no_sql_provider VARCHAR,
	document_table_name VARCHAR,
	parsing_api_key VARCHAR,
	buckets_list VARCHAR,
	scan_bucket VARCHAR,
	elastic_search_index VARCHAR,
	elastic_search_host VARCHAR,
	elastic_search_port VARCHAR,
	elastic_search_api_key VARCHAR,
	search_document_db BOOLEAN,
	search_elastic_search BOOLEAN
);
