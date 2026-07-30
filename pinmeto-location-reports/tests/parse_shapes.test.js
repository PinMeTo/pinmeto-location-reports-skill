#!/usr/bin/env node
/**
 * Shape tests for the v4 insights parser in scripts/fetch_pinmeto_data.js.
 *
 * Run with:
 *   node --test tests/
 *
 * The fixtures in tests/fixtures/ were produced by running the PinMeTo Location
 * MCP v4.0.0 transform pipeline (convertApiDataToInsights -> aggregateInsights
 * -> finalizeInsights) over the server's own raw API examples, so they carry the
 * real response shape rather than a hand-written approximation. Prior-period
 * values are scaled to 80% of current to produce non-trivial deltas.
 *
 * Expected totals below were computed independently from the raw API examples,
 * not from the fixtures, so a parser that silently reads the wrong field fails
 * rather than agreeing with itself.
 */

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const {
  insightsOf,
  findMetric,
  currentValue,
  priorValue,
  sumMetrics,
  buildChartData,
  humanizeMetric,
  calcChange,
  GOOGLE_IMPRESSIONS,
  GOOGLE_ACTIONS,
  FB_IMPRESSIONS
} = require('../scripts/fetch_pinmeto_data.js');

const fixture = name =>
  JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', name), 'utf8'));

// Independently computed from tests/server-response-examples in the MCP repo.
const EXPECTED = {
  googleImpressionsTotal: 2003,
  googleActionsTotal: 435,
  googleDesktopSearch: 1461,
  googleCallClicks: 4,
  facebookImpressions: 356,
  priorScale: 0.8
};

test('total aggregation: flat insight entries', async t => {
  const payload = fixture('google_insights_total_yoy.json');
  const insights = insightsOf(payload);

  await t.test('reads the metric-keyed array, not a metrics object', () => {
    assert.ok(insights.length > 0, 'insights should be a non-empty array');
    assert.ok(
      findMetric(insights, 'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH'),
      'metric lookup by name should succeed'
    );
    assert.strictEqual(
      findMetric(insights, 'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH').value,
      EXPECTED.googleDesktopSearch
    );
  });

  await t.test('sums impressions across all four surfaces', () => {
    const { current } = sumMetrics(insights, GOOGLE_IMPRESSIONS);
    assert.strictEqual(current, EXPECTED.googleImpressionsTotal);
  });

  await t.test('sums the three action metrics', () => {
    const { current } = sumMetrics(insights, GOOGLE_ACTIONS);
    assert.strictEqual(current, EXPECTED.googleActionsTotal);
  });

  await t.test('reads flat priorValue rather than a nested comparison object', () => {
    const { current, prior } = sumMetrics(insights, GOOGLE_IMPRESSIONS);
    assert.notStrictEqual(prior, null, 'prior should be populated when compare_with is set');
    // Prior is per-metric rounding of 80%, so allow a small tolerance.
    assert.ok(
      Math.abs(prior - current * EXPECTED.priorScale) <= 4,
      `prior ${prior} should be ~80% of ${current}`
    );
  });

  await t.test('no legacy comparison.prior path exists', () => {
    const entry = findMetric(insights, 'CALL_CLICKS');
    assert.strictEqual(entry.comparison, undefined, 'v4 has no nested comparison object');
    assert.strictEqual(typeof entry.priorValue, 'number');
  });
});

test('time-series aggregation: values array', async t => {
  const payload = fixture('google_insights_monthly_yoy.json');
  const insights = insightsOf(payload);

  await t.test('sums across periods to the same totals as aggregation=total', () => {
    assert.strictEqual(
      sumMetrics(insights, GOOGLE_IMPRESSIONS).current,
      EXPECTED.googleImpressionsTotal
    );
    assert.strictEqual(
      currentValue(findMetric(insights, 'CALL_CLICKS')),
      EXPECTED.googleCallClicks
    );
  });

  await t.test('chart data uses the server periodLabel', () => {
    const chart = buildChartData(insights, GOOGLE_IMPRESSIONS);
    assert.ok(chart.length > 0, 'chart data should not be empty');
    for (const point of chart) {
      assert.ok(point.label, 'every point needs a label');
      assert.ok(
        /^[A-Z][a-z]+ \d{4}$|^Q\d \d{4}$|^H\d \d{4}$|^\d{4}/.test(point.label),
        `label "${point.label}" should be a readable server-provided label`
      );
      assert.strictEqual(typeof point.value, 'number');
    }
  });

  await t.test('chart totals match the metric totals', () => {
    const chart = buildChartData(insights, GOOGLE_IMPRESSIONS);
    const charted = chart.reduce((sum, p) => sum + p.value, 0);
    assert.strictEqual(charted, EXPECTED.googleImpressionsTotal);
  });
});

test('missing comparison data is distinguished from a zero baseline', async t => {
  const payload = fixture('google_insights_monthly_nocompare.json');
  const insights = insightsOf(payload);

  await t.test('priorValue returns null when no comparison was requested', () => {
    assert.strictEqual(priorValue(findMetric(insights, 'WEBSITE_CLICKS')), null);
    assert.strictEqual(sumMetrics(insights, GOOGLE_IMPRESSIONS).prior, null);
  });

  await t.test('current values still parse without comparison', () => {
    assert.strictEqual(
      sumMetrics(insights, GOOGLE_IMPRESSIONS).current,
      EXPECTED.googleImpressionsTotal
    );
  });
});

test('facebook metric keys are lower_snake_case', async t => {
  const payload = fixture('facebook_insights_monthly_yoy.json');
  const insights = insightsOf(payload);

  await t.test('reads page_impressions', () => {
    assert.strictEqual(
      sumMetrics(insights, FB_IMPRESSIONS).current,
      EXPECTED.facebookImpressions
    );
  });

  await t.test('uppercase Google-style keys find nothing', () => {
    // Guards the previous bug: the old parser looked for PAGE_IMPRESSIONS and
    // PAGE_VIEWS_TOTAL, which silently yielded zero for every Facebook metric.
    assert.strictEqual(sumMetrics(insights, ['PAGE_IMPRESSIONS']).current, 0);
    assert.strictEqual(sumMetrics(insights, ['PAGE_VIEWS_TOTAL']).current, 0);
  });

  await t.test('facebook prior values parse the same way as Google', () => {
    const { current, prior } = sumMetrics(insights, FB_IMPRESSIONS);
    assert.ok(prior !== null && prior > 0);
    assert.ok(Math.abs(prior - current * EXPECTED.priorScale) <= 4);
  });
});

test('keywords use value, not impressions', async t => {
  const payload = fixture('google_keywords_all.json');

  await t.test('data is a flat array, not nested per location', () => {
    assert.ok(Array.isArray(payload.data));
    assert.ok(payload.data.length > 0);
    const first = payload.data[0];
    assert.strictEqual(typeof first.keyword, 'string');
    assert.strictEqual(typeof first.value, 'number');
    assert.strictEqual(
      first.impressions,
      undefined,
      'there is no impressions field; the count lives in value'
    );
    assert.strictEqual(
      first.keywords,
      undefined,
      'there is no per-location keywords nesting'
    );
  });

  await t.test('ranking by value produces a sane top keyword', () => {
    const ranked = payload.data
      .map(kw => ({ keyword: kw.keyword, impressions: kw.value || 0 }))
      .sort((a, b) => b.impressions - a.impressions);
    assert.strictEqual(ranked[0].impressions, 1042);
    assert.ok(ranked[0].impressions >= ranked[ranked.length - 1].impressions);
  });
});

test('percent change handles unavailable and zero baselines', async t => {
  await t.test('null prior renders N/A rather than a bogus number', () => {
    assert.strictEqual(calcChange(100, null), 'N/A');
    assert.strictEqual(calcChange(100, undefined), 'N/A');
  });

  await t.test('zero baseline renders N/A rather than Infinity', () => {
    assert.strictEqual(calcChange(100, 0), 'N/A');
  });

  await t.test('normal changes are signed', () => {
    assert.strictEqual(calcChange(120, 100), '+20%');
    assert.strictEqual(calcChange(80, 100), '-20%');
    assert.strictEqual(calcChange(100, 100), '+0%');
  });
});

test('metric keys become readable labels', async t => {
  await t.test('google SCREAMING_SNAKE', () => {
    assert.strictEqual(
      humanizeMetric('BUSINESS_IMPRESSIONS_DESKTOP_MAPS'),
      'Impressions Desktop Maps'
    );
    assert.strictEqual(humanizeMetric('WEBSITE_CLICKS'), 'Website Clicks');
  });

  await t.test('facebook lower_snake', () => {
    assert.strictEqual(humanizeMetric('page_total_actions'), 'Total Actions');
    assert.strictEqual(humanizeMetric('page_impressions_unique'), 'Impressions Unique');
  });
});

test('empty and error payloads do not throw', async t => {
  await t.test('missing insights yields an empty array', () => {
    assert.deepStrictEqual(insightsOf({}), []);
    assert.deepStrictEqual(insightsOf(null), []);
    assert.deepStrictEqual(insightsOf({ error: 'boom', errorCode: 'NOT_FOUND' }), []);
  });

  await t.test('summing an absent metric yields zero, not NaN', () => {
    const { current, prior } = sumMetrics([], GOOGLE_IMPRESSIONS);
    assert.strictEqual(current, 0);
    assert.strictEqual(prior, null);
  });

  await t.test('chart data for an absent metric is empty', () => {
    assert.deepStrictEqual(buildChartData([], GOOGLE_IMPRESSIONS), []);
  });
});
