import message_ix
import pytest

from message_ix_models import testing

# Number of items in the respective YAML files
SET_SIZE = dict(
    commodity=13,
    level=6,
    technology=377,
    node=14 + 1,  # R14 is default, and 'World' exists automatically
    year=11,  # Default: 2010, 2020, ..., 2110
)


@pytest.mark.parametrize(
    "settings, expected",
    [
        # Defaults per bare.SETTINGS
        (dict(), dict()),
        #
        # Different regional aggregations
        (dict(regions="R11"), dict(node=11 + 1)),
        (dict(regions="RCP"), dict(node=5 + 1)),
        # MESSAGE-IL
        (dict(regions="ISR"), dict(node=1 + 1)),
        #
        # Different time discretizations
        (dict(time_step=5), dict(year=21)),  # 2010, 2015, ..., 2110
        #
        # Option to add a dummy technology/commodity so the model solves
        (
            dict(res_with_dummies=True),
            dict(
                commodity=SET_SIZE["commodity"] + 1,
                technology=SET_SIZE["technology"] + 2,
            ),
        ),
    ],
)
def test_create_res(request, test_context, settings, expected):
    # Apply settings to the temporary context
    test_context.update(settings)

    # Call bare.create_res() via testing.bare_res(). This ensures the slow step of
    # creating the scenario occurs only once per test session. If it fails, it will
    # either fail within this test, or in some other test function that calls
    # testing.bare_res() with the same arguments.
    scenario = testing.bare_res(request, test_context, solved=False)

    # Returns a Scenario object
    assert isinstance(scenario, message_ix.Scenario)

    # Sets contain the expected number of elements
    sets = SET_SIZE.copy()
    sets.update(expected)
    for name, size in sets.items():
        assert len(scenario.set(name)) == size

    # Contains the correct periods
    year = scenario.set("year").tolist()
    assert year[0] == test_context.period_start
    assert year[-1] == test_context.period_end
    assert year[-1] - year[-2] == test_context.time_step

    # TODO Contains the correct duration_period values
