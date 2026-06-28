import enum

class RelationshipsType(enum.Enum):
    SUBDOMAIN_TO_DOMAIN = "subdomain_to_domain"

    SERVICE_TO_IP = "service_to_ip"

    # avoid duplicate entries in <--> bidirectional realationship
    IP_TO_SUBDOMAIN = "ip_to_subdomain"  
    # SUBDOMAIN_TO_IP = "subdomain_to_ip"

    CERTIFICATE_TO_DOMAIN = "certificate_to_domain"
    CERTIFICATE_TO_SUBDOMAIN = "certificate_to_subdomain"
    
    TECHNOLOGY_TO_SUBDOMAIN = "technology_to_subdomain"
    TECHNOLOGY_TO_SERVICE = "technology_to_service"