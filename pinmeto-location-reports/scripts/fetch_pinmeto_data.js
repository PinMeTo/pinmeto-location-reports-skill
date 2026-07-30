#!/usr/bin/env node
// © 2025 PinMeTo AB. All rights reserved.
// See LICENSE file for full terms.
/**
 * Fetch real data from the PinMeTo Location MCP server and format it for report generation.
 *
 * Requires PinMeTo Location MCP >= 4.0.0.
 *
 * Usage:
 *   node scripts/fetch_pinmeto_data.js --year 2025 --output real_data.json
 *   node scripts/fetch_pinmeto_data.js --year 2025 --server /path/to/build/index.js
 *
 * Credentials are read from the environment:
 *   PINMETO_ACCOUNT_ID, PINMETO_APP_ID, PINMETO_APP_SECRET
 *
 * The output is written in the report data schema documented in
 * references/data-schema.md and can be checked with:
 *   python scripts/validate_report_data.py <output>
 */

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

const MIN_SERVER_MAJOR = 4;

// ============================================================================
// Metric keys (v4.0.0)
// ============================================================================
// Literal values of the `metric` field in each insights entry. Case-sensitive:
// Google uses SCREAMING_SNAKE, Facebook uses lower_snake. See
// references/metrics-glossary.md.

const GOOGLE_IMPRESSIONS = [
  'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH',
  'BUSINESS_IMPRESSIONS_MOBILE_SEARCH',
  'BUSINESS_IMPRESSIONS_DESKTOP_MAPS',
  'BUSINESS_IMPRESSIONS_MOBILE_MAPS'
];
const GOOGLE_SEARCH_IMPRESSIONS = [
  'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH',
  'BUSINESS_IMPRESSIONS_MOBILE_SEARCH'
];
const GOOGLE_MAPS_IMPRESSIONS = [
  'BUSINESS_IMPRESSIONS_DESKTOP_MAPS',
  'BUSINESS_IMPRESSIONS_MOBILE_MAPS'
];
const GOOGLE_WEBSITE_CLICKS = ['WEBSITE_CLICKS'];
const GOOGLE_DIRECTIONS = ['BUSINESS_DIRECTION_REQUESTS'];
const GOOGLE_CALLS = ['CALL_CLICKS'];
const GOOGLE_ACTIONS = [...GOOGLE_WEBSITE_CLICKS, ...GOOGLE_DIRECTIONS, ...GOOGLE_CALLS];

const FB_IMPRESSIONS = ['page_impressions'];
const FB_REACH = ['page_impressions_unique'];
const FB_ORGANIC = ['page_impressions_organic'];
const FB_PAID = ['page_impressions_paid'];
const FB_ACTIONS = ['page_total_actions'];
const FB_FANS = ['page_fans'];
const FB_FAN_ADDS = ['page_fan_adds'];
const FB_FAN_REMOVES = ['page_fan_removes'];

// ============================================================================
// Credentials and server discovery
// ============================================================================

function validateCredentials() {
  const required = ['PINMETO_ACCOUNT_ID', 'PINMETO_APP_ID', 'PINMETO_APP_SECRET'];
  const missing = required.filter(key => !process.env[key]);

  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing.join(', '));
    console.error('Set these variables before running the script:');
    console.error('  export PINMETO_ACCOUNT_ID="your-account-id"');
    console.error('  export PINMETO_APP_ID="your-app-id"');
    console.error('  export PINMETO_APP_SECRET="your-app-secret"');
    process.exit(1);
  }
}

/**
 * Locate the MCP server entry point.
 *
 * Extension directory names are not stable (they have changed across Claude
 * Desktop versions), so scan the extensions directories for anything matching
 * the PinMeTo server rather than hardcoding one path.
 *
 * Resolution order: --server flag, PINMETO_MCP_PATH, local node_modules,
 * installed desktop extension.
 */
function resolveServerPath(explicitPath) {
  // An explicit path that does not exist is a hard error. Falling back to
  // discovery could silently connect to a different (possibly older) server
  // than the one the caller named.
  for (const [source, value] of [
    ['--server', explicitPath],
    ['PINMETO_MCP_PATH', process.env.PINMETO_MCP_PATH]
  ]) {
    if (!value) continue;
    if (!fs.existsSync(value)) {
      console.error(`${source} points to a file that does not exist: ${value}`);
      process.exit(1);
    }
    return value;
  }

  const candidates = [];

  candidates.push(
    path.join(
      __dirname,
      '..',
      'node_modules',
      '@pinmeto',
      'pinmeto-location-mcp',
      'build',
      'index.js'
    )
  );

  for (const candidate of candidates) {
    if (candidate && fs.existsSync(candidate)) return candidate;
  }

  const home = process.env.HOME || process.env.USERPROFILE || '';
  const extensionDirs = [
    path.join(home, 'Library/Application Support/Claude/Claude Extensions'),
    process.env.APPDATA ? path.join(process.env.APPDATA, 'Claude/Claude Extensions') : null,
    path.join(home, '.config/Claude/Claude Extensions')
  ].filter(Boolean);

  for (const dir of extensionDirs) {
    if (!fs.existsSync(dir)) continue;
    const matches = fs
      .readdirSync(dir)
      .filter(name => /pinmeto.*location-mcp/i.test(name))
      .map(name => path.join(dir, name, 'build', 'index.js'))
      .filter(entry => fs.existsSync(entry));
    if (matches.length > 0) return matches[0];
  }

  console.error('Could not locate the PinMeTo Location MCP server.');
  console.error('Pass an explicit path or set the environment variable:');
  console.error('  node scripts/fetch_pinmeto_data.js --server /path/to/build/index.js');
  console.error('  export PINMETO_MCP_PATH="/path/to/build/index.js"');
  process.exit(1);
}

// ============================================================================
// MCP client
// ============================================================================

/** Error carrying the server's own error classification. */
class ToolError extends Error {
  constructor(message, { errorCode, retryable } = {}) {
    super(message);
    this.name = 'ToolError';
    this.errorCode = errorCode;
    // Unknown retryability is treated as retryable: transport faults reach here
    // with no classification and those are worth another attempt.
    this.retryable = retryable !== false;
  }
}

class MCPClient {
  constructor(serverPath) {
    this.serverPath = serverPath;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.serverProcess = null;
    this.rl = null;
    this.serverInfo = null;
  }

  async start() {
    const ready = new Promise((resolve, reject) => {
      this.serverProcess = spawn('node', [this.serverPath], {
        env: { ...process.env },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.rl = readline.createInterface({
        input: this.serverProcess.stdout,
        crlfDelay: Infinity
      });

      this.rl.on('line', line => {
        let response;
        try {
          response = JSON.parse(line);
        } catch (e) {
          return; // Not a JSON-RPC frame
        }
        const pending = this.pendingRequests.get(response.id);
        if (!pending) return;
        this.pendingRequests.delete(response.id);
        if (response.error) {
          pending.reject(new ToolError(response.error.message, { retryable: false }));
        } else {
          pending.resolve(response.result);
        }
      });

      this.serverProcess.stderr.on('data', data => {
        const msg = data.toString().trim();
        if (msg) console.error('[MCP]', msg);
      });

      this.serverProcess.on('error', reject);
      this.serverProcess.on('exit', code => {
        const err = new Error(`MCP server exited (code ${code})`);
        for (const [, pending] of this.pendingRequests) pending.reject(err);
        this.pendingRequests.clear();
      });

      resolve();
    });

    await ready;

    // Handshake immediately rather than waiting for a stderr banner. v4.0.0 no
    // longer overrides the SDK initialize handler, so the banner is not a
    // reliable readiness signal.
    const initResult = await this.sendRequest('initialize', {
      protocolVersion: '2025-06-18',
      capabilities: {},
      clientInfo: { name: 'pinmeto-report-generator', version: '2.0.0' }
    });

    this.serverInfo = initResult && initResult.serverInfo;
    this.sendNotification('notifications/initialized');
    this.checkServerVersion();

    return initResult;
  }

  checkServerVersion() {
    const version = this.serverInfo && this.serverInfo.version;
    if (!version) {
      console.warn('Warning: server did not report a version; assuming v4 contracts.');
      return;
    }
    console.log(`Connected to ${this.serverInfo.name || 'PinMeTo MCP'} v${version}`);
    const major = parseInt(String(version).split('.')[0], 10);
    if (Number.isFinite(major) && major < MIN_SERVER_MAJOR) {
      console.warn(
        `Warning: this script targets PinMeTo Location MCP >= ${MIN_SERVER_MAJOR}.0.0 but the ` +
          `server reports v${version}. Tool contracts differ and results may be wrong or empty. ` +
          'Update the MCP server.'
      );
    }
  }

  sendNotification(method, params = {}) {
    this.serverProcess.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
  }

  async sendRequest(method, params = {}) {
    const id = ++this.requestId;
    const request = { jsonrpc: '2.0', id, method, params };

    return new Promise((resolve, reject) => {
      // Clear the timer on settle, otherwise a pending 60s timer keeps the event
      // loop alive long after the work is done and the script appears to hang.
      const timer = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, 60000);

      this.pendingRequests.set(id, {
        resolve: value => {
          clearTimeout(timer);
          resolve(value);
        },
        reject: error => {
          clearTimeout(timer);
          reject(error);
        }
      });

      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');
    });
  }

  /**
   * Call a tool and return its structured payload.
   * Throws ToolError carrying the server's errorCode and retryable flag.
   */
  async callTool(name, args) {
    const result = await this.sendRequest('tools/call', { name, arguments: args });
    const data = extractData(result);

    if (result.isError || (data && data.error)) {
      const message = (data && data.error) || `${name} failed`;
      throw new ToolError(message, {
        errorCode: data && data.errorCode,
        retryable: data && data.retryable
      });
    }

    if (data && data.warning) {
      console.warn(`[${name}] ${data.warningCode || 'WARNING'}: ${data.warning}`);
    }

    return data;
  }

  /**
   * Call a tool, retrying only failures the server marked retryable.
   * Retrying an auth failure or a 404 can never succeed.
   */
  async callToolWithRetry(name, args, maxRetries = 3) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await this.callTool(name, args);
      } catch (error) {
        lastError = error;

        if (error instanceof ToolError && !error.retryable) {
          throw new Error(
            `${name} failed (${error.errorCode || 'not retryable'}): ${error.message}`
          );
        }

        if (attempt < maxRetries - 1) {
          const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
          console.log(
            `[Retry ${attempt + 1}/${maxRetries}] ${name}: ${error.message}. Waiting ${delay}ms...`
          );
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw new Error(`${name} failed after ${maxRetries} attempts: ${lastError.message}`);
  }

  stop() {
    if (this.serverProcess) this.serverProcess.kill();
    if (this.rl) this.rl.close();
  }
}

/** Extract the structured payload from an MCP tool result. */
function extractData(result) {
  if (!result) return null;
  if (result.structuredContent) return result.structuredContent;
  if (result.content && result.content[0] && result.content[0].text) {
    try {
      return JSON.parse(result.content[0].text);
    } catch (e) {
      return { raw: result.content[0].text };
    }
  }
  return result;
}

// ============================================================================
// Insights parsing (v4 response shape)
// ============================================================================
// insights is an array keyed by metric name. With aggregation=total each entry
// is flat ({metric, value, priorValue, delta, deltaPercent}); with any other
// aggregation each entry holds a values[] time series. Comparison fields are
// flat on the entry or on each value, never nested under `comparison`.

function insightsOf(payload) {
  return payload && Array.isArray(payload.insights) ? payload.insights : [];
}

function findMetric(insights, key) {
  return insights.find(entry => entry.metric === key);
}

/** Sum the current-period value of one metric across all its periods. */
function currentValue(insight) {
  if (!insight) return 0;
  if (typeof insight.value === 'number') return insight.value;
  return (insight.values || []).reduce((sum, v) => sum + (v.value || 0), 0);
}

/**
 * Sum the prior-period value of one metric.
 * Returns null when the response carries no comparison data, which is distinct
 * from a real prior value of 0.
 */
function priorValue(insight) {
  if (!insight) return null;
  if (typeof insight.priorValue === 'number') return insight.priorValue;
  const values = insight.values || [];
  if (!values.some(v => typeof v.priorValue === 'number')) return null;
  return values.reduce((sum, v) => sum + (v.priorValue || 0), 0);
}

/** Total current and prior values across a group of metric keys. */
function sumMetrics(insights, keys) {
  let current = 0;
  let prior = null;

  for (const key of keys) {
    const insight = findMetric(insights, key);
    if (!insight) continue;
    current += currentValue(insight);
    const p = priorValue(insight);
    if (p !== null) prior = (prior || 0) + p;
  }

  return { current, prior };
}

/**
 * Build chart data from a time-series response, summing the given metric keys
 * per period. Uses the server's periodLabel rather than reconstructing labels.
 */
function buildChartData(insights, keys) {
  const byPeriod = new Map();

  for (const key of keys) {
    const insight = findMetric(insights, key);
    if (!insight || !Array.isArray(insight.values)) continue;

    for (const v of insight.values) {
      const entry = byPeriod.get(v.period) || {
        label: v.periodLabel || v.period,
        value: 0,
        priorValue: 0,
        hasPrior: false
      };
      entry.value += v.value || 0;
      if (typeof v.priorValue === 'number') {
        entry.priorValue += v.priorValue;
        entry.hasPrior = true;
      }
      byPeriod.set(v.period, entry);
    }
  }

  return Array.from(byPeriod.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, entry]) => ({
      label: entry.label,
      value: entry.value,
      priorValue: entry.hasPrior ? entry.priorValue : 0
    }));
}

/** Turn a raw metric key into a readable label. */
function humanizeMetric(key) {
  return String(key)
    .replace(/^(BUSINESS_|PAGE_|page_)/, '')
    .replace(/[_-]+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
}

// ============================================================================
// Formatting helpers
// ============================================================================

function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return String(num);
}

/**
 * Percent change as a display string.
 * Returns 'N/A' when there is no comparison data or the baseline is 0, matching
 * the server's own null deltaPercent behaviour.
 */
function calcChange(current, prior) {
  if (prior === null || prior === undefined || prior === 0) return 'N/A';
  const change = ((current - prior) / prior) * 100;
  const rounded = change.toFixed(0);
  return change >= 0 ? `+${rounded}%` : `${rounded}%`;
}

function metricRow(name, { current, prior }) {
  return {
    name,
    value: current,
    periodChange: 'N/A', // Requires a second call with compare_with=prior_period
    yearChange: calcChange(current, prior)
  };
}

// ============================================================================
// Data fetching
// ============================================================================

async function fetchPinMeToData(year, serverPath) {
  const client = new MCPClient(serverPath);

  console.log('Starting PinMeTo MCP server...');
  await client.start();

  const fromDate = `${year}-01-01`;
  const toDate = `${year}-12-31`;
  // Keywords take month precision, not full dates.
  const fromMonth = `${year}-01`;
  const toMonth = `${year}-12`;

  const reportData = {
    companyName: process.env.PINMETO_ACCOUNT_ID || 'PinMeTo',
    title: 'Location Analytics Report',
    period: `${year}`,
    priorPeriod: `${year - 1}`,
    dateRange: `January 1 - December 31, ${year}`,
    priorDateRange: `January 1 - December 31, ${year - 1}`,
    executiveSummary: { narrative: '', highlights: [] },
    kpis: [],
    google: { insights: [], metrics: [], chartData: [] },
    facebook: { insights: [], metrics: [], chartData: [] },
    apple: { insights: [], metrics: [], chartData: [] },
    keywords: { insights: [], topKeywords: [], categoryDistribution: [] },
    reviews: {
      insights: [],
      totalReviews: 0,
      ratingChange: 'N/A',
      sentiment: { positive: 0, neutral: 0, negative: 0 },
      topThemes: [],
      recentHighlights: []
    },
    recommendations: [],
    appendix: {
      dataSources: [],
      reportingPeriod: {
        quarter: `${year}`,
        dateRange: `January 1, ${year} - December 31, ${year}`,
        dataFreshness: '',
        lagNote: ''
      },
      calculationNotes: [
        'YoY (Year-over-Year) comparisons use the prior calendar year as the baseline',
        'Percentage changes calculated as: ((current - previous) / previous) x 100',
        'Percentage change reported as N/A when the prior-period baseline is zero or unavailable',
        'Google impressions are the sum of desktop and mobile, search and maps surfaces',
        'Google actions are the sum of website clicks, direction requests, and phone calls',
        'Average ratings are weighted by review count and exclude locations with no reviews'
      ],
      locationCoverage: { totalLocations: 0 }
    },
    dataWarnings: []
  };

  const noteWarning = message => {
    if (message && !reportData.dataWarnings.includes(message)) {
      reportData.dataWarnings.push(message);
    }
  };

  try {
    // ---- Locations ----------------------------------------------------------
    console.log('Fetching locations...');
    try {
      const locations = await client.callToolWithRetry('pinmeto_get_locations', {
        fields: ['storeId', 'name', 'address'],
        limit: 1000,
        response_format: 'json'
      });

      const rows = Array.isArray(locations.data) ? locations.data : [];
      reportData.appendix.locationCoverage.totalLocations = rows.length;

      const countries = new Set(
        rows.map(loc => loc.address && loc.address.country).filter(Boolean)
      );
      if (countries.size > 0) {
        reportData.appendix.locationCoverage.geographicCoverage =
          `${countries.size} ${countries.size === 1 ? 'country' : 'countries'} ` +
          `(${Array.from(countries).sort().join(', ')})`;
      }
      console.log(`  ${rows.length} locations`);
    } catch (e) {
      console.log('Locations not available:', e.message);
      noteWarning(`Location list unavailable: ${e.message}`);
    }

    // ---- Google insights ----------------------------------------------------
    console.log('Fetching Google insights...');
    try {
      const googlePayload = await client.callToolWithRetry('pinmeto_get_google_insights', {
        from: fromDate,
        to: toDate,
        aggregation: 'monthly',
        compare_with: 'prior_year',
        response_format: 'json'
      });

      if (googlePayload.warning) noteWarning(googlePayload.warning);
      if (googlePayload.comparisonError) {
        noteWarning(`Google YoY comparison unavailable: ${googlePayload.comparisonError}`);
      }

      const insights = insightsOf(googlePayload);
      if (insights.length === 0) {
        noteWarning('Google insights returned no metrics for this period.');
      }

      const views = sumMetrics(insights, GOOGLE_IMPRESSIONS);
      const searches = sumMetrics(insights, GOOGLE_SEARCH_IMPRESSIONS);
      const maps = sumMetrics(insights, GOOGLE_MAPS_IMPRESSIONS);
      const webClicks = sumMetrics(insights, GOOGLE_WEBSITE_CLICKS);
      const directions = sumMetrics(insights, GOOGLE_DIRECTIONS);
      const calls = sumMetrics(insights, GOOGLE_CALLS);
      const actions = sumMetrics(insights, GOOGLE_ACTIONS);

      reportData.google.metrics = [
        metricRow('Total Views', views),
        metricRow('Search Impressions', searches),
        metricRow('Maps Impressions', maps),
        metricRow('Website Clicks', webClicks),
        metricRow('Direction Requests', directions),
        metricRow('Phone Calls', calls)
      ];

      reportData.google.chartData = buildChartData(insights, GOOGLE_IMPRESSIONS);

      // Derived, factual observations. Refine the wording when writing the report.
      if (views.current > 0) {
        reportData.google.insights.push(
          `Total Google views reached ${formatNumber(views.current)} ` +
            `(${calcChange(views.current, views.prior)} YoY).`
        );
        const mapsShare = Math.round((maps.current / views.current) * 100);
        reportData.google.insights.push(
          `Maps surfaces drove ${mapsShare}% of impressions, search drove ${100 - mapsShare}%.`
        );
      }
      if (actions.current > 0 && views.current > 0) {
        const rate = ((actions.current / views.current) * 100).toFixed(1);
        reportData.google.insights.push(
          `${formatNumber(actions.current)} customer actions at a ${rate}% view-to-action rate ` +
            `(${calcChange(actions.current, actions.prior)} YoY).`
        );
      }

      reportData.kpis.push(
        {
          name: 'Google Views',
          value: formatNumber(views.current),
          change: calcChange(views.current, views.prior)
        },
        {
          name: 'Customer Actions',
          value: formatNumber(actions.current),
          change: calcChange(actions.current, actions.prior)
        }
      );

      reportData.appendix.dataSources.push('Google Business Profile via PinMeTo API');
    } catch (e) {
      console.log('Google insights not available:', e.message);
      noteWarning(`Google insights unavailable: ${e.message}`);
    }

    // ---- Facebook insights --------------------------------------------------
    console.log('Fetching Facebook insights...');
    try {
      const fbPayload = await client.callToolWithRetry('pinmeto_get_facebook_insights', {
        from: fromDate,
        to: toDate,
        aggregation: 'monthly',
        compare_with: 'prior_year',
        response_format: 'json'
      });

      if (fbPayload.comparisonError) {
        noteWarning(`Facebook YoY comparison unavailable: ${fbPayload.comparisonError}`);
      }

      const insights = insightsOf(fbPayload);
      const impressions = sumMetrics(insights, FB_IMPRESSIONS);
      const reach = sumMetrics(insights, FB_REACH);
      const organic = sumMetrics(insights, FB_ORGANIC);
      const paid = sumMetrics(insights, FB_PAID);
      const fbActions = sumMetrics(insights, FB_ACTIONS);
      const fans = sumMetrics(insights, FB_FANS);
      const fanAdds = sumMetrics(insights, FB_FAN_ADDS);
      const fanRemoves = sumMetrics(insights, FB_FAN_REMOVES);

      reportData.facebook.metrics = [
        metricRow('Impressions', impressions),
        metricRow('Reach', reach),
        metricRow('Organic Impressions', organic),
        metricRow('Paid Impressions', paid),
        metricRow('Total Actions', fbActions),
        metricRow('Page Fans', fans)
      ];

      reportData.facebook.chartData = buildChartData(insights, FB_IMPRESSIONS);

      if (impressions.current > 0) {
        reportData.facebook.insights.push(
          `Facebook impressions totalled ${formatNumber(impressions.current)} ` +
            `(${calcChange(impressions.current, impressions.prior)} YoY).`
        );
        if (organic.current > 0) {
          const organicShare = Math.round((organic.current / impressions.current) * 100);
          reportData.facebook.insights.push(
            `${organicShare}% of impressions were organic.`
          );
        }
      }
      const netFanGrowth = fanAdds.current - fanRemoves.current;
      if (fanAdds.current > 0 || fanRemoves.current > 0) {
        reportData.facebook.insights.push(
          `Net follower change of ${netFanGrowth >= 0 ? '+' : ''}${netFanGrowth} ` +
            `(${formatNumber(fanAdds.current)} gained, ${formatNumber(fanRemoves.current)} lost).`
        );
      }

      if (reach.current > 0) {
        reportData.kpis.push({
          name: 'FB Reach',
          value: formatNumber(reach.current),
          change: calcChange(reach.current, reach.prior)
        });
      }

      if (insights.length > 0) {
        reportData.appendix.dataSources.push('Facebook Pages via PinMeTo API');
      }
    } catch (e) {
      console.log('Facebook insights not available:', e.message);
      noteWarning(`Facebook insights unavailable: ${e.message}`);
    }

    // ---- Apple insights -----------------------------------------------------
    // Apple metric keys are passed through from the PinMeTo API and are not
    // enumerated by the MCP server, so discover them from the response instead
    // of hardcoding names.
    console.log('Fetching Apple insights...');
    try {
      const applePayload = await client.callToolWithRetry('pinmeto_get_apple_insights', {
        from: fromDate,
        to: toDate,
        aggregation: 'monthly',
        compare_with: 'prior_year',
        response_format: 'json'
      });

      const insights = insightsOf(applePayload);
      console.log(`  Apple metrics found: ${insights.map(i => i.metric).join(', ') || 'none'}`);

      reportData.apple.metrics = insights.map(insight =>
        metricRow(humanizeMetric(insight.metric), {
          current: currentValue(insight),
          prior: priorValue(insight)
        })
      );

      if (insights.length > 0) {
        const largest = insights
          .map(i => ({ metric: i.metric, total: currentValue(i), prior: priorValue(i) }))
          .sort((a, b) => b.total - a.total)[0];

        reportData.apple.chartData = buildChartData(insights, [largest.metric]);
        reportData.apple.insights.push(
          `${humanizeMetric(largest.metric)} led Apple Maps activity at ` +
            `${formatNumber(largest.total)} (${calcChange(largest.total, largest.prior)} YoY).`
        );
        reportData.appendix.dataSources.push('Apple Maps via PinMeTo API');
      }
    } catch (e) {
      console.log('Apple insights not available:', e.message);
      noteWarning(`Apple insights unavailable: ${e.message}`);
    }

    // ---- Google keywords ----------------------------------------------------
    // Response is a flat array already aggregated across locations, with the
    // impression count in `value`. There is no limit parameter, so take top N here.
    console.log('Fetching Google keywords...');
    try {
      const kwPayload = await client.callToolWithRetry('pinmeto_get_google_keywords', {
        from: fromMonth,
        to: toMonth,
        response_format: 'json'
      });

      const keywords = Array.isArray(kwPayload.data) ? kwPayload.data : [];
      const brandTerm = (process.env.PINMETO_ACCOUNT_ID || '').toLowerCase();

      const classify = keyword => {
        const text = keyword.toLowerCase();
        if (brandTerm && text.includes(brandTerm)) return 'Branded';
        if (/\bnear me\b|\bnearby\b|\bdirections?\b|\bopen now\b|\bhours?\b/.test(text)) {
          return 'Navigational';
        }
        return 'Discovery';
      };

      const ranked = keywords
        .map(kw => ({
          keyword: kw.keyword,
          impressions: kw.value || 0,
          locationCounts: kw.locationCounts,
          category: classify(kw.keyword || '')
        }))
        .sort((a, b) => b.impressions - a.impressions);

      reportData.keywords.topKeywords = ranked.slice(0, 25);

      // Distribution over the full keyword set, not just the top slice.
      const totals = { Branded: 0, Discovery: 0, Navigational: 0 };
      for (const kw of ranked) totals[kw.category] += kw.impressions;
      const grandTotal = Object.values(totals).reduce((a, b) => a + b, 0);

      reportData.keywords.categoryDistribution = Object.entries(totals).map(([label, value]) => ({
        label,
        value: grandTotal > 0 ? Math.round((value / grandTotal) * 100) : 0
      }));

      if (grandTotal > 0) {
        const brandedShare = Math.round((totals.Branded / grandTotal) * 100);
        reportData.keywords.insights.push(
          `Branded searches account for ${brandedShare}% of keyword impressions.`,
          `${ranked.length} distinct keywords generated ${formatNumber(grandTotal)} impressions.`
        );
        if (ranked[0]) {
          reportData.keywords.insights.push(
            `Top keyword "${ranked[0].keyword}" drove ${formatNumber(ranked[0].impressions)} impressions.`
          );
        }
      }
      console.log(`  ${ranked.length} keywords`);
    } catch (e) {
      console.log('Keywords not available:', e.message);
      noteWarning(`Google keywords unavailable: ${e.message}`);
    }

    // ---- Google ratings -----------------------------------------------------
    console.log('Fetching Google ratings...');
    try {
      const ratingsPayload = await client.callToolWithRetry('pinmeto_get_google_ratings', {
        from: fromDate,
        to: toDate,
        response_format: 'json'
      });

      const raw = ratingsPayload.data;
      const rows = Array.isArray(raw) ? raw : raw ? [raw] : [];

      let totalReviews = 0;
      let weightedSum = 0;
      const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };

      for (const loc of rows) {
        const reviews = loc.totalReviews || 0;
        totalReviews += reviews;
        // averageRating is 0 for a location with no reviews in range. Excluding
        // those keeps the weighted average from being dragged toward zero.
        if (reviews > 0 && loc.averageRating > 0) {
          weightedSum += loc.averageRating * reviews;
        }
        for (const [star, count] of Object.entries(loc.distribution || {})) {
          distribution[star] = (distribution[star] || 0) + count;
        }
      }

      reportData.reviews.totalReviews = totalReviews;

      if (totalReviews > 0) {
        reportData.reviews.averageRating = parseFloat((weightedSum / totalReviews).toFixed(1));
      }

      const positive = distribution[4] + distribution[5];
      const neutral = distribution[3];
      const negative = distribution[1] + distribution[2];
      const rated = positive + neutral + negative;

      if (rated > 0) {
        reportData.reviews.sentiment = {
          positive: Math.round((positive / rated) * 100),
          neutral: Math.round((neutral / rated) * 100),
          negative: Math.round((negative / rated) * 100)
        };
      }

      reportData.reviews.ratingDistribution = distribution;

      if (totalReviews > 0) {
        reportData.kpis.push(
          { name: 'Avg Rating', value: String(reportData.reviews.averageRating), change: 'N/A' },
          { name: 'Reviews', value: formatNumber(totalReviews), change: 'N/A' }
        );
        reportData.reviews.insights.push(
          `${formatNumber(totalReviews)} reviews averaging ${reportData.reviews.averageRating} stars ` +
            `across ${rows.length} ${rows.length === 1 ? 'location' : 'locations'}.`
        );
      } else {
        noteWarning('No Google reviews found in the reporting period.');
      }
      console.log(`  ${totalReviews} reviews`);
    } catch (e) {
      console.log('Ratings not available:', e.message);
      noteWarning(`Google ratings unavailable: ${e.message}`);
    }

    // ---- Google review insights --------------------------------------------
    // Server-side sentiment statistics. Far cheaper than fetching every review,
    // but it performs no theme extraction: topThemes still comes from raw text.
    console.log('Fetching Google review insights...');
    try {
      const baseArgs = {
        from: fromDate,
        to: toDate,
        analysisType: 'summary',
        response_format: 'json'
      };

      let payload = await client.callToolWithRetry(
        'pinmeto_get_google_review_insights',
        baseArgs
      );

      // A full year can exceed the confirmation threshold; proceed explicitly.
      if (payload.requiresConfirmation) {
        const count =
          (payload.largeDatasetWarning && payload.largeDatasetWarning.totalReviewCount) ||
          'many';
        console.log(`  Large dataset (${count} reviews), re-requesting with confirmation...`);
        payload = await client.callToolWithRetry('pinmeto_get_google_review_insights', {
          ...baseArgs,
          skipConfirmation: true,
          samplingStrategy: 'representative'
        });
      }

      const summary = payload.data && payload.data.summary;
      if (summary) {
        if (summary.sentimentDistribution) {
          reportData.reviews.sentiment = {
            positive: Math.round(summary.sentimentDistribution.positive),
            neutral: Math.round(summary.sentimentDistribution.neutral),
            negative: Math.round(summary.sentimentDistribution.negative)
          };
        }
        if (summary.averageRating > 0) {
          reportData.reviews.averageRating = parseFloat(summary.averageRating.toFixed(1));
        }
        if (summary.executiveSummary) {
          reportData.reviews.insights.push(summary.executiveSummary);
        }
        if (summary.lowConfidence) {
          noteWarning('Review sentiment is based on a small sample (<20 reviews).');
        }
      }

      const meta = payload.metadata;
      if (meta && meta.analyzedReviewCount < meta.totalReviewCount) {
        noteWarning(
          `Review sentiment based on ${meta.analyzedReviewCount} of ${meta.totalReviewCount} ` +
            `reviews (${meta.samplingStrategy || 'sampled'}).`
        );
      }

      // Present on the schema but not populated: the server does no theme
      // extraction. Use it if it ever appears, otherwise derive below.
      const themes = payload.data && payload.data.themes;
      if (themes) {
        reportData.reviews.topThemes = [
          ...(themes.positive || []).map(t => ({
            theme: t.theme,
            mentions: t.mentions || t.count || 0,
            sentiment: 'positive'
          })),
          ...(themes.negative || []).map(t => ({
            theme: t.theme,
            mentions: t.mentions || t.count || 0,
            sentiment: 'negative'
          }))
        ];
      }
    } catch (e) {
      console.log('Review insights not available:', e.message);
      noteWarning(`Google review insights unavailable: ${e.message}`);
    }

    // ---- Google reviews (pull quotes) ---------------------------------------
    console.log('Fetching recent reviews...');
    try {
      const reviewsPayload = await client.callToolWithRetry('pinmeto_get_google_reviews', {
        from: fromDate,
        to: toDate,
        limit: 50,
        minRating: 4,
        response_format: 'json'
      });

      const reviews = Array.isArray(reviewsPayload.data) ? reviewsPayload.data : [];
      reportData.reviews.recentHighlights = reviews
        .filter(r => r.comment && r.comment.length > 10)
        .slice(0, 3)
        .map(r => ({
          text: r.comment.length > 100 ? `${r.comment.substring(0, 100)}...` : r.comment,
          rating: r.rating,
          date: r.date
        }));

      if (reviewsPayload.hasMore) {
        console.log(
          `  Showing ${reviews.length} of ${reviewsPayload.totalCount} matching reviews ` +
            '(4+ stars). Themes should be derived from a wider sample.'
        );
      }
    } catch (e) {
      console.log('Reviews not available:', e.message);
      noteWarning(`Google reviews unavailable: ${e.message}`);
    }

    // ---- Executive summary and recommendations -----------------------------
    const googleViews = reportData.google.metrics.find(m => m.name === 'Total Views');
    if (googleViews) {
      reportData.executiveSummary.highlights.push({
        title: 'Google Visibility',
        description:
          `Total Google views reached ${formatNumber(googleViews.value)} in ${year} ` +
          `(${googleViews.yearChange} year-over-year).`
      });
    }
    if (reportData.reviews.totalReviews > 0) {
      reportData.executiveSummary.highlights.push({
        title: 'Customer Feedback',
        description:
          `${formatNumber(reportData.reviews.totalReviews)} reviews averaging ` +
          `${reportData.reviews.averageRating} stars, with ` +
          `${reportData.reviews.sentiment.positive}% positive sentiment.`
      });
    }
    const topKeyword = reportData.keywords.topKeywords[0];
    if (topKeyword) {
      reportData.executiveSummary.highlights.push({
        title: 'Search Demand',
        description:
          `"${topKeyword.keyword}" was the top search term with ` +
          `${formatNumber(topKeyword.impressions)} impressions.`
      });
    }

    reportData.executiveSummary.narrative =
      `This report covers ${year} performance across ` +
      `${reportData.appendix.locationCoverage.totalLocations || 'all'} locations. ` +
      (googleViews
        ? `Google views totalled ${formatNumber(googleViews.value)} (${googleViews.yearChange} YoY). `
        : '') +
      'Replace this placeholder with an analytical narrative before delivering the report.';

    reportData.recommendations = [
      {
        title: 'Optimize Google Business Profiles',
        description:
          'Update location descriptions and categories with high-performing discovery keywords ' +
          'from the keyword table to improve visibility on non-branded searches.',
        impact: 'Projected increase in discovery search impressions'
      },
      {
        title: 'Respond to Reviews',
        description:
          'Maintain a high response rate on customer reviews, prioritizing unresponded ' +
          'negative reviews (query with hasResponse=false, maxRating=3).',
        impact: 'Improved customer trust and local ranking signals'
      },
      {
        title: 'Close Data Gaps',
        description:
          'Review the dataWarnings field and connect any platforms or locations missing data ' +
          'so future reports cover the full estate.',
        impact: 'More complete and comparable reporting'
      }
    ];

    reportData.appendix.reportingPeriod.dataFreshness = new Date().toISOString().split('T')[0];
    reportData.appendix.reportingPeriod.lagNote = reportData.dataWarnings.length
      ? reportData.dataWarnings.join(' ')
      : 'No data completeness warnings were reported by the API for this period.';
  } finally {
    client.stop();
  }

  return reportData;
}

// ============================================================================
// Main
// ============================================================================

function parseArgs(argv) {
  const options = { year: new Date().getFullYear() - 1, output: 'real_data.json', server: null };

  for (let i = 0; i < argv.length; i++) {
    const next = argv[i + 1];
    if (argv[i] === '--year' && next) options.year = parseInt(next, 10);
    if (argv[i] === '--output' && next) options.output = next;
    if (argv[i] === '--server' && next) options.server = next;
  }

  if (!Number.isFinite(options.year)) {
    console.error('Invalid --year value. Expected a four-digit year, e.g. --year 2025');
    process.exit(1);
  }

  return options;
}

async function main() {
  validateCredentials();

  const options = parseArgs(process.argv.slice(2));
  const serverPath = resolveServerPath(options.server);

  console.log(`Fetching PinMeTo data for ${options.year}...`);
  console.log(`Using MCP server: ${serverPath}`);

  const data = await fetchPinMeToData(options.year, serverPath);

  fs.writeFileSync(options.output, JSON.stringify(data, null, 2));
  console.log(`\nData saved to ${options.output}`);

  if (data.dataWarnings.length > 0) {
    console.log('\nData warnings:');
    for (const warning of data.dataWarnings) console.log(`  - ${warning}`);
  }

  console.log('\nNext step: validate before generating the report');
  console.log(`  python scripts/validate_report_data.py ${options.output}`);
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error.message);
    process.exit(1);
  });
}

// Exported for tests/parse_shapes.test.js
module.exports = {
  insightsOf,
  findMetric,
  currentValue,
  priorValue,
  sumMetrics,
  buildChartData,
  humanizeMetric,
  calcChange,
  formatNumber,
  resolveServerPath,
  GOOGLE_IMPRESSIONS,
  GOOGLE_ACTIONS,
  FB_IMPRESSIONS
};
