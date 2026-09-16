# This file will contain the service interfaces and implementations.

class ServiceInterface:
    def operation(self):
        pass

class ExampleService(ServiceInterface):
    def operation(self):
        print("Service operation executed.")