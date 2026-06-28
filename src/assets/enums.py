import enum

class AssetType(enum.Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP_ADDRESS = "ip_address"
    SERVICE = "service"
    CERTIFICATE = "certificate"
    TECHNOLOGY = "technology"

class AssetStatus(enum.Enum):
    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"

