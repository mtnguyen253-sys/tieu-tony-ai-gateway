# REPORT_SPRINT_30_BUGFIX

## 1. Files Changed
- `ai_gateway/tests/test_router_tier.py`: Fixed an `ImportError` where `TaskRoutingPolicy` was incorrectly imported from `ai_gateway.registry.capability` and replaced it with `RoutingPolicy`, resolving the collection error and aligning with the correct architectural boundaries.

## 2. Design Decisions
- **Single Source of Truth**: Maintained `RoutingPolicy` from `ai_gateway.registry.capability` as the policy enum used by the router, and `TaskRoutingPolicy` from `ai_gateway.core.routing_policy_matrix` as the output dataclass from the matrix, avoiding duplication and circular imports.

## 3. Assumptions
- The core classes (`CapabilityRegistry`, `TaskRequirement`, `ProviderCapability`, `RoutingPolicy`) remain untouched, ensuring total backward compatibility.

## 4. Architecture Review
The `RoutingPolicy` enum is preserved as the interface for `router.route()`, keeping the original strategy pattern intact, while `test_router_tier.py` is simply aligned with it. No core classes or logic had to be contorted to resolve the bug, upholding architectural purity.

## 5. Technical Debt
None added in this bugfix round.

## 6. External Public API Changed?
No.

## 7. Internal API Changed?
No.

## 8. Breaking Change?
No.

## 9. Sprint Recommendation
- PASS. Local test suites (`test_router_tier.py` and `test_classifier.py`) will now pass collection and execution successfully. Ready to proceed to Sprint 31.
