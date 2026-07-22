import logging
from friday.core.kernel.service_registry import ServiceRegistry
from friday.core.kernel.dependency_graph import DependencyGraph
from friday.core.kernel.lifecycle import LifecycleCoordinator
from friday.core.kernel.config_manager import ConfigManager
from friday.core.kernel.security_manager import SecurityManager
from friday.core.kernel.capability_manager import CapabilityManager
from friday.core.kernel.plugin_loader import PluginLoader

logger = logging.getLogger(__name__)

class FridayKernel:
    """The central AI Kernel that owns, registers, and controls all OS subsystems."""
    def __init__(self, plugin_dir: str = "./plugins"):
        self.services = ServiceRegistry()
        self.dependencies = DependencyGraph()
        self.lifecycle = LifecycleCoordinator()
        self.config = ConfigManager()
        self.security = SecurityManager()
        self.capabilities = CapabilityManager()
        self.plugins = PluginLoader(plugin_dir)

        # Register self
        self.services.register(FridayKernel, self)

        # Register managers
        self.services.register(ServiceRegistry, self.services)
        self.services.register(DependencyGraph, self.dependencies)
        self.services.register(LifecycleCoordinator, self.lifecycle)
        self.services.register(ConfigManager, self.config)
        self.services.register(SecurityManager, self.security)
        self.services.register(CapabilityManager, self.capabilities)
        self.services.register(PluginLoader, self.plugins)

    async def bootstrap(self) -> None:
        """Loads configuration and boots up registered services in dependency order."""
        logger.info("Bootstrapping Friday Kernel...")
        self.config.load()
        
        # Resolve order
        order = self.dependencies.resolve_bootstrap_order()
        self.lifecycle.set_bootstrap_order(order)
        
        await self.lifecycle.startup()
        logger.info("Kernel bootstrap complete. Systems are ONLINE.")

    async def shutdown(self) -> None:
        logger.info("Shutting down Friday Kernel...")
        await self.lifecycle.shutdown()
        logger.info("Kernel offline.")
