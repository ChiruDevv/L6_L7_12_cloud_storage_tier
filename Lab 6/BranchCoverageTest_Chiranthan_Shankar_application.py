"""Branch-coverage tests for billing decisions and replication monitoring."""

import pytest

from cloud_storage_tier import monitor_replication_latency, process_storage_tenants


def tenant(tier="hot", buckets=None, **overrides):
    data = {"account_active": True, "tier": tier, "buckets": buckets or []}
    data.update(overrides)
    return data


def bucket(size=100, corrupted=False, egress=0):
    return {"size_gb": size, "corrupted": corrupted, "egress_gb": egress}


def test_validation_short_circuits_and_rejects_each_invalid_input():
    with pytest.raises(ValueError):
        process_storage_tenants(None, -1)
    with pytest.raises(ValueError):
        process_storage_tenants([], -1)
    assert process_storage_tenants([], 0) == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_inactive_unknown_tier_and_missing_defaults_are_handled():
    tenants = [
        {"account_active": False, "tier": "hot", "buckets": [bucket()]},
        tenant("premium", [bucket()]),
        {"account_active": True},
    ]
    assert process_storage_tenants(tenants, 0) == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_each_tier_valid_invalid_bucket_corruption_and_threshold_path():
    tenants = [
        tenant("hot", [bucket(0), bucket(500), bucket(501), bucket(100, True)]),
        tenant("cool", [bucket(100, True), bucket(100, egress=101)]),
        tenant("archive", [bucket(100, True), bucket(100)]),
    ]
    result = process_storage_tenants(tenants, 0)
    # The archive corruption resets its storage charge and stops later bucket processing.
    assert result == {"total_billed": 25.35, "status": "BILLED"}


def test_archive_corruption_break_skips_rest_of_tenant_buckets():
    assert process_storage_tenants(
        [tenant("archive", [bucket(100), bucket(100, True), bucket(100, egress=500)])], 0
    ) == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_backup_fee_can_make_empty_bucket_tenant_billable():
    assert process_storage_tenants([tenant("hot", [], has_backup_vault=True)], 4.5) == {
        "total_billed": 4.5, "status": "BILLED"
    }


def test_more_than_four_flagged_buckets_returns_audit_status():
    tenants = [tenant("invalid", []) for _ in range(5)]
    assert process_storage_tenants(tenants, 0) == {"total_billed": 0.0, "status": "AUDIT_FLAGGED"}


def test_latency_threshold_streak_reset_and_multi_node_iteration():
    assert monitor_replication_latency([[201, 200, 201], [], [200, 201]]) == "SYNCED"
    assert monitor_replication_latency([[201], [202, 203]]) == "SYNC_LAG_ALERT"



def test_empty_replication_matrix_has_no_data():
    assert monitor_replication_latency([]) == "NO_DATA"
