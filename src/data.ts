export interface FileNode {
  path: string;
  name: string;
  type: 'file' | 'folder';
  content?: string;
  description: string;
  children?: FileNode[];
}

export const PROJECT_FILES: Record<string, { content: string; desc: string }> = {
  'AGENTS.md': {
    content: `# Project Governance (AGENTS.md)

## Mission
Cung cấp một lớp trung gian (Gateway) thông minh, ổn định và linh hoạt để điều phối các yêu cầu tới đa dạng các nhà cung cấp AI.

## Working Rules
- Chỉ làm đúng phạm vi Sprint.
- Không tự refactor.
- Không thay đổi Public API nếu chưa được yêu cầu.
- Không thêm dependency ngoài yêu cầu.
- Không hardcode.
- Ưu tiên Composition hơn Inheritance.
- Ưu tiên Strategy / Adapter Pattern.
- Nếu phát hiện vấn đề kiến trúc thì ghi Technical Debt thay vì tự sửa.

## Sprint Rules
- Chỉ giải quyết một vấn đề.
- Không mở rộng ngoài phạm vi.
- Không thêm feature ngoài yêu cầu.

## Testing & Validation Rules
- Không được tuyên bố "PASS 100%" nếu chưa thực sự chạy được bộ test. Nếu môi trường không có pytest, phải ghi rõ đây là giới hạn của môi trường thay vì kết luận test đã thành công.

## Output Rules
Sau mỗi Sprint phải sinh báo cáo có các mục sau:
- Files Changed
- Design Decisions
- Assumptions
- Architecture Review
- Technical Debt
- External Public API Changed?
- Internal API Changed?
- Breaking Change?
- Sprint Recommendation

## Definition of Done
Sprint chỉ PASS khi:
- pytest PASS (nếu môi trường hỗ trợ)
- Không phá Public API
- Có Report

## Architecture First

Nếu phát hiện vấn đề trong quá trình triển khai:

1. Đánh giá xem đó là Bug, Technical Debt hay Feature Request.
2. Không tự refactor để "tiện tay sửa luôn".
3. Nếu không thuộc phạm vi Sprint:
   - Ghi vào TECH_DEBT.md hoặc báo cáo cuối Sprint.
   - Tiếp tục hoàn thành Sprint hiện tại.

Ưu tiên hoàn thành đúng phạm vi hơn là theo đuổi kiến trúc hoàn hảo.
`,
    desc: 'Project Governance'
  },
  'ROADMAP.md': {
    content: `# Project Roadmap

## Milestone 1 - Core Stable
- Phase 1 - CAP
- Phase 2 - Provider Adapter
- Sprint 8 - Capability Registry
- Sprint 9 - Policy Router
- Sprint 10 - Circuit Breaker
- Sprint 11 - Execution Engine
- Sprint 12 - Execution Orchestrator
- Sprint 13 - Retry Strategy
- Sprint 14 - Fallback Strategy
- Sprint 15 - Execution Refactor
- Sprint 16 - HALF_OPEN Recovery

## Milestone 2 - Public Gateway (Sprint 17)
- Expose OpenAI-compatible REST APIs (/chat/completions, /models, /health, streaming cơ bản).
- API Key management and Authentication.

## Backlog
- Async Migration (Technical Debt TD-003)
- Provider Health Monitor
- Metrics & Telemetry
- Dynamic Score Normalization
`,
    desc: 'Project Roadmap'
  },
  'TECH_DEBT.md': {
    content: `# Technical Debt

## TD-001
- **Title**: Circuit Breaker HALF_OPEN implementation
- **Description**: Trạng thái \`HALF_OPEN\` đã được khai báo nhưng chưa có logic kiểm tra phục hồi tự động (probe requests).
- **Impact**: Provider có thể chuyển thẳng từ OPEN sang CLOSED khi hết thời gian chờ, dễ dẫn đến sập lại hệ thống.
- **Priority**: High
- **Status**: Resolved (Sprint 16)
- **Created**: Sprint 10
- **Recommendation**: Triển khai cơ chế giới hạn 1 request thử nghiệm (probe) khi ở trạng thái HALF_OPEN.

## TD-002
- **Title**: Scoring Engine dynamic normalization
- **Description**: Thuật toán tính điểm sử dụng trọng số cứng mà không chuẩn hoá (normalization) các thang đo khác biệt (ms vs USD).
- **Impact**: Trọng số có thể thiếu chính xác khi các giá trị input có thang đo quá chênh lệch.
- **Priority**: Medium
- **Status**: Open
- **Created**: Sprint 9
- **Recommendation**: Triển khai thuật toán Min-Max Scaling hoặc Softmax.

## TD-003
- **Title**: Synchronous execution pipeline
- **Description**: Toàn bộ luồng thực thi (Router, Engine, Strategy, Orchestrator) đang là thiết kế synchronous.
- **Impact**: Gây blocking thread khi kết nối tới API của provider (I/O bound). Ảnh hưởng nghiêm trọng đến Throughput thực tế.
- **Priority**: Critical
- **Status**: Open
- **Created**: Sprint 11
- **Recommendation**: Refactor toàn bộ core API sử dụng \`async/await\` và \`asyncio\`.

## TD-004
- **Title**: Real Provider Integration
- **Description**: Các Adapter (Gemini, OpenRouter) mới chỉ dừng ở mức API chuẩn (Mock objects). Chưa có kết nối mạng thực tế.
- **Impact**: Không thể gửi request AI thật sự trong production.
- **Priority**: High
- **Status**: Open
- **Created**: Phase 2
- **Recommendation**: Tích hợp các SDK chính thức hoặc triển khai HTTP client gọi REST API trực tiếp.

## TD-005
- **Title**: Observability (Telemetry & Metrics)
- **Description**: Hiện chỉ sử dụng Python \`logging\`. Thiếu các công cụ đo đếm metric như success rate, token usage, timeout count, request latency.
- **Impact**: Rất khó debug và thống kê chi phí, tối ưu hệ thống ở production.
- **Priority**: Medium
- **Status**: Open
- **Created**: Sprint 12.5
- **Recommendation**: Tích hợp metrics gateway như Prometheus hoặc OpenTelemetry.

## TD-006
- **Title**: ExecutionEngine mixed responsibilities
- **Description**: \`ExecutionEngine.execute()\` vừa hỗ trợ tự gọi Router lại vừa cho phép thực thi nếu provider được chỉ định (tiêm qua arguments).
- **Impact**: Gây lẫn lộn trách nhiệm, tiềm ẩn vi phạm SRP nếu logic routing phức tạp lên.
- **Priority**: High
- **Status**: Resolved (Sprint 15)
- **Created**: Sprint 14
- **Recommendation**: Tách dứt điểm logic gọi Router ra khỏi Engine. Engine chỉ tập trung gọi AI.

## TD-007
- **Title**: Hardcoded Retry Limits
- **Description**: Cấu hình của \`FixedRetryStrategy\` đang để tham số số lần retry cố định trong class.
- **Impact**: Thiếu linh hoạt với các Policy khác nhau hoặc yêu cầu cấu hình độc lập qua biến môi trường.
- **Priority**: Low
- **Status**: Open
- **Created**: Sprint 13
- **Recommendation**: Xây dựng object Config để tiêm (inject) các thông số timeout, retries vào strategy.

## TD-008
- **Title**: API Streaming Support
- **Description**: Public Gateway v1 mới chỉ hỗ trợ trả kết quả JSON 1 cục, chưa hỗ trợ chế độ Server-Sent Events (SSE) \`stream=True\` của OpenAI.
- **Impact**: UX kém đối với các tác vụ dài (long-running generation).
- **Priority**: High
- **Status**: Open
- **Created**: Sprint 17
- **Recommendation**: Triển khai \`StreamingResponse\` trong FastAPI kết hợp với Async I/O (TD-003).

## TD-009
- **Title**: API Authentication & Key Management
- **Description**: Các public endpoint hiện tại hoàn toàn mở (unauthenticated). Chưa có quản lý API keys của người dùng (Gateway users).
- **Impact**: Rủi ro bảo mật, không kiểm soát được lượng truy cập và lạm dụng (abuse) nếu expose ra ngoài.
- **Priority**: Critical
- **Status**: Open
- **Created**: Sprint 17
- **Recommendation**: Xây dựng module middleware/dependency để kiểm tra Bearer Token hợp lệ.
`,
    desc: 'Technical Debt Log'
  },
  'REPORT_SPRINT_15.md': {
    content: `# Sprint 15 Report: Execution Refactor (SRP Restoration)

## 1. Files Changed
- \`ai_gateway/core/executor.py\`
- \`ai_gateway/core/orchestrator.py\`
- \`ai_gateway/core/fallback.py\`
- \`ai_gateway/tests/test_executor.py\`
- \`ai_gateway/tests/test_orchestrator.py\`
- \`ai_gateway/tests/test_fallback.py\`
- \`src/data.ts\` (sync)

## 2. Design Decisions
- **SRP Restoration**: Removed \`PolicyRouter\` dependency entirely from \`ExecutionEngine\`. \`ExecutionEngine\` now receives an already routed \`provider\` instance and focuses purely on execution, catching exceptions, measuring time, logging, and updating the \`CircuitBreaker\`.
- **Validation Check**: If \`provider\` is \`None\`, \`ExecutionEngine\` immediately raises \`ValidationException\`.
- **Orchestrator Routing**: \`ExecutionOrchestrator\` is now the sole component invoking \`PolicyRouter.route\` for the initial attempt (via manual routing if no fallback strategy is used, or passing control to the fallback strategy).
- **Fallback Routing Control**: \`ProviderFallbackStrategy\` no longer holds a reference to \`ExecutionEngine\`. It handles iterative routing loops natively calling \`PolicyRouter.route\`, passing the newly chosen provider to the injected \`operation\` block.

## 3. Assumptions
- Tests are mock-based and do not require external HTTP connections.
- The \`ProviderFallbackStrategy\` retains the state of \`excluded_providers\` and iteratively queries \`PolicyRouter\` until a provider succeeds or all providers are exhausted.
- Unit test assertions verify exact behavior, but I removed irrelevant test stubs in \`test_executor\` that previously mocked \`PolicyRouter\` natively inside the engine.

## 4. Architecture Review
**PASS**. The architecture is now cleaner and adheres tightly to SRP. The \`ExecutionEngine\` is decoupled from routing. Dependencies now follow a cleaner one-way tree:
\`ExecutionOrchestrator\` -> \`PolicyRouter\` & \`ExecutionEngine\`
\`ProviderFallbackStrategy\` -> \`PolicyRouter\`
\`ExecutionEngine\` (No longer depends on \`PolicyRouter\`)

## 5. Technical Debt
- **TD-006 (ExecutionEngine mixed responsibilities)** is formally **RESOLVED** and closed via this Sprint.
- The project retains other outstanding Technical Debt (e.g., HALF_OPEN recovery, Dynamic Normalization, Synchronous pipeline), which are planned for future sprints.

## 6. Sprint Recommendation
- Since core request lifecycle modules are now isolated functionally (Routing vs Executing vs Retrying vs Fallback), the architecture is robust enough for advanced strategies. 
- Recommend moving to **HALF_OPEN Recovery** (TD-001) in Sprint 16 to solidify the \`CircuitBreaker\` resilience.
`,
    desc: 'Sprint 15 Report'
  },
  'REPORT_SPRINT_16.md': {
    content: `# Sprint 16 Report: Circuit Breaker HALF_OPEN + Probe Recovery

## 1. Files Changed
- \`ai_gateway/core/circuit_breaker.py\`
- \`ai_gateway/core/executor.py\`
- \`ai_gateway/tests/test_circuit_breaker.py\`
- \`ai_gateway/tests/test_executor.py\`
- \`TECH_DEBT.md\`
- \`ROADMAP.md\`
- \`AGENTS.md\`
- \`src/data.ts\` (sync)

## 2. Design Decisions
- **HALF_OPEN State Machine**: Triển khai cơ chế kiểm soát \`HALF_OPEN\` thông qua thuộc tính \`probe_in_flight\` trong \`ProviderState\`.
- **Probe Logic**: Khi provider đang ở trạng thái \`HALF_OPEN\`, chỉ duy nhất 1 request đầu tiên được cấp quyền thăm dò (probe) và gán \`probe_in_flight = True\`. Các request sau sẽ bị từ chối (\`is_available\` trả về False) cho tới khi probe hoàn thành và cập nhật trạng thái mới (\`CLOSED\` hoặc \`OPEN\`).
- **ExecutionEngine Integration**: Bổ sung cơ chế gọi \`record_success\` (đưa Circuit về \`CLOSED\`) hoặc \`record_failure\` (đưa Circuit về lại \`OPEN\`) ngay trong block \`try-except\` khi thực thi provider.
- **Timeout Exception Handling**: Bổ sung xử lý riêng rẽ \`TimeoutException\`: Lỗi timeout sẽ chỉ kích hoạt circuit trip (đưa về \`OPEN\`) nếu system đang thử nghiệm (probe) ở mode \`HALF_OPEN\`.

### State Transition Table
| Current State | Event/Condition | Action | New State | \`probe_in_flight\` | \`lock_until\` |
| --- | --- | --- | --- | --- | --- |
| \`CLOSED\` | Provider Failed (Rate Limit/Unavailable) | \`record_failure()\` -> \`trip()\` | \`OPEN\` | \`False\` | \`now() + duration\` |
| \`OPEN\` | \`now() >= lock_until\` | Check \`get_state()\` | \`HALF_OPEN\` | \`False\` | Unchanged |
| \`HALF_OPEN\` | \`is_available()\` called (first time) | Allow request | \`HALF_OPEN\` | \`True\` | Unchanged |
| \`HALF_OPEN\` | \`is_available()\` called (subsequent) | Deny request | \`HALF_OPEN\` | \`True\` | Unchanged |
| \`HALF_OPEN\` | Provider Success | \`record_success()\` | \`CLOSED\` | \`False\` | \`0.0\` |
| \`HALF_OPEN\` | Provider Failed (incl. Timeout) | \`record_failure()\` -> \`trip()\` | \`OPEN\` | \`False\` | \`now() + duration\` |

## 3. Assumptions
- Các \`ProviderUnavailableException\`, \`RateLimitException\` mặc định đều luôn bị coi là critical network failures (Trip ngay lập tức).
- Timeout là lỗi có thể ngẫu nhiên hoặc thoáng qua, nên không trigger trip circuit breaker (khi đang \`CLOSED\`), nhưng đặc biệt nguy hiểm nếu đang ở trạng thái \`HALF_OPEN\`, do đó sẽ fallback thẳng về \`OPEN\`.
- Quản lý \`probe_in_flight\` thông qua boolean (không sử dụng Atomic Integer hay Locks phức tạp), vì môi trường Python hiện tại giả định single process hoặc GIL lock là đủ trong kiến trúc thiết kế mock hiện thời. Đảm bảo chỉ 1 request trở thành probe.

## 4. Architecture Review
Hệ thống xử lý đúng đắn cơ chế phục hồi Circuit Breaker. Tuy nhiên, việc chạy Test Suite chưa thành công hoàn toàn (không PASS 100%) do giới hạn của môi trường không cài đặt sẵn \`pytest\`.

## 5. Technical Debt
- **TD-001 (Circuit Breaker HALF_OPEN implementation)** is formally **RESOLVED** via this Sprint.
- Hệ thống vẫn đang chạy Synchronous (TD-003) và chưa có Async I/O, đây là bottle-neck hiệu năng thực tế.

## 6. External Public API Changed?
- Không.

## 7. Internal API Changed?
- Có bổ sung thêm \`record_success(provider_name)\` và \`record_failure(provider_name, ...)\` vào \`CircuitBreaker\`.

## 8. Breaking Change?
- Không. Interface hiện tại vẫn giữ nguyên (tương thích lùi), chỉ bổ sung API.

## 9. Sprint Recommendation
- Lõi hệ thống (Core Engine, CircuitBreaker, Routing) đã gần như hoàn thiện. Đề xuất chuẩn bị cho **Milestone 2 - Public Gateway** (Sprint 17), tập trung vào các API REST tương thích OpenAI.
`,
    desc: 'Sprint 16 Report'
  },
  'REPORT_SPRINT_17.md': {
    content: `# Sprint 17.2 Bugfix Report: Fix Public Gateway CAP Contract Mapping & Abstract Strategy Instantiation

## 1. Files Changed
- \`ai_gateway/api/app.py\`
- \`ai_gateway/tests/test_api.py\`
- \`ai_gateway/core/fallback.py\`
- \`ai_gateway/tests/test_fallback.py\`

## 2. Design Decisions
- **Fix MockRouter Assertions**: Chỉnh sửa hành vi của \`MockRouter\` trong file \`test_fallback.py\` để biến \`call_count\` tăng ngay lập tức ở đầu hàm (ngay cả khi gọi router nhưng bị throw \`NoProviderAvailableException\`). Điều này đảm bảo test \`test_6_both_providers_fail\` kiểm chứng chính xác 3 lần routing attempts trước khi fallback bị cạn kiệt.
- **Fix Fallback Exception Mapping**: Sửa lỗi \`CircuitOpenException\` (và \`RateLimitException\`) không kích hoạt cơ chế fallback. Đã xóa các class Exception định nghĩa trùng lặp nội bộ trong \`fallback.py\` và import trực tiếp từ \`ai_gateway.core.executor\` để đồng nhất type catch. Tránh được lỗi bắt sai exception khiến fallback strategy thất bại.
- **Fix Abstract Strategy Instantiation**: Khắc phục lỗi TypeError ("Can't instantiate abstract class RetryStrategy without an implementation for abstract method 'execute'") bằng cách thay đổi \`RetryStrategy()\` thành concrete class \`NoRetryStrategy()\`. Cấu trúc factory \`create_app\` vẫn được giữ nguyên tính độc lập để test.
- **Fix CAP Contract Mapping**:
  - Đã loại bỏ import sai class \`Message\` (không tồn tại trong module \`ai_gateway.protocols.cap\`). Thay vào đó chỉ sử dụng duy nhất class \`AgentRequest\` có sẵn.
  - Sửa lại việc khởi tạo \`AgentRequest\` từ HTTP Request để bám đúng vào contract chuẩn của \`AgentRequest.model_fields\`, với các trường bắt buộc như \`request_id\`, \`messages\` (đã được map thủ công thành cấu trúc dict) và tuỳ chọn \`tools=None\` thay vì gọi đối tượng không hợp lệ.
  - Sửa lỗi mapping từ response ảo (có \`data\` và \`metadata\`) sang đúng contract của \`AgentResponse\` (với các trường \`response_id\`, \`content\`, \`usage\`).
- **503 Service Unavailable Exception Mapping**: Xử lý triệt để lỗi \`NoProviderAvailableException\` từ core truyền ra và map chuẩn thành mã lỗi \`503 Service Unavailable\`. Cấu trúc JSON response tuân thủ theo chuẩn format lỗi của OpenAI API để client dễ dàng tương thích (\`error.type = provider_unavailable\`, \`error.code = no_provider_available\`). Tránh được việc throw lỗi 500 do nội bộ.
- **\`create_app\` Factory**: Tái cấu trúc module \`app.py\` sử dụng Application Factory Pattern (\`create_app(orchestrator, registry)\`). Cách làm này loại bỏ sự phụ thuộc (hard dependency) của API vào các core components thật khi thực thi tests, cho phép dễ dàng inject Mock Orchestrator và Mock Registry.
- **Dynamic \`/models\` Endpoint**: API \`/models\` không còn bị crash khi Registry chưa có provider, thay vào đó sẽ graceful return object dạng \`{"object": "list", "data": []}\`.
- **Simplified \`/health\`**: Bỏ các dependency không cần thiết (không gọi thật vào provider), chỉ trả về thông tin tối giản (\`status\`, \`service\`, \`version\`).

## 3. Assumptions
- Các tham số streaming, authentication, tool calling tạm thời chưa được xử lý và mặc định bỏ qua.
- Với testing, chúng ta giả định MockOrchestrator có thể bao phủ hoàn toàn contract của Core Orchestrator mà API mong đợi.

## 4. Architecture Review
Cấu trúc Layer API đã trở nên độc lập và dễ test hơn, đồng thời giải quyết triệt để lỗi Contract mapping. Tuy nhiên, việc chạy Test Suite chưa thành công (không "PASS 100%") do giới hạn của môi trường không cài đặt sẵn \`pytest\`. Các file test (\`test_api.py\`) đã được cập nhật logic mock đầy đủ.

## 5. Technical Debt
- **TD-003 (Async Migration)**: Hệ thống vẫn chạy Synchronous, API framework đã dùng FastAPI (hỗ trợ async) nhưng core vẫn là block operations.
- **TD-008 (API Streaming Support)**: Chưa hỗ trợ luồng stream (\`stream=True\`) của OpenAI.
- **TD-009 (API Authentication)**: Public Gateway hiện chưa có tính năng check API key.

## 6. External Public API Changed?
- API \`/chat/completions\` hiện tại sẽ trả về HTTP Status 503 thay vì 500 khi hệ thống không có Provider nào khả dụng (đáp ứng đúng chuẩn OpenAI-compatible error handling). Cấu trúc error JSON được thiết kế chuẩn xác hơn.

## 7. Internal API Changed?
- Việc gọi API layer tới CAP package tuân thủ đúng định dạng của AgentRequest và AgentResponse thật thay vì class mock ảo.

## 8. Breaking Change?
- Có thay đổi nhỏ trong cấu trúc internal bootstrap API, tuy nhiên do Public Gateway mới phát hành dạng thử nghiệm nên chưa gây ảnh hưởng tới client hiện tại.

## 9. Sprint Recommendation
- API Gateway đã chịu lỗi (fault-tolerant) tốt hơn trước các sự cố ở tầng Routing/Provider. Hệ thống Mapping contract đã đồng bộ. Sprint tiếp theo tập trung vào việc quản lý API Key (TD-009) để đảm bảo an toàn nếu expose dịch vụ ra public.
`,
    desc: 'Báo cáo Sprint 17 về Public REST API v1.'
  },
  'ai_gateway/core/__init__.py': {
    content: `"""
Core module for Tiểu Tony AI Gateway.
Contains configuration, logging, and foundational system utilities.
"""
`,
    desc: 'File khởi tạo package core, định nghĩa các tiện ích lõi của hệ thống.'
  },
  'ai_gateway/core/config.py': {
    content: `"""
Core Configuration Module for AI Gateway (Dự án Tiểu Tony)
"""
import os
from dataclasses import dataclass


@dataclass
class GatewayConfig:
    """System configuration settings for the AI Gateway."""
    app_name: str = "Tiểu Tony AI Gateway"
    version: str = "0.1.0-phase0"
    environment: str = os.getenv("GATEWAY_ENV", "development")
    host: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    port: int = int(os.getenv("GATEWAY_PORT", "8000"))
    debug: bool = True


def get_config() -> GatewayConfig:
    """Load and return system configuration."""
    return GatewayConfig()
`,
    desc: 'Lớp cấu hình trung tâm (GatewayConfig) quản lý tham số biến môi trường, host, port và chế độ debug.'
  },
  'ai_gateway/core/router.py': {
    content: `import time
import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel
from ai_gateway.registry.capability import (
    CapabilityRegistry,
    TaskRequirement,
    RoutingPolicy,
    ScoringEngine,
)
from ai_gateway.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

class RoutingDecision(BaseModel):
    provider_name: str
    provider: Any
    score: float
    reason: str
    excluded_providers: Dict[str, str]
    policy_used: RoutingPolicy
    timestamp: float

class NoProviderAvailableException(Exception):
    """Raised when no provider meets the requirements or constraints."""
    pass

class PolicyRouter:
    """Routes tasks to the most suitable AI provider based on capabilities and policies."""
    
    def __init__(self, registry: CapabilityRegistry, circuit_breaker: Optional[CircuitBreaker] = None):
        self.registry = registry
        self.circuit_breaker = circuit_breaker

    def route(
        self,
        requirement: TaskRequirement,
        context: Dict[str, Any],
        quotas: Dict[str, float],
        policy: RoutingPolicy
    ) -> RoutingDecision:
        logger.info(f"Routing task: {requirement.task_type} with policy {policy.name}")
        
        candidates = self.registry.all()
        excluded_providers: Dict[str, str] = {}
        scored_providers = []

        logger.info(f"Candidate Providers: {list(candidates.keys())}")

        for name, capability in candidates.items():
            # Circuit breaker check
            if self.circuit_breaker and not self.circuit_breaker.is_available(name):
                excluded_providers[name] = "Circuit breaker OPEN"
                logger.info(f"Provider excluded: {name} - Reason: Circuit breaker OPEN")
                continue

            provider = self.registry.get_provider(name)
            if not provider:
                continue

            health_info = provider.health()
            is_healthy = health_info.get("status") == "ok"
            quota = quotas.get(name, 1.0)
            
            # Constraints Check
            if not ScoringEngine.constraints(capability, requirement, quota, is_healthy):
                if quota <= 0:
                    reason = "Out of quota"
                elif not is_healthy:
                    reason = "Provider unhealthy"
                elif capability.context_window < requirement.required_context:
                    reason = "Context window too small"
                elif requirement.required_tools and not capability.tool_call:
                    reason = "Tool calling not supported"
                elif capability.cost > requirement.budget:
                    reason = "Cost exceeds budget"
                elif capability.latency > requirement.latency_requirement:
                    reason = "Latency exceeds requirement"
                else:
                    reason = "Constraints not met"
                
                excluded_providers[name] = reason
                logger.info(f"Provider excluded: {name} - Reason: {reason}")
                continue
            
            # Score Calculation
            score = ScoringEngine.score(capability, requirement, policy, quota)
            scored_providers.append((score, name, provider))
            logger.info(f"Score for {name}: {score:.4f}")

        if not scored_providers:
            logger.error("No provider available for routing.")
            raise NoProviderAvailableException("No provider met the constraints.")

        # Sort: Descending by score, Tie-break alphabetically by provider name
        scored_providers.sort(key=lambda x: (-x[0], x[1]))
        
        best_score, best_name, best_provider = scored_providers[0]
        logger.info(f"Selected Provider: {best_name} with score {best_score:.4f}")

        return RoutingDecision(
            provider_name=best_name,
            provider=best_provider,
            score=best_score,
            reason=f"Highest score ({best_score:.2f})",
            excluded_providers=excluded_providers,
            policy_used=policy,
            timestamp=time.time()
        )
`,
    desc: 'PolicyRouter định tuyến logic cho các Provider dựa vào Capability và Policy.'
  },
  'ai_gateway/core/circuit_breaker.py': {
    content: `import time
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class Clock:
    """Abstraction for time to allow deterministic testing."""
    def now(self) -> float:
        return time.time()

class ProviderState(BaseModel):
    state: CircuitState = CircuitState.CLOSED
    lock_until: float = 0.0
    reason: str = ""
    probe_in_flight: bool = False

class CircuitBreaker:
    """Manages the availability state of AI providers."""
    
    def __init__(self, clock: Optional[Clock] = None):
        self._states: Dict[str, ProviderState] = {}
        self.clock = clock or Clock()

    def get_state(self, provider_name: str) -> CircuitState:
        """Returns the current state of the circuit breaker for a provider."""
        if provider_name not in self._states:
            return CircuitState.CLOSED
        
        provider_state = self._states[provider_name]
        
        # Auto-reset if lock_until has expired
        if provider_state.state == CircuitState.OPEN and self.clock.now() >= provider_state.lock_until:
            provider_state.state = CircuitState.HALF_OPEN
            provider_state.reason = "Lock expired, entering HALF_OPEN"
            provider_state.probe_in_flight = False
            
        return provider_state.state

    def is_available(self, provider_name: str) -> bool:
        """Checks if a provider is currently available to accept requests."""
        state = self.get_state(provider_name)
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            provider_state = self._states[provider_name]
            if not provider_state.probe_in_flight:
                provider_state.probe_in_flight = True
                return True
            return False
        return False

    def record_success(self, provider_name: str) -> None:
        if provider_name in self._states:
            self._states[provider_name].state = CircuitState.CLOSED
            self._states[provider_name].probe_in_flight = False
            self._states[provider_name].lock_until = 0.0
            self._states[provider_name].reason = "Success"

    def record_failure(self, provider_name: str, duration: float = 30.0, reason: str = "") -> None:
        self.trip(provider_name, duration, reason)

    def trip(self, provider_name: str, duration: float = 30.0, reason: str = "") -> None:
        """Trips the circuit breaker, marking the provider as OPEN for a duration."""
        lock_until = self.clock.now() + duration
        if provider_name not in self._states:
            self._states[provider_name] = ProviderState(
                state=CircuitState.OPEN, 
                lock_until=lock_until, 
                reason=reason
            )
        else:
            self._states[provider_name].state = CircuitState.OPEN
            self._states[provider_name].lock_until = lock_until
            self._states[provider_name].reason = reason
            self._states[provider_name].probe_in_flight = False

    def reset(self, provider_name: str) -> None:
        """Manually resets the circuit breaker, marking the provider as CLOSED."""
        if provider_name in self._states:
            self._states[provider_name].state = CircuitState.CLOSED
            self._states[provider_name].lock_until = 0.0
            self._states[provider_name].reason = "Manual reset"
            self._states[provider_name].probe_in_flight = False
`,
    desc: 'CircuitBreaker kiểm soát trạng thái Provider.'
  },
  'ai_gateway/core/executor.py': {
    content: `import time
import logging
from typing import Dict, Any, Optional

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.circuit_breaker import CircuitBreaker

class RateLimitException(Exception):
    pass

class ProviderUnavailableException(Exception):
    pass

class TimeoutException(Exception):
    pass

class UnknownProviderException(Exception):
    pass

class CircuitOpenException(Exception):
    pass

class ValidationException(Exception):
    pass

class AuthenticationException(Exception):
    pass


class ExecutionEngine:
    """Executes requests using the appropriate provider determined by the router."""

    def __init__(
        self, 
        circuit_breaker: CircuitBreaker,
        logger: Optional[logging.Logger] = None
    ):
        self.circuit_breaker = circuit_breaker
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self, 
        request: AgentRequest,
        provider: Any
    ) -> AgentResponse:
        if not provider:
            raise ValidationException("Provider cannot be None.")

        provider_name = getattr(provider, 'name', 'unknown')

        # If a provider is injected directly, check circuit breaker just in case,
        # but usually the router checks it. If it's open, throw CircuitOpenException.
        if not self.circuit_breaker.is_available(provider_name):
            raise CircuitOpenException(f"Circuit breaker is OPEN for {provider_name}")

        self.logger.info(f"Executing request {request.request_id} with provider {provider_name}")
        start_time = time.time()
        
        try:
            response = provider.chat(request)
            execution_time = time.time() - start_time
            self.logger.info(f"Request {request.request_id} succeeded in {execution_time:.4f}s")
            self.circuit_breaker.record_success(provider_name)
            return response
        except (RateLimitException, ProviderUnavailableException) as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            raise
        except TimeoutException as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with TimeoutException in {execution_time:.4f}s. Reason: {e}")
            from ai_gateway.core.circuit_breaker import CircuitState
            if self.circuit_breaker.get_state(provider_name) == CircuitState.HALF_OPEN:
                self.circuit_breaker.record_failure(provider_name, reason=str(e))
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            raise
`,
    desc: 'Execution Engine quản lý luồng gọi provider và xử lý exception.'
  },
  'ai_gateway/core/orchestrator.py': {
    content: `import time
import logging
from typing import Optional, Dict, Any

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.executor import ExecutionEngine
from ai_gateway.core.router import PolicyRouter
from ai_gateway.registry.capability import TaskRequirement, RoutingPolicy
from ai_gateway.core.retry import RetryStrategy, NoRetryStrategy
from ai_gateway.core.fallback import FallbackStrategy, NoFallbackStrategy
from ai_gateway.adapters.base import BaseProvider

class ExecutionOrchestrator:
    """Orchestrates the lifecycle of a request."""
    
    def __init__(
        self,
        engine: ExecutionEngine,
        router: PolicyRouter,
        retry_strategy: Optional[RetryStrategy] = None,
        fallback_strategy: Optional[FallbackStrategy] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.engine = engine
        self.router = router
        self.retry_strategy = retry_strategy or NoRetryStrategy()
        self.fallback_strategy = fallback_strategy or NoFallbackStrategy()
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self,
        request: AgentRequest,
        requirement: Optional[TaskRequirement] = None,
        context: Optional[Dict[str, Any]] = None,
        quotas: Optional[Dict[str, float]] = None,
        policy: Optional[RoutingPolicy] = None
    ) -> AgentResponse:
        self.logger.info(f"Orchestrator started for request {request.request_id}")
        start_time = time.time()
        
        requirement = requirement or TaskRequirement()
        context = context or {}
        quotas = quotas or {}
        policy = policy or RoutingPolicy.BALANCED

        def _operation(provider: BaseProvider) -> AgentResponse:
            def _inner():
                return self.engine.execute(
                    request=request,
                    provider=provider
                )
            return self.retry_strategy.execute(_inner)
            
        try:
            if isinstance(self.fallback_strategy, NoFallbackStrategy):
                decision = self.router.route(requirement, context, quotas, policy)
                response = _operation(decision.provider)
            else:
                response = self.fallback_strategy.execute(
                    _operation,
                    requirement=requirement,
                    context=context,
                    quotas=quotas,
                    policy=policy
                )
            execution_time = time.time() - start_time
            self.logger.info(f"Orchestrator success for request {request.request_id} in {execution_time:.4f}s")
            return response
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Orchestrator failure for request {request.request_id} in {execution_time:.4f}s. Reason: {e}")
            raise
`,
    desc: 'Execution Orchestrator điều phối vòng đời request.'
  },
  'ai_gateway/core/fallback.py': {
    content: `import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List

from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.core.executor import (
    ProviderUnavailableException,
    UnknownProviderException,
    CircuitOpenException,
    ValidationException,
    AuthenticationException,
    RateLimitException,
)

logger = logging.getLogger(__name__)

class FallbackStrategy(ABC):
    @abstractmethod
    def execute(
        self,
        operation: Callable[[BaseProvider], AgentResponse],
        # Adding kwargs to pass request context without violating the core signature requirement
        **kwargs
    ) -> AgentResponse:
        ...

class NoFallbackStrategy(FallbackStrategy):
    def execute(self, operation: Callable[[BaseProvider], AgentResponse], **kwargs) -> AgentResponse:
        # Without routing, we just pass None and let ExecutionEngine do it if modified to handle None,
        # OR we can assume operation doesn't strictly need a BaseProvider if it routes internally.
        # But to respect the signature:
        return operation(None) # type: ignore

class ProviderFallbackStrategy(FallbackStrategy):
    def __init__(self, router: PolicyRouter):
        self.router = router

    def execute(self, operation: Callable[[BaseProvider], AgentResponse], **kwargs) -> AgentResponse:
        requirement = kwargs.get("requirement")
        context = kwargs.get("context", {})
        quotas = kwargs.get("quotas")
        
        from ai_gateway.registry.capability import RoutingPolicy
        policy = kwargs.get("policy") or RoutingPolicy.BALANCED

        failed_providers: List[str] = context.get("excluded_providers", [])
        
        while True:
            context["excluded_providers"] = failed_providers
            
            try:
                decision = self.router.route(requirement, context, quotas, policy)
            except NoProviderAvailableException as e:
                logger.error(f"Fallback exhausted. No providers available: {e}")
                raise
                
            provider = decision.provider
            if not provider:
                raise UnknownProviderException(f"Provider {decision.provider_name} not found")

            try:
                return operation(provider)
            except (ProviderUnavailableException, CircuitOpenException, NoProviderAvailableException, RateLimitException) as e:
                logger.warning(f"Provider {decision.provider_name} failed with {type(e).__name__}. Triggering fallback.")
                failed_providers.append(decision.provider_name)
            except Exception as e:
                logger.error(f"Provider {decision.provider_name} failed with non-fallback exception {type(e).__name__}.")
                raise
`,
    desc: 'Fallback Strategy implementations.'
  },
  'ai_gateway/core/retry.py': {
    content: `import logging
from abc import ABC, abstractmethod
from typing import Callable, Tuple, Type

from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.core.executor import (
    TimeoutException,
    RateLimitException,
    ProviderUnavailableException,
    UnknownProviderException
)

logger = logging.getLogger(__name__)

class AuthenticationException(Exception):
    pass

class RetryStrategy(ABC):
    """Abstract base class for retry strategies."""
    
    @abstractmethod
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        """Executes the operation according to the retry strategy."""
        pass

class NoRetryStrategy(RetryStrategy):
    """Executes the operation exactly once, without retries."""
    
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        return operation()

class FixedRetryStrategy(RetryStrategy):
    """Retries the operation a fixed number of times for specific exceptions."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retryable_exceptions: Tuple[Type[Exception], ...] = (TimeoutException,)
        
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        attempts = 0
        while True:
            try:
                return operation()
            except self.retryable_exceptions as e:
                attempts += 1
                if attempts > self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) reached. Failing.")
                    raise
                logger.warning(f"Operation failed with {type(e).__name__}. Retrying {attempts}/{self.max_retries}...")
            except Exception as e:
                logger.error(f"Operation failed with non-retryable exception {type(e).__name__}. Re-raising.")
                raise
`,
    desc: 'Retry Strategy implementations.'
  },
  'ai_gateway/core/state.py': {
    content: `import uuid
import time
from typing import Any, Dict
from pydantic import BaseModel

class StateSnapshot(BaseModel):
    """Pydantic model representing a snapshot of the agent's state."""
    snapshot_id: str
    timestamp: float
    working_directory: str
    variables: Dict[str, Any]
    current_state: Dict[str, Any]

class StateManager:
    """Manages the internal state of the Agent in the local environment."""
    
    def __init__(self, working_directory: str = "/"):
        self.working_directory = working_directory
        self.variables: Dict[str, Any] = {}
        self.current_state: Dict[str, Any] = {
            "git_diff": "",
            "files": [],
            "conversation_summary": ""
        }
        # In-memory storage for snapshots mapped by snapshot_id
        self._snapshots: Dict[str, StateSnapshot] = {}

    def update_variable(self, key: str, value: Any) -> None:
        """Update a variable in the agent's environment."""
        self.variables[key] = value

    def save_snapshot(self) -> StateSnapshot:
        """Package the entire current state into a snapshot object."""
        snapshot_id = str(uuid.uuid4())
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            working_directory=self.working_directory,
            variables=self.variables.copy(),
            current_state=self.current_state.copy()
        )
        self._snapshots[snapshot_id] = snapshot
        return snapshot

    def load_snapshot(self, snapshot_id: str) -> None:
        """Restore the state from a previously saved snapshot."""
        if snapshot_id not in self._snapshots:
            raise ValueError(f"Snapshot with ID '{snapshot_id}' not found.")
        
        snapshot = self._snapshots[snapshot_id]
        self.working_directory = snapshot.working_directory
        self.variables = snapshot.variables.copy()
        self.current_state = snapshot.current_state.copy()
`,
    desc: 'Quản lý trạng thái làm việc của Agent, hỗ trợ tạo và tải snapshot.'
  },
  'ai_gateway/core/compressor.py': {
    content: `import math
from typing import List, Dict, Any

class MessageCompressor:
    """
    Compresses conversation history to fit within context limits using rule-based techniques.
    """
    
    def __init__(self, chars_per_token: float = 4.0):
        self.chars_per_token = chars_per_token

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        if not text:
            return 0
        return math.ceil(len(text) / self.chars_per_token)

    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate tokens for a single message."""
        content = message.get("content", "")
        if content is None:
            return 0
        return self._estimate_tokens(str(content))

    def _summarize_long_text(self, text: str, max_chars: int) -> str:
        """Summarize long text by keeping the beginning and end."""
        if len(text) <= max_chars:
            return text
        
        half_limit = max(0, (max_chars - 50) // 2)
        if half_limit == 0:
            return "[...TRUNCATED...]"
            
        return text[:half_limit] + "\\n\\n...[CONTENT COMPRESSED]...\\n\\n" + text[-half_limit:]

    def compress(self, messages: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        """
        Compresses messages to fit within max_tokens.
        Strategy:
        1. Always keep 'system' messages.
        2. Always keep the last few messages (e.g., last 2).
        3. For messages in the middle, truncate long contents (like logs or huge code blocks)
           if we are over the token limit.
        """
        if not messages:
            return []

        total_tokens = sum(self._estimate_message_tokens(m) for m in messages)
        if total_tokens <= max_tokens:
            return messages

        compressed_messages = []
        
        # Identify system messages and the most recent messages
        system_indices = [i for i, m in enumerate(messages) if m.get("role") == "system"]
        
        # Keep the last 2 messages intact if possible
        recent_count = min(2, len(messages) - len(system_indices))
        recent_indices = []
        if recent_count > 0:
             # Get the last recent_count indices that are not system messages
             non_system_indices = [i for i in range(len(messages)) if i not in system_indices]
             recent_indices = non_system_indices[-recent_count:] if non_system_indices else []

        protected_indices = set(system_indices + recent_indices)
        
        # Calculate tokens used by protected messages
        protected_tokens = sum(self._estimate_message_tokens(messages[i]) for i in protected_indices)
        
        # Calculate remaining tokens for the middle messages
        remaining_tokens = max(0, max_tokens - protected_tokens)
        
        # Middle messages are those not protected
        middle_indices = [i for i in range(len(messages)) if i not in protected_indices]
        
        # Distribute remaining tokens among middle messages evenly
        if middle_indices:
            tokens_per_middle_msg = max(5, remaining_tokens // len(middle_indices))
            max_chars_per_msg = int(tokens_per_middle_msg * self.chars_per_token)
        else:
            max_chars_per_msg = 0

        for i, msg in enumerate(messages):
            new_msg = msg.copy()
            if i in protected_indices:
                compressed_messages.append(new_msg)
            else:
                content = str(new_msg.get("content", ""))
                compressed_content = self._summarize_long_text(content, max_chars_per_msg)
                new_msg["content"] = compressed_content
                compressed_messages.append(new_msg)

        return compressed_messages
`,
    desc: 'Giải thuật nén tin nhắn phi LLM (Rule-based) để tránh tràn token.'
  },
  'ai_gateway/adapters/__init__.py': {
    content: `"""
Adapters module.
Responsible for connecting external AI providers (OpenAI, Gemini, Anthropic, local models).
"""
`,
    desc: 'Package adapters chuẩn bị tích hợp các nhà cung cấp mô hình AI (OpenAI, Gemini, Ollama...) ở các phase tiếp theo.'
  },
  'ai_gateway/adapters/base.py': {
    content: `import abc
from typing import Generator, Dict, Any
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class BaseProvider(abc.ABC):
    """
    Abstract Base Class defining the standard interface for all AI providers.
    """
    
    @property
    @abc.abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Returns the capabilities of the provider."""
        pass

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establishes connection or authenticates with the provider."""
        pass

    @abc.abstractmethod
    def chat(self, request: AgentRequest) -> AgentResponse:
        """Processes a chat completion request."""
        pass

    @abc.abstractmethod
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        """Processes a streaming chat completion request."""
        pass

    @abc.abstractmethod
    def tool_call(self, request: AgentRequest) -> AgentResponse:
        """Processes a request that mandates tool calling."""
        pass

    @abc.abstractmethod
    def health(self) -> Dict[str, Any]:
        """Checks the health and availability of the provider."""
        pass

    @abc.abstractmethod
    def estimate_cost(self, request: AgentRequest) -> float:
        """Estimates the cost of a given request."""
        pass
`,
    desc: 'Định nghĩa Abstract Base Class `BaseProvider` với các hàm chuẩn giao tiếp cho Provider.'
  },
  'ai_gateway/adapters/gemini.py': {
    content: `import uuid
from typing import Generator, Dict, Any
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse, ToolCall

class GeminiAdapter(BaseProvider):
    """
    Adapter for Google Gemini API (Mock Implementation for Phase 2).
    """

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "codebase_reading": 10,
            "context_window": 10,
            "reasoning": 9
        }

    def connect(self) -> bool:
        # Mock connection logic
        return True

    def chat(self, request: AgentRequest) -> AgentResponse:
        # 1. Translate CAP to Gemini payload (Mock)
        gemini_messages = []
        for msg in request.messages:
            gemini_messages.append({
                "role": "model" if msg.get("role") == "assistant" else "user",
                "parts": [{"text": msg.get("content", "")}]
            })
            
        # 2. Mock calling Gemini API
        mock_response_content = f"Mocked Gemini response for request {request.request_id}"
        
        # 3. Translate Gemini response back to CAP
        return AgentResponse(
            response_id=f"gemini_res_{uuid.uuid4().hex[:8]}",
            content=mock_response_content,
            usage={"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35}
        )

    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        # Mock streaming chunks
        for i in range(3):
            yield AgentResponse(
                response_id=f"gemini_stream_{uuid.uuid4().hex[:8]}",
                content=f"Chunk {i} ",
                usage={"prompt_tokens": 15, "completion_tokens": 5, "total_tokens": 20}
            )

    def tool_call(self, request: AgentRequest) -> AgentResponse:
        # Mock tool call response
        tc = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            name="mock_tool",
            arguments={"param": "value"}
        )
        return AgentResponse(
            response_id=f"gemini_tool_res_{uuid.uuid4().hex[:8]}",
            content=None,
            tool_calls=[tc],
            usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
        )

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "gemini"}

    def estimate_cost(self, request: AgentRequest) -> float:
        # Mock cost estimation based on number of messages
        return 0.001 * len(request.messages)
`,
    desc: 'Adapter giả lập (Mock) cho Google Gemini API, chuyển đổi qua lại giữa CAP và Gemini.'
  },
  'ai_gateway/protocols/__init__.py': {
    content: `"""
Protocols module.
Defines standardized data structures, request/response schemas, and communication interfaces.
"""
`,
    desc: 'Package protocols chuẩn hoá cấu trúc dữ liệu input/output chuẩn cho toàn bộ Gateway.'
  },
  'ai_gateway/protocols/cap.py': {
    content: `from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    tool_call_id: str
    output: str
    is_error: bool = False


class AgentRequest(BaseModel):
    request_id: str
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None


class AgentResponse(BaseModel):
    response_id: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    usage: Dict[str, Any]


class ContextSnapshot(BaseModel):
    snapshot_id: str
    timestamp: float
    tokens_used: int
    data: Dict[str, Any]
`,
    desc: 'Định nghĩa các Data Model chuẩn sử dụng Pydantic v2 cho toàn bộ Agent Loop.'
  },
  'ai_gateway/registry/__init__.py': {
    content: `"""
Registry module.
Manages model routing tables, dynamic provider registration, and endpoint discovery.
"""
`,
    desc: 'Package registry quản lý bảng định tuyến mô hình và khám phá các endpoint động.'
  },
  'ai_gateway/registry/capability.py': {
    content: `import logging
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class RoutingPolicy(str, Enum):
    BALANCED = "BALANCED"
    QUALITY_FIRST = "QUALITY_FIRST"
    COST_FIRST = "COST_FIRST"
    LATENCY_FIRST = "LATENCY_FIRST"

class TaskType(str, Enum):
    CODING = "CODING"
    REASONING = "REASONING"
    TRANSLATION = "TRANSLATION"
    GENERAL = "GENERAL"

class ProviderCapability(BaseModel):
    coding: float = 0.0
    reasoning: float = 0.0
    translation: float = 0.0
    context_window: int = 0
    tool_call: bool = False
    latency: float = 0.0
    cost: float = 0.0
    quota_weight: float = 1.0

class TaskRequirement(BaseModel):
    task_type: TaskType = TaskType.GENERAL
    required_context: int = 0
    required_tools: bool = False
    priority: int = 1
    budget: float = 100.0
    latency_requirement: float = 10000.0

class CapabilityRegistry:
    def __init__(self):
        self._providers: Dict[str, Any] = {}
        self._capabilities: Dict[str, ProviderCapability] = {}

    def register(self, name: str, provider: Any) -> None:
        self._providers[name] = provider
        # Extract raw dict from provider capabilities property
        raw_caps = provider.capabilities
        self._capabilities[name] = ProviderCapability(
            coding=raw_caps.get("coding", raw_caps.get("codebase_reading", 0.0)),
            reasoning=raw_caps.get("reasoning", 0.0),
            translation=raw_caps.get("translation", 0.0),
            context_window=raw_caps.get("context_window", 0),
            tool_call=raw_caps.get("tool_call", False),
            latency=raw_caps.get("latency", 0.0),
            cost=raw_caps.get("cost", 0.0),
            quota_weight=raw_caps.get("quota_weight", 1.0)
        )

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)
        self._capabilities.pop(name, None)

    def refresh(self, name: str, provider: Any) -> None:
        self.register(name, provider)

    def get(self, name: str) -> Optional[ProviderCapability]:
        return self._capabilities.get(name)

    def get_provider(self, name: str) -> Optional[Any]:
        return self._providers.get(name)

    def all(self) -> Dict[str, ProviderCapability]:
        return self._capabilities.copy()

class ScoringEngine:
    @staticmethod
    def constraints(capability: ProviderCapability, requirement: TaskRequirement, quota: float, is_healthy: bool) -> bool:
        if quota <= 0:
            return False
        if not is_healthy:
            return False
        if capability.context_window < requirement.required_context:
            return False
        if requirement.required_tools and not capability.tool_call:
            return False
        if capability.cost > requirement.budget:
            return False
        if capability.latency > requirement.latency_requirement:
            return False
        return True

    @staticmethod
    def weight(policy: RoutingPolicy) -> Dict[str, float]:
        if policy == RoutingPolicy.QUALITY_FIRST:
            return {"quality": 0.7, "cost": 0.1, "latency": 0.1, "quota": 0.1}
        elif policy == RoutingPolicy.COST_FIRST:
            return {"quality": 0.2, "cost": 0.6, "latency": 0.1, "quota": 0.1}
        elif policy == RoutingPolicy.LATENCY_FIRST:
            return {"quality": 0.2, "cost": 0.1, "latency": 0.6, "quota": 0.1}
        else:  # BALANCED
            return {"quality": 0.4, "cost": 0.3, "latency": 0.2, "quota": 0.1}

    @staticmethod
    def score(capability: ProviderCapability, requirement: TaskRequirement, policy: RoutingPolicy, quota: float) -> float:
        weights = ScoringEngine.weight(policy)

        # Base quality score on task type
        quality_score = 0.0
        if requirement.task_type == TaskType.CODING:
            quality_score = capability.coding
        elif requirement.task_type == TaskType.REASONING:
            quality_score = capability.reasoning
        elif requirement.task_type == TaskType.TRANSLATION:
            quality_score = capability.translation
        else:
            quality_score = (capability.coding + capability.reasoning + capability.translation) / 3.0

        # Cost score (inverted, 0 means best/free, higher is worse)
        # Assumes cost is typically between 0 and 10.
        cost_score = max(0.0, 10.0 - capability.cost)

        # Latency score (inverted, lower is better)
        # Latency is often in ms, max 10,000 assumed for normalization
        latency_score = max(0.0, 10.0 - (capability.latency / 1000.0))

        # Quota score
        quota_score = min(10.0, quota * capability.quota_weight)

        final_score = (
            quality_score * weights["quality"] +
            cost_score * weights["cost"] +
            latency_score * weights["latency"] +
            quota_score * weights["quota"]
        )
        return final_score
`,
    desc: 'Capability Registry định nghĩa Schema và quản lý Provider Capability.'
  },
  'ai_gateway/api/__init__.py': {
    content: `# API module
`,
    desc: 'Module khởi tạo API layer.'
  },
  'ai_gateway/api/schemas.py': {
    content: `from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
`,
    desc: 'Chứa các schema Pydantic tương thích OpenAI API (ChatCompletion).'
  },
  'ai_gateway/api/app.py': {
    content: `import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    Message as APIMessage,
    ChatCompletionUsage
)

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.orchestrator import ExecutionOrchestrator
from ai_gateway.registry.capability import CapabilityRegistry
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.fallback import ProviderFallbackStrategy
from ai_gateway.core.retry import NoRetryStrategy
from ai_gateway.core.executor import ExecutionEngine


def create_app(orchestrator: Optional[ExecutionOrchestrator] = None, registry: Optional[CapabilityRegistry] = None) -> FastAPI:
    app = FastAPI(title="Tiểu Tony AI Gateway", version="0.1.0")

    # Initialize core components if not provided
    if registry is None:
        registry = CapabilityRegistry()
        # Load provider from environment if available
        import os
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_api_key:
            from ai_gateway.adapters.openrouter import OpenRouterAdapter
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            provider = OpenRouterAdapter(api_key=openrouter_api_key, default_model=openrouter_model)
            registry.register("openrouter", provider)
    
    if orchestrator is None:
        router = PolicyRouter(registry)
        circuit_breaker = CircuitBreaker()
        retry_strategy = NoRetryStrategy()
        fallback_strategy = ProviderFallbackStrategy(router)
        executor = ExecutionEngine(circuit_breaker)

        orchestrator = ExecutionOrchestrator(
            engine=executor,
            router=router,
            retry_strategy=retry_strategy,
            fallback_strategy=fallback_strategy
        )

    @app.get("/health")
    async def health_check():
        """Returns service health."""
        return {
            "status": "ok",
            "service": "ai_gateway",
            "version": "0.1.0"
        }

    @app.get("/models")
    async def list_models():
        """Returns available models in OpenAI-compatible format."""
        providers = list(registry.all().keys()) if hasattr(registry, 'all') else []
        
        if not providers:
            return {
                "object": "list",
                "data": []
            }
            
        data = []
        if "openrouter" in providers:
            # If OpenRouter is registered, expose models
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            data.append({
                "id": openrouter_model,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openrouter"
            })
        
        return {
            "object": "list",
            "data": data
        }

    @app.post("/chat/completions", response_model=ChatCompletionResponse)
    async def chat_completions(req: ChatCompletionRequest):
        """OpenAI-compatible chat completions endpoint."""
        
        if not req.messages:
            raise HTTPException(status_code=422, detail="Request must contain at least one message.")
            
        # Map to CAP AgentRequest
        cap_messages = [
            {"role": m.role, "content": m.content} for m in req.messages
        ]
        
        agent_req = AgentRequest(
            request_id=f"chatcmpl-{uuid.uuid4().hex}",
            messages=cap_messages,
            tools=None
        )
        
        try:
            response = orchestrator.execute(agent_req)
            
            # Map back to OpenAI Response
            content = "Success"
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
            if response.content is not None:
                content = response.content
            if hasattr(response, 'usage') and response.usage:
                prompt_tokens = response.usage.get("prompt_tokens", 0)
                completion_tokens = response.usage.get("completion_tokens", 0)
                total_tokens = response.usage.get("total_tokens", 0)
                
            choice = ChatCompletionChoice(
                index=0,
                message=APIMessage(
                    role="assistant",
                    content=content
                ),
                finish_reason="stop"
            )
            
            return ChatCompletionResponse(
                id=response.response_id,
                created=int(time.time()),
                model=req.model,
                choices=[choice],
                usage=ChatCompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
            )
        except NoProviderAvailableException as e:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "message": str(e) or "No provider available",
                        "type": "provider_unavailable",
                        "code": "no_provider_available"
                    }
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app

# Expose a default app instance for simple uvicorn running
app = create_app()
`,
    desc: 'Module chính của FastAPI, định nghĩa các endpoints REST API v1 tương thích OpenAI.'
  },
  'ai_gateway/main.py': {
    content: `"""
Main Entry Point for AI Gateway (Dự án Tiểu Tony - Phase 0)
"""
import sys
from core.config import get_config


def main():
    """Initialize system configuration and start gateway daemon."""
    config = get_config()
    
    print(f"[{config.app_name} v{config.version}] Initializing system configuration...")
    print(f"Mode: {config.environment} | Debug: {config.debug} | Host: {config.host}:{config.port}")
    print("Gateway started")


if __name__ == "__main__":
    main()
`,
    desc: 'Điểm bắt đầu thực thi chương trình. Nạp cấu hình và in thông báo khởi động "Gateway started".'
  },
  'ai_gateway/tests/__init__.py': {
    content: `"""
Tests module.
Unit tests and integration benchmarks for gateway components.
"""
`,
    desc: 'Package tests chứa các kịch bản kiểm thử tự động (Unit Test & Integration Test).'
  },
  'ai_gateway/tests/test_router.py': {
    content: `import pytest
from ai_gateway.registry.capability import (
    CapabilityRegistry, ProviderCapability, TaskRequirement, RoutingPolicy, TaskType
)
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException, RoutingDecision
from ai_gateway.adapters.base import BaseProvider
from typing import Dict, Any, Generator
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class MockProvider(BaseProvider):
    def __init__(self, name: str, caps: Dict[str, Any], healthy: bool = True):
        self.name = name
        self._caps = caps
        self._healthy = healthy
        
    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._caps

    def connect(self) -> bool: return True
    def chat(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]: pass # type: ignore
    def tool_call(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def health(self) -> Dict[str, Any]: return {"status": "ok" if self._healthy else "error"}
    def estimate_cost(self, request: AgentRequest) -> float: return 0.0

@pytest.fixture
def registry() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    # Gemini
    reg.register("gemini", MockProvider("gemini", {
        "coding": 10.0, "reasoning": 9.0, "translation": 8.0,
        "context_window": 1000000, "tool_call": True, "latency": 500.0, "cost": 5.0
    }))
    # OpenRouter
    reg.register("openrouter", MockProvider("openrouter", {
        "coding": 8.0, "reasoning": 8.0, "translation": 8.0,
        "context_window": 128000, "tool_call": True, "latency": 800.0, "cost": 2.0
    }))
    # Google Free
    reg.register("google_free", MockProvider("google_free", {
        "coding": 5.0, "reasoning": 5.0, "translation": 9.0,
        "context_window": 32000, "tool_call": False, "latency": 300.0, "cost": 0.0
    }))
    return reg

def test_1_refactor_codebase(registry: CapabilityRegistry):
    # Task: Refactor toàn bộ codebase -> coding cao, context lớn -> Expected: gemini
    req = TaskRequirement(task_type=TaskType.CODING, required_context=200000)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "gemini"
    assert "openrouter" in decision.excluded_providers
    assert decision.excluded_providers["openrouter"] == "Context window too small"
    assert "google_free" in decision.excluded_providers

def test_2_translate_low_cost(registry: CapabilityRegistry):
    # Task: Dịch tài liệu, chi phí thấp -> Expected: google_free
    req = TaskRequirement(task_type=TaskType.TRANSLATION)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.COST_FIRST)
    
    assert decision.provider_name == "google_free"

def test_3_gemini_out_of_quota(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.CODING)
    router = PolicyRouter(registry)
    quotas = {"gemini": 0.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "openrouter"
    assert "gemini" in decision.excluded_providers
    assert decision.excluded_providers["gemini"] == "Out of quota"

def test_4_quality_first_gemini_wins(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.REASONING)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "gemini"

def test_5_cost_first_google_free_wins(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.GENERAL)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.COST_FIRST)
    
    assert decision.provider_name == "google_free"

def test_6_context_exceeds_gemini_excluded(registry: CapabilityRegistry):
    # Context vượt giới hạn -> Gemini bị loại -> Expect NoProviderAvailableException
    req = TaskRequirement(task_type=TaskType.CODING, required_context=2000000)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, quotas, RoutingPolicy.BALANCED)

def test_7_tool_calling_required(registry: CapabilityRegistry):
    # Tool Calling Required -> Google Free bị loại
    req = TaskRequirement(task_type=TaskType.GENERAL, required_tools=True)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.BALANCED)
    
    assert "google_free" in decision.excluded_providers
    assert decision.excluded_providers["google_free"] == "Tool calling not supported"

def test_8_no_provider_available(registry: CapabilityRegistry):
    # Không còn Provider (e.g., budget is extremely low, no one meets it)
    req = TaskRequirement(task_type=TaskType.GENERAL, budget=-1.0)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, quotas, RoutingPolicy.BALANCED)

def test_9_tie_break():
    # Hai Provider cùng điểm -> Kiểm tra Tie Break (tên alphabet)
    reg = CapabilityRegistry()
    reg.register("beta_provider", MockProvider("beta", {"coding": 5, "cost": 5, "latency": 500}))
    reg.register("alpha_provider", MockProvider("alpha", {"coding": 5, "cost": 5, "latency": 500}))
    
    router = PolicyRouter(reg)
    req = TaskRequirement(task_type=TaskType.CODING)
    quotas = {"beta_provider": 10.0, "alpha_provider": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.BALANCED)
    
    assert decision.provider_name == "alpha_provider"

def test_10_registry_refresh(registry: CapabilityRegistry):
    # Registry refresh -> Provider mới được Router nhìn thấy
    req = TaskRequirement(task_type=TaskType.GENERAL)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0, "super_provider": 10.0}
    
    # First, gemini should win
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    assert decision.provider_name == "gemini"
    
    # Introduce new provider and refresh
    registry.refresh("super_provider", MockProvider("super", {
        "coding": 100.0, "reasoning": 100.0, "translation": 100.0, 
        "cost": 0.0, "latency": 1.0, "context_window": 10000000, "tool_call": True
    }))
    
    decision2 = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    assert decision2.provider_name == "super_provider"
`,
    desc: 'Unit test kiểm tra 10 kịch bản định tuyến của PolicyRouter.'
  },
  'ai_gateway/tests/test_circuit_breaker.py': {
    content: `import pytest
from ai_gateway.core.circuit_breaker import CircuitBreaker, CircuitState, Clock
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, RoutingPolicy, TaskType
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from typing import Dict, Any, Generator

class FakeClock(Clock):
    def __init__(self, initial_time: float = 0.0):
        self.current_time = initial_time

    def now(self) -> float:
        return self.current_time

    def advance(self, seconds: float):
        self.current_time += seconds

def test_1_default_available():
    cb = CircuitBreaker()
    assert cb.is_available("gemini") is True
    assert cb.get_state("gemini") == CircuitState.CLOSED

def test_2_trip_unavailable():
    cb = CircuitBreaker()
    cb.trip("gemini", reason="429 Too Many Requests")
    assert cb.is_available("gemini") is False
    assert cb.get_state("gemini") == CircuitState.OPEN

def test_3_fake_clock_advance():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("gemini", duration=30.0)
    assert cb.is_available("gemini") is False
    assert cb.get_state("gemini") == CircuitState.OPEN
    
    # Hết lock_until -> HALF_OPEN -> probe được phép
    clock.advance(31.0)
    # get_state triggers the transition
    assert cb.get_state("gemini") == CircuitState.HALF_OPEN
    
    # HALF_OPEN chỉ cho 1 probe
    assert cb.is_available("gemini") is True # First probe allowed
    assert cb.is_available("gemini") is False # Second probe denied
    assert cb.get_state("gemini") == CircuitState.HALF_OPEN

def test_half_open_success():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    cb.trip("gemini", duration=30.0)
    clock.advance(31.0)
    
    assert cb.is_available("gemini") is True # Probe
    
    # record_success -> CLOSED
    cb.record_success("gemini")
    assert cb.get_state("gemini") == CircuitState.CLOSED
    assert cb.is_available("gemini") is True

def test_half_open_failure():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    cb.trip("gemini", duration=30.0)
    clock.advance(31.0)
    
    assert cb.is_available("gemini") is True # Probe
    
    # record_failure -> OPEN
    cb.record_failure("gemini", duration=30.0)
    assert cb.get_state("gemini") == CircuitState.OPEN
    assert cb.is_available("gemini") is False

def test_4_reset():
    cb = CircuitBreaker()
    cb.trip("gemini")
    assert cb.is_available("gemini") is False
    
    cb.reset("gemini")
    assert cb.is_available("gemini") is True
    assert cb.get_state("gemini") == CircuitState.CLOSED

def test_5_unknown_provider_no_crash():
    cb = CircuitBreaker()
    cb.reset("unknown_provider")
    assert cb.is_available("unknown_provider") is True

class MockProvider(BaseProvider):
    def __init__(self, name: str, caps: Dict[str, Any], healthy: bool = True):
        self.name = name
        self._caps = caps
        self._healthy = healthy
        
    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._caps

    def connect(self) -> bool: return True
    def chat(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]: pass # type: ignore
    def tool_call(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def health(self) -> Dict[str, Any]: return {"status": "ok" if self._healthy else "error"}
    def estimate_cost(self, request: AgentRequest) -> float: return 0.0

@pytest.fixture
def registry_with_providers() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register("p1", MockProvider("p1", {"coding": 10}))
    reg.register("p2", MockProvider("p2", {"coding": 10}))
    reg.register("p3", MockProvider("p3", {"coding": 10}))
    return reg

def test_6_router_excludes_open_provider(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1") # Trip p1
    
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
    
    assert "p1" in decision.excluded_providers
    assert decision.excluded_providers["p1"] == "Circuit breaker OPEN"
    assert decision.provider_name in ["p2", "p3"]

def test_7_two_open_router_chooses_remaining(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1")
    cb.trip("p2")
    
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
    
    assert "p1" in decision.excluded_providers
    assert "p2" in decision.excluded_providers
    assert decision.provider_name == "p3"

def test_8_all_open_no_provider(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1")
    cb.trip("p2")
    cb.trip("p3")
    
    req = TaskRequirement(task_type=TaskType.CODING)
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
`,
    desc: 'Unit test kiểm tra kịch bản CircuitBreaker và Router.'
  },
  'ai_gateway/tests/test_executor.py': {
    content: `import pytest
import logging
from ai_gateway.core.executor import (
    ExecutionEngine, RateLimitException, ProviderUnavailableException, TimeoutException, UnknownProviderException, ValidationException
)
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class MockProvider:
    def __init__(self, name: str, exception_to_raise=None, response_to_return=None):
        self.name = name
        self.exception_to_raise = exception_to_raise
        self.response_to_return = response_to_return
        
    def chat(self, request: AgentRequest) -> AgentResponse:
        if self.exception_to_raise:
            raise self.exception_to_raise
        return self.response_to_return


def test_1_provider_success():
    req = AgentRequest(request_id="req1", messages=[])
    resp = AgentResponse(response_id="res1", content="ok", usage={})
    
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    result = engine.execute(req, provider=provider)
    assert result == resp

def test_2_provider_rate_limit_trips_cb():
    req = AgentRequest(request_id="req2", messages=[])
    provider = MockProvider("p1", exception_to_raise=RateLimitException("429"))
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(RateLimitException):
        engine.execute(req, provider=provider)
        
    assert cb.is_available("p1") is False

def test_3_provider_timeout_no_trip():
    req = AgentRequest(request_id="req3", messages=[])
    provider = MockProvider("p1", exception_to_raise=TimeoutException("timeout"))
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(TimeoutException):
        engine.execute(req, provider=provider)
        
    assert cb.is_available("p1") is True

def test_4_provider_none_raises_validation():
    req = AgentRequest(request_id="req4", messages=[])
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(ValidationException):
        engine.execute(req, provider=None)

def test_5_provider_returns_agent_response():
    req = AgentRequest(request_id="req5", messages=[])
    resp = AgentResponse(response_id="res5", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    result = engine.execute(req, provider=provider)
    assert isinstance(result, AgentResponse)
    assert result.content == "data"

def test_6_logger_called(caplog):
    req = AgentRequest(request_id="req6", messages=[])
    resp = AgentResponse(response_id="res6", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.INFO)
    engine = ExecutionEngine(circuit_breaker=cb, logger=test_logger) # type: ignore
    with caplog.at_level(logging.INFO, logger="test_logger"):
        engine.execute(req, provider=provider)
        
    assert "Executing request req6 with provider p1" in caplog.text
    assert "Request req6 succeeded" in caplog.text


def test_7_provider_timeout_in_half_open_trips_cb():
    from ai_gateway.core.circuit_breaker import CircuitState, Clock
    
    class FakeClock(Clock):
        def __init__(self):
            self.current_time = 0.0
        def now(self) -> float:
            return self.current_time
        def advance(self, seconds: float):
            self.current_time += seconds
            
    clock = FakeClock()
    req = AgentRequest(request_id="req7", messages=[])
    provider = MockProvider("p1", exception_to_raise=TimeoutException("timeout"))
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("p1", duration=30.0)
    clock.advance(31.0)
    
    # State is now HALF_OPEN
    assert cb.get_state("p1") == CircuitState.HALF_OPEN
    
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(TimeoutException):
        engine.execute(req, provider=provider)
        
    # Should be back to OPEN
    assert cb.get_state("p1") == CircuitState.OPEN

def test_8_provider_success_records_success():
    from ai_gateway.core.circuit_breaker import CircuitState, Clock
    
    class FakeClock(Clock):
        def __init__(self):
            self.current_time = 0.0
        def now(self) -> float:
            return self.current_time
        def advance(self, seconds: float):
            self.current_time += seconds
            
    clock = FakeClock()
    req = AgentRequest(request_id="req8", messages=[])
    resp = AgentResponse(response_id="res8", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("p1", duration=30.0)
    clock.advance(31.0)
    
    assert cb.get_state("p1") == CircuitState.HALF_OPEN
    
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    engine.execute(req, provider=provider)
        
    # Should be CLOSED now
    assert cb.get_state("p1") == CircuitState.CLOSED
`,
    desc: 'Unit test kiểm tra 6 kịch bản Execution Engine.'
  },
  'ai_gateway/tests/test_orchestrator.py': {
    content: `import pytest
import logging
from ai_gateway.core.orchestrator import ExecutionOrchestrator
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.router import RoutingDecision


class MockRouter:
    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        return RoutingDecision(provider_name="p1", provider="mock_prov", score=1.0, reason="", excluded_providers={}, policy_used=policy or RoutingPolicy.BALANCED, timestamp=0.0)

class MockExecutionEngine:
    def __init__(self, response=None, exception=None):
        self.response = response
        self.exception = exception

    def execute(self, request, provider=None):
        if self.exception:
            raise self.exception
        return self.response

def test_1_execution_success():
    req = AgentRequest(request_id="req1", messages=[])
    resp = AgentResponse(response_id="res1", content="ok", usage={})
    engine = MockExecutionEngine(response=resp)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    result = orchestrator.execute(req)
    assert result == resp

def test_2_execution_exception_raised():
    req = AgentRequest(request_id="req2", messages=[])
    engine = MockExecutionEngine(exception=ValueError("engine failed"))
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    with pytest.raises(ValueError):
        orchestrator.execute(req)

def test_3_logger_called(caplog):
    req = AgentRequest(request_id="req3", messages=[])
    resp = AgentResponse(response_id="res3", content="ok", usage={})
    engine = MockExecutionEngine(response=resp)
    test_logger = logging.getLogger("orch_test_logger")
    test_logger.setLevel(logging.INFO)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router, logger=test_logger) # type: ignore
    
    with caplog.at_level(logging.INFO, logger="orch_test_logger"):
        orchestrator.execute(req)
        
    assert "Orchestrator started for request req3" in caplog.text
    assert "Orchestrator success for request req3" in caplog.text

def test_4_agent_response_unchanged():
    req = AgentRequest(request_id="req4", messages=[])
    resp = AgentResponse(response_id="res4", content="data", usage={"tokens": 10})
    engine = MockExecutionEngine(response=resp)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    result = orchestrator.execute(req)
    assert result.content == "data"
    assert result.usage["tokens"] == 10
`,
    desc: 'Unit test kiểm tra 4 kịch bản Execution Orchestrator.'
  },
  'ai_gateway/tests/test_fallback.py': {
    content: `import pytest
from ai_gateway.core.fallback import ProviderFallbackStrategy, NoFallbackStrategy
from ai_gateway.core.router import PolicyRouter, RoutingDecision, NoProviderAvailableException
from ai_gateway.core.executor import (
    ProviderUnavailableException,
    CircuitOpenException,
    AuthenticationException,
    UnknownProviderException,
    ExecutionEngine
)
from ai_gateway.protocols.cap import AgentResponse

class MockProvider:
    def __init__(self, name):
        self.name = name

class MockRouter:
    def __init__(self, sequence):
        self.sequence = sequence
        self.call_count = 0
        self.last_context = None

    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        self.last_context = context
        index = self.call_count
        self.call_count += 1
        if index >= len(self.sequence):
            raise NoProviderAvailableException("No more providers")
        
        provider_name = self.sequence[index]
        
        if not provider_name:
            raise NoProviderAvailableException("No provider")
            
        return RoutingDecision(
            provider_name=provider_name,
            provider=MockProvider(provider_name),
            score=10.0,
            reason="test",
            excluded_providers={},
            policy_used=policy or RoutingPolicy.BALANCED,
            timestamp=0.0
        )

def test_1_first_provider_success():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        return AgentResponse(response_id="1", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p1"
    assert router.call_count == 1

def test_2_first_provider_unavailable_fallback_to_second():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        return AgentResponse(response_id="2", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p2"
    assert router.call_count == 2
    assert "p1" in router.last_context["excluded_providers"]

def test_3_first_provider_circuit_open_fallback():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise CircuitOpenException("p1 open")
        return AgentResponse(response_id="3", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p2"
    assert router.call_count == 2
    assert "p1" in router.last_context["excluded_providers"]

def test_4_first_provider_auth_exception_no_fallback():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise AuthenticationException("p1 auth failed")
        return AgentResponse(response_id="4", content="ok", usage={})
        
    with pytest.raises(AuthenticationException):
        fallback.execute(op, context={})
        
    assert router.call_count == 1

def test_5_no_provider_available():
    router = MockRouter([])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        pass
        
    with pytest.raises(NoProviderAvailableException):
        fallback.execute(op, context={})

def test_6_both_providers_fail():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        if provider.name == "p2":
            raise CircuitOpenException("p2 open")
            
    with pytest.raises(NoProviderAvailableException):
        fallback.execute(op, context={})
        
    assert router.call_count == 3  # Try p1, try p2, then empty

def test_7_router_does_not_pick_failed_provider():
    # Because we check the excluded_providers is updated correctly.
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        return AgentResponse(response_id="7", content="ok", usage={})
        
    fallback.execute(op, context={"excluded_providers": []})
    
    assert "p1" in router.last_context["excluded_providers"]
`,
    desc: 'Unit test cho Fallback Strategy.'
  },
  'ai_gateway/tests/test_retry.py': {
    content: `import pytest
from ai_gateway.core.retry import (
    NoRetryStrategy, 
    FixedRetryStrategy,
    AuthenticationException
)
from ai_gateway.core.executor import (
    TimeoutException,
    RateLimitException,
    ProviderUnavailableException,
    UnknownProviderException
)
from ai_gateway.protocols.cap import AgentResponse

def test_1_no_retry_success():
    strategy = NoRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        return AgentResponse(response_id="1", content="ok", usage={})
        
    res = strategy.execute(op)
    assert res.content == "ok"
    assert calls == 1

def test_2_fixed_retry_timeout_success():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutException("timeout")
        return AgentResponse(response_id="2", content="ok", usage={})
        
    res = strategy.execute(op)
    assert res.content == "ok"
    assert calls == 3

def test_3_fixed_retry_timeout_fails():
    strategy = FixedRetryStrategy(max_retries=3)
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise TimeoutException("timeout")
        
    with pytest.raises(TimeoutException):
        strategy.execute(op)
        
    assert calls == 4  # Initial call + 3 retries

def test_4_rate_limit_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise RateLimitException("rate limit")
        
    with pytest.raises(RateLimitException):
        strategy.execute(op)
        
    assert calls == 1

def test_5_provider_unavailable_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise ProviderUnavailableException("unavailable")
        
    with pytest.raises(ProviderUnavailableException):
        strategy.execute(op)
        
    assert calls == 1

def test_6_unknown_provider_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise UnknownProviderException("unknown")
        
    with pytest.raises(UnknownProviderException):
        strategy.execute(op)
        
    assert calls == 1
    
def test_7_orchestrator_uses_retry_strategy():
    from ai_gateway.core.orchestrator import ExecutionOrchestrator
    from ai_gateway.protocols.cap import AgentRequest
    from ai_gateway.core.executor import ExecutionEngine
    
    class MockEngine:
        def execute(self, *args, **kwargs):
            return AgentResponse(response_id="123", content="engine_result", usage={})
            
    class MockRouter:
        def route(self, *args, **kwargs):
            from ai_gateway.core.router import RoutingDecision
            from ai_gateway.registry.capability import RoutingPolicy
            return RoutingDecision(
                provider_name="p1", 
                provider=None, 
                score=1.0, 
                reason="", 
                excluded_providers={}, 
                policy_used=RoutingPolicy.BALANCED, 
                timestamp=0.0
            )
            
    class MockStrategy(NoRetryStrategy):
        def __init__(self):
            self.called = False
            
        def execute(self, op):
            self.called = True
            return op()
            
    strategy = MockStrategy()
    orch = ExecutionOrchestrator(engine=MockEngine(), router=MockRouter(), retry_strategy=strategy) # type: ignore
    req = AgentRequest(request_id="test", messages=[])
    
    res = orch.execute(req)
    assert strategy.called is True
    assert res.content == "engine_result"
`,
    desc: 'Unit test cho Retry Strategy.'
  },
  'ai_gateway/tests/test_state.py': {
    content: `import pytest
from ai_gateway.core.state import StateManager, StateSnapshot

def test_state_manager_initialization():
    manager = StateManager("/tmp/workdir")
    assert manager.working_directory == "/tmp/workdir"
    assert manager.variables == {}
    assert "git_diff" in manager.current_state
    assert "files" in manager.current_state
    assert "conversation_summary" in manager.current_state

def test_update_variable():
    manager = StateManager()
    manager.update_variable("api_key", "secret123")
    assert manager.variables["api_key"] == "secret123"
    
    manager.update_variable("api_key", "new_secret")
    assert manager.variables["api_key"] == "new_secret"

def test_save_and_load_snapshot():
    manager = StateManager("/app")
    manager.update_variable("theme", "dark")
    manager.current_state["files"] = ["main.py"]
    manager.current_state["git_diff"] = "+ print('hello')"
    
    # Save the snapshot
    snapshot = manager.save_snapshot()
    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.variables["theme"] == "dark"
    assert "main.py" in snapshot.current_state["files"]
    
    # Modify state after snapshot
    manager.update_variable("theme", "light")
    manager.current_state["files"] = ["main.py", "utils.py"]
    manager.current_state["git_diff"] = ""
    
    # Verify modification applied
    assert manager.variables["theme"] == "light"
    assert len(manager.current_state["files"]) == 2
    
    # Load snapshot to restore state
    manager.load_snapshot(snapshot.snapshot_id)
    
    assert manager.working_directory == "/app"
    assert manager.variables["theme"] == "dark"
    assert manager.current_state["files"] == ["main.py"]
    assert manager.current_state["git_diff"] == "+ print('hello')"

def test_load_invalid_snapshot():
    manager = StateManager()
    with pytest.raises(ValueError, match="not found"):
        manager.load_snapshot("invalid_snapshot_id")
`,
    desc: 'Unit test kiểm tra chức năng lưu, khôi phục snapshot và quản lý biến môi trường của StateManager.'
  },
  'ai_gateway/tests/test_compressor.py': {
    content: `import pytest
from ai_gateway.core.compressor import MessageCompressor

def test_token_estimation():
    compressor = MessageCompressor(chars_per_token=4.0)
    assert compressor._estimate_tokens("1234") == 1
    assert compressor._estimate_tokens("12345") == 2
    assert compressor._estimate_tokens("") == 0

def test_summarize_long_text():
    compressor = MessageCompressor()
    text = "A" * 1000
    summarized = compressor._summarize_long_text(text, max_chars=100)
    assert len(summarized) <= 150  # 100 chars + compression notice length
    assert summarized.startswith("A")
    assert summarized.endswith("A")
    assert "[CONTENT COMPRESSED]" in summarized

def test_compress_under_limit():
    compressor = MessageCompressor()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    # Limit is very high, no compression expected
    compressed = compressor.compress(messages, max_tokens=1000)
    assert len(compressed) == 2
    assert compressed[0]["content"] == "You are a helpful assistant."
    assert compressed[1]["content"] == "Hello!"

def test_compress_over_limit():
    compressor = MessageCompressor(chars_per_token=4.0)
    
    # Create a large log message
    huge_log = "ERROR: Something went wrong\\n" * 1000  # ~28k chars -> ~7k tokens
    
    messages = [
        {"role": "system", "content": "System prompt core instructions"},
        {"role": "user", "content": "Run this task"},
        {"role": "assistant", "content": "Running..."},
        {"role": "user", "content": huge_log},
        {"role": "assistant", "content": "Failed."},
        {"role": "user", "content": "What happened?"}
    ]
    
    # We want to compress to max 100 tokens (~400 chars)
    compressed = compressor.compress(messages, max_tokens=100)
    
    # Ensure structure is maintained
    assert len(compressed) == len(messages)
    
    # System should be untouched
    assert compressed[0]["content"] == messages[0]["content"]
    
    # Last 2 non-system messages (Failed, What happened?) should be untouched
    assert compressed[-1]["content"] == "What happened?"
    assert compressed[-2]["content"] == "Failed."
    
    # The huge log should be compressed
    assert len(compressed[3]["content"]) < len(huge_log)
    assert "[CONTENT COMPRESSED]" in compressed[3]["content"]
    
    # Calculate total tokens after compression to ensure it dropped significantly
    total_tokens_after = sum(compressor._estimate_message_tokens(m) for m in compressed)
    
    # It might not be exactly 100 due to fixed size of protected messages and compression strings,
    # but it should be way less than original
    assert total_tokens_after < 250
`,
    desc: 'Unit test kiểm thử giải thuật nén nội dung hội thoại bảo toàn system prompt và tin nhắn gần nhất.'
  },
  'ai_gateway/tests/test_api.py': {
    content: `import pytest
from fastapi.testclient import TestClient
from ai_gateway.api.app import create_app
from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.core.router import NoProviderAvailableException

# We'll use a mocked orchestrator and registry for tests
class MockRegistry:
    def all(self):
        return {"mock-provider": {}}

class MockEmptyRegistry:
    def all(self):
        return {}

class MockOrchestrator:
    def execute(self, req):
        return AgentResponse(
            response_id="test-123",
            content="Hello there!",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

class MockFailingOrchestrator:
    def execute(self, req):
        raise NoProviderAvailableException("All fallback providers exhausted.")

app = create_app(orchestrator=MockOrchestrator(), registry=MockRegistry())
client = TestClient(app)

empty_app = create_app(orchestrator=MockFailingOrchestrator(), registry=MockEmptyRegistry())
empty_client = TestClient(empty_app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ai_gateway"

def test_list_models():
    response = client.get("/models")
    assert response.status_code == 200
    json_resp = response.json()
    assert "data" in json_resp
    assert isinstance(json_resp["data"], list)
    assert len(json_resp["data"]) > 0

def test_list_models_empty():
    response = empty_client.get("/models")
    assert response.status_code == 200
    json_resp = response.json()
    assert "data" in json_resp
    assert len(json_resp["data"]) == 0

def test_chat_completions_missing_messages():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": []
    }
    response = client.post("/chat/completions", json=payload)
    assert response.status_code == 422

def test_chat_completions_success():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = client.post("/chat/completions", json=payload)
    assert response.status_code == 200
    
    json_resp = response.json()
    assert "choices" in json_resp
    assert len(json_resp["choices"]) > 0
    assert json_resp["choices"][0]["message"]["content"] == "Hello there!"
    assert json_resp["usage"]["total_tokens"] == 30
    assert json_resp["id"] == "test-123"

def test_chat_completions_no_provider():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = empty_client.post("/chat/completions", json=payload)
    assert response.status_code == 503
    json_resp = response.json()
    assert "error" in json_resp
    assert json_resp["error"]["type"] == "provider_unavailable"
    assert json_resp["error"]["code"] == "no_provider_available"

`,
    desc: 'File test mock cho API layer, kiểm tra validation, response và schema mapping.'
  }
};

export const FILE_TREE: FileNode[] = [
  { path: 'AGENTS.md', name: 'AGENTS.md', type: 'file', description: PROJECT_FILES['AGENTS.md'].desc },
  { path: 'ROADMAP.md', name: 'ROADMAP.md', type: 'file', description: PROJECT_FILES['ROADMAP.md'].desc },
  { path: 'TECH_DEBT.md', name: 'TECH_DEBT.md', type: 'file', description: PROJECT_FILES['TECH_DEBT.md'].desc },
  { path: 'REPORT_SPRINT_15.md', name: 'REPORT_SPRINT_15.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_15.md'].desc },
  { path: 'REPORT_SPRINT_16.md', name: 'REPORT_SPRINT_16.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_16.md'].desc },
  { path: 'REPORT_SPRINT_17.md', name: 'REPORT_SPRINT_17.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_17.md'].desc },
  { path: 'ai_gateway/core/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/__init__.py'].desc },
  { path: 'ai_gateway/core/config.py', name: 'config.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/config.py'].desc },
  { path: 'ai_gateway/core/router.py', name: 'router.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/router.py'].desc },
  { path: 'ai_gateway/core/circuit_breaker.py', name: 'circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/circuit_breaker.py'].desc },
  { path: 'ai_gateway/core/executor.py', name: 'executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/executor.py'].desc },
  { path: 'ai_gateway/core/orchestrator.py', name: 'orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/orchestrator.py'].desc },
  { path: 'ai_gateway/core/fallback.py', name: 'fallback.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/fallback.py'].desc },
  { path: 'ai_gateway/core/retry.py', name: 'retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/retry.py'].desc },
  { path: 'ai_gateway/core/state.py', name: 'state.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/state.py'].desc },
  { path: 'ai_gateway/core/compressor.py', name: 'compressor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/compressor.py'].desc },
  { path: 'ai_gateway/adapters/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/adapters/__init__.py'].desc },
  { path: 'ai_gateway/adapters/base.py', name: 'base.py', type: 'file', description: PROJECT_FILES['ai_gateway/adapters/base.py'].desc },
  { path: 'ai_gateway/adapters/gemini.py', name: 'gemini.py', type: 'file', description: PROJECT_FILES['ai_gateway/adapters/gemini.py'].desc },
  { path: 'ai_gateway/protocols/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/protocols/__init__.py'].desc },
  { path: 'ai_gateway/protocols/cap.py', name: 'cap.py', type: 'file', description: PROJECT_FILES['ai_gateway/protocols/cap.py'].desc },
  { path: 'ai_gateway/registry/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/registry/__init__.py'].desc },
  { path: 'ai_gateway/registry/capability.py', name: 'capability.py', type: 'file', description: PROJECT_FILES['ai_gateway/registry/capability.py'].desc },
  { path: 'ai_gateway/api/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/api/__init__.py'].desc },
  { path: 'ai_gateway/api/schemas.py', name: 'schemas.py', type: 'file', description: PROJECT_FILES['ai_gateway/api/schemas.py'].desc },
  { path: 'ai_gateway/api/app.py', name: 'app.py', type: 'file', description: PROJECT_FILES['ai_gateway/api/app.py'].desc },
  { path: 'ai_gateway/main.py', name: 'main.py', type: 'file', description: PROJECT_FILES['ai_gateway/main.py'].desc },
  { path: 'ai_gateway/tests/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/__init__.py'].desc },
  { path: 'ai_gateway/tests/test_router.py', name: 'test_router.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_router.py'].desc },
  { path: 'ai_gateway/tests/test_circuit_breaker.py', name: 'test_circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_circuit_breaker.py'].desc },
  { path: 'ai_gateway/tests/test_executor.py', name: 'test_executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_executor.py'].desc },
  { path: 'ai_gateway/tests/test_orchestrator.py', name: 'test_orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_orchestrator.py'].desc },
  { path: 'ai_gateway/tests/test_fallback.py', name: 'test_fallback.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_fallback.py'].desc },
  { path: 'ai_gateway/tests/test_retry.py', name: 'test_retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_retry.py'].desc },
  { path: 'ai_gateway/tests/test_state.py', name: 'test_state.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_state.py'].desc },
  { path: 'ai_gateway/tests/test_compressor.py', name: 'test_compressor.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_compressor.py'].desc },
  { path: 'ai_gateway/tests/test_api.py', name: 'test_api.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_api.py'].desc }
];
