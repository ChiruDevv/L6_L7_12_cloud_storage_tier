"""Line-coverage tests for the cloud storage tier assignment."""

import pytest

from cloud_storage_tier import monitor_replication_latency, process_storage_tenants


def test_single_active_hot_tenant():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": False,
        "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 50}],
    }]
    assert process_storage_tenants(tenants, 10.0) == {"total_billed": 2.5, "status": "BILLED"}


def test_all_storage_tiers_and_large_bucket_discount():
    tenants = [
        {"account_active": True, "tier": "hot", "buckets": [{"size_gb": 501}]},
        {"account_active": True, "tier": "cool", "buckets": [{"size_gb": 100}]},
        {"account_active": True, "tier": "archive", "buckets": [{"size_gb": 100}]},
    ]
    assert process_storage_tenants(tenants, 10) == {"total_billed": 13.27, "status": "BILLED"}


def test_backup_fee_and_egress_overage_are_billed():
    tenants = [{
        "account_active": True,
        "tier": "hot",
        "has_backup_vault": True,
        "buckets": [{"size_gb": 100, "egress_gb": 125}],
    }]
    assert process_storage_tenants(tenants, 10) == {"total_billed": 14.5, "status": "BILLED"}


def test_empty_and_inactive_usage_returns_zero():
    assert process_storage_tenants([], 10) == {"total_billed": 0.0, "status": "ZERO_USAGE"}
    assert process_storage_tenants([{"account_active": False}], 10) == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_invalid_arguments_raise_value_error():
    with pytest.raises(ValueError):
        process_storage_tenants({}, 10)
    with pytest.raises(ValueError):
        process_storage_tenants([], -1)


def test_replication_latency_empty_and_synced_inputs():
    assert monitor_replication_latency([]) == "NO_DATA"
    assert monitor_replication_latency([[200, 201, 100], [1, 250, 200]]) == "SYNCED"


def test_replication_latency_two_consecutive_slow_samples_alert():
    assert monitor_replication_latency([[201, 202]]) == "SYNC_LAG_ALERT"



def test_invalid_tier_bucket_size_and_corruption_are_flagged():
    tenants = [
        {"account_active": True, "tier": "unknown", "buckets": []},
        {"account_active": True, "tier": "hot", "buckets": [
            {"size_gb": 0},
            {"size_gb": 100, "corrupted": True},
        ]},
        {"account_active": True, "tier": "archive", "buckets": [
            {"size_gb": 100, "corrupted": True},
        ]},
    ]
    result = process_storage_tenants(tenants, 0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_many_invalid_tiers_trigger_audit_flag():
    tenants = [{"account_active": True, "tier": "unknown"} for _ in range(5)]
    assert process_storage_tenants(tenants, 0) == {
        "total_billed": 0.0, "status": "AUDIT_FLAGGED"
    }
