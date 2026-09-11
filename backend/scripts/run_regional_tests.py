import sys
sys.path.insert(0, ".")

import tests.unit.test_regional_intelligence as t

tests = [
    t.test_kerala_district_direct_mention,
    t.test_kerala_district_alias_resolution,
    t.test_all_14_kerala_districts_recognized,
    t.test_india_region_classification,
    t.test_global_region_classification,
    t.test_importance_scorer_kerala_boost,
    t.test_importance_scorer_breaking_classification,
    t.test_importance_scorer_low_priority_lifestyle,
    t.test_ssrf_validator_blocks_private_ip,
    t.test_ssrf_validator_blocks_localhost,
    t.test_ssrf_validator_blocks_cloud_metadata,
    t.test_ssrf_validator_blocks_bad_schemes,
    t.test_ssrf_validator_allows_valid_https_url,
    t.test_sources_yaml_loads_kerala_and_india_regions,
]

passed = 0
failed = 0
for fn in tests:
    try:
        fn()
        print(f"PASS: {fn.__name__}", flush=True)
        passed += 1
    except Exception as e:
        print(f"FAIL: {fn.__name__} -> {e}", flush=True)
        failed += 1

print(f"\nResult: {passed} passed, {failed} failed out of {len(tests)} tests.", flush=True)
if failed > 0:
    sys.exit(1)
