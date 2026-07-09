with open("ai_gateway/tests/test_fallback.py", "r") as f:
    content = f.read()

old = """    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        self.last_context = context
        if self.call_count >= len(self.sequence):
            raise NoProviderAvailableException("No more providers")
        
        provider_name = self.sequence[self.call_count]
        self.call_count += 1"""

new = """    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        self.last_context = context
        index = self.call_count
        self.call_count += 1
        if index >= len(self.sequence):
            raise NoProviderAvailableException("No more providers")
        
        provider_name = self.sequence[index]"""

if old in content:
    content = content.replace(old, new)
    with open("ai_gateway/tests/test_fallback.py", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Pattern not found")
