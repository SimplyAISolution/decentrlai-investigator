from enum import StrEnum

class CollectorKind(StrEnum):
    WEB_SEARCH = "web_search"
    NEWS = "news"
    HTTP = "http"
    BROWSER = "browser"
    RSS = "rss"
    RDAP = "rdap"
    DNS = "dns"
    PUBLIC_DATA = "public_data"

class SourceType(StrEnum):
    WEB_PAGE = "web_page"
    SEARCH_RESULT = "search_result"
    NEWS_ARTICLE = "news_article"
    RSS_ITEM = "rss_item"
    API_RESPONSE = "api_response"
    RDAP_RECORD = "rdap_record"
    DNS_RECORD = "dns_record"
    DOCUMENT = "document"
    UNKNOWN = "unknown"
