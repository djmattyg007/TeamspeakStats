import pendulum
import pytest

from tsstats.exceptions import InvalidLog
from tsstats.log import TimedLog, _bundle_logs, _parse_details, parse_logs
from tsstats.template import render_servers

testlog_path = 'tsstats/tests/res/test.log'


@pytest.fixture
def clients():
    return _parse_details(testlog_path, online_dc=False)


def test_log_client_count(clients):
    assert len(clients) == 3


def test_log_onlinetime(clients):
    assert clients['1'].onlinetime == pendulum.Interval(
        seconds=402, microseconds=149208)
    assert clients['2'].onlinetime == pendulum.Interval(
        seconds=19, microseconds=759644)


def test_log_kicks(clients):
    assert clients['UIDClient1'].kicks == 1


def test_log_pkicks(clients):
    assert clients['2'].pkicks == 1


def test_log_bans(clients):
    assert clients['UIDClient1'].bans == 1


def test_log_pbans(clients):
    assert clients['2'].pbans == 1


@pytest.mark.parametrize("logs,bundled", [
    (
        ['l1.log', 'l2.log'],
        {'': [TimedLog('l1.log', None), TimedLog('l2.log', None)]}
    ),
    (
        [
            'ts3server_2016-06-06__14_22_09.527229_1.log',
            'ts3server_2017-07-07__15_23_10.638340_1.log'
        ],
        {
            '1': [
                TimedLog(
                    'ts3server_2016-06-06__14_22_09.527229_1.log',
                    pendulum.create(
                        year=2016, month=6, day=6, hour=14, minute=22,
                        second=9, microsecond=527229
                    )
                ),
                TimedLog(
                    'ts3server_2017-07-07__15_23_10.638340_1.log',
                    pendulum.create(
                        year=2017, month=7, day=7, hour=15, minute=23,
                        second=10, microsecond=638340
                    )
                )
            ]
        }
    )
])
def test_log_bundle(logs, bundled):
    assert _bundle_logs(logs) == bundled


def test_log_invalid():
    with pytest.raises(InvalidLog):
        _parse_details('tsstats/tests/res/test.log.broken')


def test_log_client_online():
    current_time = pendulum.now()

    pendulum.set_test_now(current_time)
    clients = _parse_details(testlog_path)
    old_onlinetime = int(clients['1'].onlinetime.total_seconds())

    pendulum.set_test_now(current_time.add(seconds=2))  # add 2s to .now()
    clients = _parse_details(testlog_path)
    assert int(clients['1'].onlinetime.total_seconds()) == old_onlinetime + 2


def test_parse_logs():
    assert len(_parse_details(testlog_path)) ==\
        len(parse_logs(testlog_path)[0].clients)


def test_parse_groups():
    clients = _parse_details('tsstats/tests/res/test.log.groups')
    assert len(clients) == 0


def test_parse_utf8(output):
    servers = parse_logs(testlog_path + '.utf8')
    render_servers(servers, output)


def test_server_stop():
    clients = _parse_details('tsstats/tests/res/test.log.stopped')
    assert clients['1'].onlinetime.seconds / 60 == 20  # minutes
    assert clients['2'].onlinetime.seconds / 60 == 10  # minutes
