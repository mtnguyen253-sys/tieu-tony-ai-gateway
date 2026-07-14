import pytest
from ai_gateway.core.task_classifier import TaskClassifier, TaskComplexity
from ai_gateway.protocols.cap import AgentRequest
from ai_gateway.core.routing_policy_matrix import RoutingPolicyMatrix, ModelTier

@pytest.fixture
def classifier():
    return TaskClassifier()

@pytest.fixture
def policy_matrix():
    return RoutingPolicyMatrix()

def test_classifier_simple(classifier):
    req = AgentRequest(request_id="1", messages=[{"role": "user", "content": "Please translate this text to French"}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.SIMPLE

def test_classifier_simple_commit_msg(classifier):
    req = AgentRequest(request_id="2", messages=[{"role": "user", "content": "write a commit message for these changes"}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.SIMPLE

def test_classifier_complex(classifier):
    req = AgentRequest(request_id="3", messages=[{"role": "user", "content": "Let's refactor core routing logic and add a circuit breaker"}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.COMPLEX

def test_classifier_long_context(classifier):
    # Rough estimate is 1 token per 4 chars
    # Create a string of length > 32000 chars
    long_content = "a" * 33000
    req = AgentRequest(request_id="4", messages=[{"role": "user", "content": long_content}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.LONG_CONTEXT

def test_classifier_critical(classifier):
    req = AgentRequest(request_id="5", messages=[{"role": "user", "content": "delete all files in the current directory and push to main"}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.CRITICAL

def test_classifier_critical_secret(classifier):
    req = AgentRequest(request_id="6", messages=[{"role": "user", "content": "what is my api_key?"}])
    cls = classifier.classify(req)
    assert cls.complexity == TaskComplexity.CRITICAL

def test_policy_matrix_simple(classifier, policy_matrix):
    req = AgentRequest(request_id="1", messages=[{"role": "user", "content": "translate hello"}])
    cls = classifier.classify(req)
    policy = policy_matrix.get_policy(cls)
    assert policy.recommended_tier == ModelTier.CHEAP

def test_policy_matrix_complex(classifier, policy_matrix):
    req = AgentRequest(request_id="3", messages=[{"role": "user", "content": "refactor core logic"}])
    cls = classifier.classify(req)
    policy = policy_matrix.get_policy(cls)
    assert policy.recommended_tier == ModelTier.STRONG

def test_policy_matrix_long_context(classifier, policy_matrix):
    long_content = "a" * 33000
    req = AgentRequest(request_id="4", messages=[{"role": "user", "content": long_content}])
    cls = classifier.classify(req)
    policy = policy_matrix.get_policy(cls)
    assert policy.recommended_tier == ModelTier.LONG_CONTEXT
    assert policy.prefer_cache == True
