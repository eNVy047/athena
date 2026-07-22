import pytest
from friday.core.di import Container

def test_di_container_resolution():
    container = Container()
    
    class Interface:
        pass
        
    class Implementation(Interface):
        pass
        
    impl = Implementation()
    container.register(Interface, impl)
    
    resolved = container.resolve(Interface)
    assert resolved == impl
