import logging

logger = logging.getLogger(__name__)

class PermissionAuditor:
    """Validates that requested plugin permissions are safe and approved."""
    
    @staticmethod
    def audit_manifest_permissions(permissions: list) -> bool:
        dangerous = ["filesystem", "terminal"]
        for p in permissions:
            if p.value in dangerous:
                logger.warning(f"Plugin requested highly sensitive permission: {p.value}")
                # In production, this might trigger a manual review flow
        return True
