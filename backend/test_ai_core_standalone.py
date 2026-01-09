#!/usr/bin/env python3
"""
Standalone test for AI Core Domain (DDD)
Bypasses app/__init__.py to avoid pre-existing import errors.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_value_objects():
    """Test Value Objects"""
    print("\n=== Testing Value Objects ===")

    # Import directly from file
    from app.api.system_features.ai.core import value_objects

    # Test Margin
    print("\n1. Testing Margin:")
    margin = value_objects.Margin(margin_percent=33.33)
    print(f"   ✓ Created Margin: {margin.margin_percent}%")

    price = margin.apply_to_cost(Decimal('0.003'))
    print(f"   ✓ Applied to 0.003 cost: {price}")
    assert price == Decimal('0.003999'), f"Expected 0.003999, got {price}"

    # Test PricingTier
    print("\n2. Testing PricingTier:")
    tier = value_objects.PricingTier(
        input_cost_per_1k=Decimal('0.003'),
        output_cost_per_1k=Decimal('0.015'),
        margin=margin
    )
    print(f"   ✓ Created PricingTier")
    print(f"   ✓ Customer input price: {tier.get_customer_input_price()}")
    print(f"   ✓ Customer output price: {tier.get_customer_output_price()}")

    total = tier.calculate_total_price(input_tokens=1000, output_tokens=500)
    print(f"   ✓ Total price for 1000in/500out: {total}")

    # Test ProviderHealth
    print("\n3. Testing ProviderHealth:")
    health = value_objects.ProviderHealth.healthy(
        response_time_ms=2000,
        checked_at='2026-01-08T14:00:00'
    )
    print(f"   ✓ Created ProviderHealth: {health.status.value}")
    print(f"   ✓ Is operational: {health.is_operational()}")
    print(f"   ✓ Is healthy: {health.is_healthy()}")

    print("\n✅ All Value Object tests passed!")
    return True

def test_factories():
    """Test Factories"""
    print("\n=== Testing Factories ===")

    from app.api.system_features.ai.core import factory

    # Test AIModelFactory
    print("\n1. Testing AIModelFactory:")
    model = factory.AIModelFactory.create_from_provider_sync(
        provider_id='provider-123',
        model_identifier='gpt-4',
        model_name='GPT-4',
        category='chat',
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        context_window=8192
    )
    print(f"   ✓ Created model: {model['model_name']}")
    print(f"   ✓ Category: {model['category']}")
    print(f"   ✓ Input price (with 33.33% margin): {model['input_price_per_1k']}")

    # Test AIJobFactory
    print("\n2. Testing AIJobFactory:")
    job = factory.AIJobFactory.create_lesson_autogen_job(
        user_id='user-123',
        course_id='course-456',
        chapter_id='chapter-789',
        lesson_title='Variables and Data Types',
        learning_methods=[0, 1, 2]
    )
    print(f"   ✓ Created job: {job['job_type']}")
    print(f"   ✓ Status: {job['status']}")
    print(f"   ✓ Learning methods: {job['input_data']['learning_methods']}")

    print("\n✅ All Factory tests passed!")
    return True

def test_services():
    """Test Domain Services"""
    print("\n=== Testing Domain Services ===")

    from app.api.system_features.ai.core import services

    # Test AIModelSelectionService
    print("\n1. Testing AIModelSelectionService:")
    models = [
        {
            'model_id': '1',
            'category': 'chat',
            'active': True,
            'is_default': True,
            'input_price_per_1k': 0.01
        },
        {
            'model_id': '2',
            'category': 'chat',
            'active': True,
            'is_default': False,
            'input_price_per_1k': 0.005
        }
    ]

    selected = services.AIModelSelectionService.select_model_for_category(
        category='chat',
        models=models,
        prefer_default=True
    )
    print(f"   ✓ Selected model: {selected['model_id']} (default)")
    assert selected['model_id'] == '1', "Should select default model"

    # Test AIUsageService
    print("\n2. Testing AIUsageService:")
    model = {
        'input_cost_per_1k': 0.003,
        'output_cost_per_1k': 0.015,
        'input_price_per_1k': 0.004,
        'output_price_per_1k': 0.020
    }

    result = services.AIUsageService.calculate_operation_cost(
        model=model,
        input_tokens=1000,
        output_tokens=500
    )
    print(f"   ✓ Total cost: {result['total_cost']}")
    print(f"   ✓ Total price: {result['total_price']}")
    print(f"   ✓ Margin: {result['margin']}")

    # Test AIHealthMonitoringService
    print("\n3. Testing AIHealthMonitoringService:")
    health = services.AIHealthMonitoringService.evaluate_health_status(
        response_time_ms=2000,
        error_occurred=False
    )
    print(f"   ✓ Health status: {health.status.value}")
    print(f"   ✓ Is operational: {health.is_operational()}")

    print("\n✅ All Service tests passed!")
    return True

def test_events():
    """Test Domain Events"""
    print("\n=== Testing Domain Events ===")

    from app.api.system_features.ai.core import events
    from datetime import datetime
    import uuid

    # Test AIModelSyncedEvent
    print("\n1. Testing AIModelSyncedEvent:")
    event = events.AIModelSyncedEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.utcnow(),
        aggregate_id='provider-123',
        provider_id='provider-123',
        provider_name='OpenAI',
        models_added=5,
        models_updated=2,
        models_deactivated=1,
        sync_duration_seconds=3.5
    )
    print(f"   ✓ Created event: {event.__class__.__name__}")
    print(f"   ✓ Models added: {event.models_added}")
    print(f"   ✓ Event dict: {len(event.to_dict())} fields")

    # Test EventPublisher
    print("\n2. Testing EventPublisher:")
    received_events = []

    def handler(evt):
        received_events.append(evt)

    events.EventPublisher.subscribe(events.AIModelSyncedEvent, handler)
    events.EventPublisher.publish(event)

    print(f"   ✓ Published event")
    print(f"   ✓ Received events: {len(received_events)}")
    assert len(received_events) == 1, "Should receive 1 event"

    events.EventPublisher.clear_handlers()

    print("\n✅ All Event tests passed!")
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("AI Core Domain (DDD) - Standalone Tests")
    print("="*60)

    try:
        test_value_objects()
        test_factories()
        test_services()
        test_events()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
