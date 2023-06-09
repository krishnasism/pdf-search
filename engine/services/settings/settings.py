import logging


class Settings:
    _instance = None
    aws_access_key = ""
    aws_secret = ""
    aws_region = ""
    no_sql_provider = ""
    document_db_provider = ""
    document_table_name = ""
    parsing_api_key = ""
    buckets_list = ""
    aws_search_table_name = ""
    scan_bucket = ""
    elastic_search_index = ""
    elastic_search_host = ""
    elastic_search_port = ""
    elastic_search_api_key = ""
    search_document_db = False
    search_elastic_search = False

    def __init__(self):
        if Settings._instance is not None:
            raise Exception("Settings class is a singleton!")
        else:
            Settings._instance = self

    def update_settings(self, settings: dict):
        if len(settings) == 0:
            logging.error("[Queue - Settings] Settings not yet set, passing...")
            return None
        # TODO : Remove dup settings
        self.aws_access_key = settings["awsAccessKey"]
        self.aws_secret = settings["awsSecret"]
        self.aws_region = settings["awsRegion"]
        self.no_sql_provider = settings["noSqlProvider"]
        self.document_db_provider = settings["noSqlProvider"]
        self.document_table_name = settings["documentTableName"]
        self.aws_search_table_name = settings["documentTableName"]
        self.parsing_api_key = settings["parsingApiKey"]
        self.buckets_list = settings["bucketsList"]
        self.scan_bucket = settings["scanBucket"]
        self.elastic_search_index = settings["elasticSearchIndex"]
        self.elastic_search_host = settings["elasticSearchHost"]
        self.elastic_search_port = settings["elasticSearchPort"]
        self.elastic_search_api_key = settings["elasticSearchApiKey"]
        self.search_elastic_search = settings.get("searchElasticSearch")
        self.search_document_db = settings.get("searchDocumentDb")

    @classmethod
    def get_settings(cls):
        if cls._instance is None:
            cls._instance = Settings()
        return cls._instance
