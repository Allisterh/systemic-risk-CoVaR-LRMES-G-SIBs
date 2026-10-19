from datetime import datetime, timezone
import pytest
from src.config import cfg
from src.calendar_status import publication_report


def report(monkeypatch, banks, **extra):
    monkeypatch.setattr(cfg, 'publication_mode', 'production')
    monkeypatch.setattr(cfg, 'publication_basis', 'market_metrics')
    payload = {'dataset_kind':'research_estimate', 'banks':banks, **extra}
    observations = {'JPM':{'metric_dates':{'mes':'2026-10-15'}}}
    return publication_report(payload, observations, '2026-10-17',
                              now=datetime(2026,10,17,1,21,tzinfo=timezone.utc))


def test_stale_partial_metrics_publish_with_explicit_dates(monkeypatch):
    r=report(monkeypatch,[{'bank_id':'JPM','mes':-.01}])
    assert r['decision']=='accepted'
    assert r['fresh_eligible_count']==0
    assert r['data_status']=='partial'
    assert r['coverage_policy']=='advisory'
    assert 'INSUFFICIENT_FRESH_ELIGIBLE_COVERAGE' in r['warnings']
    assert r['metric_status']['mes']['JPM']['as_of']=='2026-10-15'
    assert r['metric_status']['mes']['JPM']['freshness']=='stale'


@pytest.mark.parametrize('banks',[[],[{'bank_id':'JPM','mes':None}],
    [{'bank_id':'JPM','mes':float('nan')}],[{'bank_id':'JPM','mes':float('inf')}],
    [{'bank_id':'unknown','mes':-.01}]])
def test_empty_or_invalid_data_still_rejected(monkeypatch,banks):
    r=report(monkeypatch,banks)
    assert r['decision']=='rejected'
    assert 'NO_VALID_METRICS' in r['reasons']


def test_quality_error_still_rejected(monkeypatch):
    r=report(monkeypatch,[{'bank_id':'JPM','mes':-.01}],
             quality={'alerts':[{'severity':'error','code':'FUTURE_DATA_DATE'}]})
    assert r['decision']=='rejected'
    assert 'QUALITY_ERROR' in r['reasons']
