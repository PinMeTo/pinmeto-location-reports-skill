#!/usr/bin/env node
// © 2025 PinMeTo AB. All rights reserved.
// See LICENSE file for full terms.
/**
 * Verify that the connected PinMeTo Location MCP server exposes the tool surface
 * this skill was written against.
 *
 * The skill silently produced wrong reports for two major versions because tool
 * contracts drifted and nothing checked. This turns that drift into a loud
 * failure.
 *
 * Usage:
 *   node scripts/check_mcp_parity.js
 *   node scripts/check_mcp_parity.js --server /path/to/build/index.js
 *   node scripts/check_mcp_parity.js --json
 *
 * Exit codes:
 *   0 - the server matches what the skill expects
 *   1 - drift detected (missing tools, renamed or removed parameters), or a
 *       --server / PINMETO_MCP_PATH value that does not exist
 *   2 - the server was found but could not be reached or did not respond
 *
 * Credentials are NOT required: tools/list works before any API call.
 */

const { spawn } = require('child_process');
const readline = require('readline');

const { resolveServerPath } = require('./fetch_pinmeto_data.js');

const EXPECTED_MAJOR = 4;

/**
 * The contract this skill relies on. `required` params must exist; `optional`
 * params are checked so a rename is caught, not just a removal. `absent` params
 * are ones the skill must NOT send, recorded so that if the server ever adds
 * them the docs can be updated.
 */
const EXPECTED_TOOLS = {
  pinmeto_get_locations: {
    required: [],
    optional: ['fields', 'limit', 'offset', 'permanentlyClosed', 'type', 'city', 'country'],
    absent: ['filters', 'status']
  },
  pinmeto_get_location: {
    required: ['storeId'],
    optional: [],
    absent: ['store_id']
  },
  pinmeto_search_locations: {
    required: ['query'],
    optional: ['limit'],
    absent: []
  },
  pinmeto_get_google_insights: {
    required: ['from', 'to'],
    optional: ['storeId', 'aggregation', 'compare_with'],
    absent: ['store_id', 'comparison_type']
  },
  pinmeto_get_google_ratings: {
    required: ['from', 'to'],
    optional: ['storeId', 'forceRefresh'],
    absent: ['aggregation', 'compare_with']
  },
  pinmeto_get_google_reviews: {
    required: ['from', 'to'],
    optional: ['storeId', 'limit', 'offset', 'minRating', 'maxRating', 'hasResponse'],
    absent: []
  },
  pinmeto_get_google_review_insights: {
    required: ['from', 'to', 'analysisType'],
    optional: ['storeIds', 'samplingStrategy', 'skipConfirmation', 'minRating', 'maxRating'],
    absent: ['storeId']
  },
  pinmeto_get_google_keywords: {
    required: ['from', 'to'],
    optional: ['storeId'],
    absent: ['limit']
  },
  pinmeto_get_facebook_insights: {
    required: ['from', 'to'],
    optional: ['storeId', 'aggregation', 'compare_with'],
    absent: []
  },
  pinmeto_get_facebook_brandpage_insights: {
    required: ['from', 'to'],
    optional: ['aggregation', 'compare_with'],
    absent: []
  },
  pinmeto_get_facebook_ratings: {
    required: ['from', 'to'],
    optional: ['storeId'],
    absent: ['aggregation']
  },
  pinmeto_get_apple_insights: {
    required: ['from', 'to'],
    optional: ['storeId', 'aggregation', 'compare_with'],
    absent: []
  }
};

/** Enum values the skill sends. A changed enum breaks calls at runtime. */
const EXPECTED_ENUMS = {
  pinmeto_get_google_insights: {
    aggregation: ['total', 'daily', 'weekly', 'monthly', 'quarterly', 'half-yearly', 'yearly'],
    compare_with: ['none', 'prior_period', 'prior_year']
  },
  pinmeto_get_google_review_insights: {
    analysisType: ['summary', 'issues', 'comparison', 'trends', 'themes']
  }
};

/** Date-format expectations, keyed by tool then parameter. */
const EXPECTED_FORMATS = {
  pinmeto_get_google_keywords: { from: 'YYYY-MM', to: 'YYYY-MM' },
  pinmeto_get_google_insights: { from: 'YYYY-MM-DD', to: 'YYYY-MM-DD' }
};

async function listTools(serverPath) {
  return new Promise((resolve, reject) => {
    const child = spawn('node', [serverPath], {
      env: { ...process.env },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    const pending = new Map();
    let nextId = 0;
    let settled = false;

    const rl = readline.createInterface({ input: child.stdout, crlfDelay: Infinity });
    rl.on('line', line => {
      let msg;
      try {
        msg = JSON.parse(line);
      } catch (e) {
        return;
      }
      const handler = pending.get(msg.id);
      if (!handler) return;
      pending.delete(msg.id);
      if (msg.error) handler.reject(new Error(msg.error.message));
      else handler.resolve(msg.result);
    });

    const request = (method, params = {}) => {
      const id = ++nextId;
      return new Promise((res, rej) => {
        pending.set(id, { resolve: res, reject: rej });
        child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
      });
    };

    // The timer is cleared on both settle paths: a live timer would keep the
    // event loop alive for its full duration after the check has finished.
    let timer;

    const fail = err => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      child.kill();
      reject(err);
    };

    timer = setTimeout(() => fail(new Error('Timed out waiting for the MCP server')), 30000);

    child.on('error', fail);

    (async () => {
      const init = await request('initialize', {
        protocolVersion: '2025-06-18',
        capabilities: {},
        clientInfo: { name: 'pinmeto-skill-parity-check', version: '1.0.0' }
      });
      child.stdin.write(
        JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }) + '\n'
      );
      const tools = await request('tools/list');
      settled = true;
      clearTimeout(timer);
      child.kill();
      resolve({ serverInfo: init && init.serverInfo, tools: (tools && tools.tools) || [] });
    })().catch(fail);
  });
}

function schemaOf(tool) {
  const schema = tool.inputSchema || {};
  return {
    properties: schema.properties || {},
    required: new Set(schema.required || [])
  };
}

/** Collect enum values from a property, looking through common wrappers. */
function enumValuesOf(property) {
  if (!property) return null;
  if (Array.isArray(property.enum)) return property.enum;
  for (const key of ['anyOf', 'oneOf', 'allOf']) {
    if (Array.isArray(property[key])) {
      for (const branch of property[key]) {
        const found = enumValuesOf(branch);
        if (found) return found;
      }
    }
  }
  return null;
}

function patternOf(property) {
  if (!property) return null;
  if (property.pattern) return property.pattern;
  for (const key of ['anyOf', 'oneOf', 'allOf']) {
    if (Array.isArray(property[key])) {
      for (const branch of property[key]) {
        const found = patternOf(branch);
        if (found) return found;
      }
    }
  }
  return null;
}

function check(serverInfo, tools) {
  const findings = [];
  const byName = new Map(tools.map(tool => [tool.name, tool]));

  const version = (serverInfo && serverInfo.version) || 'unknown';
  const major = parseInt(String(version).split('.')[0], 10);
  if (Number.isFinite(major) && major !== EXPECTED_MAJOR) {
    findings.push({
      level: major < EXPECTED_MAJOR ? 'error' : 'warn',
      tool: '(server)',
      message:
        `Server is v${version}; this skill targets v${EXPECTED_MAJOR}.x. ` +
        (major < EXPECTED_MAJOR
          ? 'Upgrade the MCP server.'
          : 'Review the changelog for breaking changes and update the skill.')
    });
  }

  for (const [name, contract] of Object.entries(EXPECTED_TOOLS)) {
    const tool = byName.get(name);
    if (!tool) {
      findings.push({ level: 'error', tool: name, message: 'Tool is missing from the server' });
      continue;
    }

    const { properties, required } = schemaOf(tool);

    for (const param of contract.required) {
      if (!(param in properties)) {
        findings.push({
          level: 'error',
          tool: name,
          message: `Required parameter "${param}" no longer exists`
        });
      }
    }

    for (const param of contract.optional) {
      if (!(param in properties)) {
        findings.push({
          level: 'error',
          tool: name,
          message: `Parameter "${param}" no longer exists (renamed or removed)`
        });
      }
    }

    for (const param of contract.absent) {
      if (param in properties) {
        findings.push({
          level: 'warn',
          tool: name,
          message: `Parameter "${param}" now exists; the skill docs say it does not`
        });
      }
    }

    // A parameter the skill never sends becoming required breaks every call.
    for (const param of required) {
      const known =
        contract.required.includes(param) ||
        contract.optional.includes(param) ||
        param === 'response_format';
      if (!known) {
        findings.push({
          level: 'error',
          tool: name,
          message: `Parameter "${param}" is now required but the skill never sends it`
        });
      }
    }

    for (const [param, expected] of Object.entries(EXPECTED_ENUMS[name] || {})) {
      const actual = enumValuesOf(properties[param]);
      if (!actual) continue;
      const missing = expected.filter(value => !actual.includes(value));
      if (missing.length > 0) {
        findings.push({
          level: 'error',
          tool: name,
          message: `${param} no longer accepts: ${missing.join(', ')} (accepts: ${actual.join(', ')})`
        });
      }
    }

    for (const [param, format] of Object.entries(EXPECTED_FORMATS[name] || {})) {
      const pattern = patternOf(properties[param]);
      if (!pattern) continue;
      const expectedPattern = format === 'YYYY-MM' ? '\\d{4}-\\d{2}$' : '\\d{4}-\\d{2}-\\d{2}';
      if (!pattern.includes(expectedPattern.replace('$', ''))) {
        findings.push({
          level: 'error',
          tool: name,
          message: `${param} expects ${format} but the server pattern is ${pattern}`
        });
      }
    }
  }

  const unexpected = tools.filter(tool => !EXPECTED_TOOLS[tool.name]).map(tool => tool.name);
  for (const name of unexpected) {
    findings.push({
      level: 'info',
      tool: name,
      message: 'New tool the skill does not use yet'
    });
  }

  return findings;
}

async function main() {
  const argv = process.argv.slice(2);
  const asJson = argv.includes('--json');
  const serverArgIndex = argv.indexOf('--server');
  const serverArg = serverArgIndex >= 0 ? argv[serverArgIndex + 1] : null;

  const serverPath = resolveServerPath(serverArg);

  let result;
  try {
    result = await listTools(serverPath);
  } catch (error) {
    if (asJson) {
      console.log(JSON.stringify({ ok: false, reason: error.message }, null, 2));
    } else {
      console.error(`Could not reach the MCP server at ${serverPath}`);
      console.error(`  ${error.message}`);
    }
    process.exit(2);
  }

  const findings = check(result.serverInfo, result.tools);
  const errors = findings.filter(f => f.level === 'error');
  const warnings = findings.filter(f => f.level === 'warn');
  const infos = findings.filter(f => f.level === 'info');

  if (asJson) {
    console.log(
      JSON.stringify(
        {
          ok: errors.length === 0,
          serverVersion: (result.serverInfo && result.serverInfo.version) || null,
          toolCount: result.tools.length,
          findings
        },
        null,
        2
      )
    );
    process.exit(errors.length === 0 ? 0 : 1);
  }

  const version = (result.serverInfo && result.serverInfo.version) || 'unknown';
  console.log(`Server:  ${(result.serverInfo && result.serverInfo.name) || 'unknown'} v${version}`);
  console.log(`Tools:   ${result.tools.length} exposed, ${Object.keys(EXPECTED_TOOLS).length} expected`);
  console.log('');

  for (const finding of [...errors, ...warnings, ...infos]) {
    const label = { error: 'FAIL', warn: 'WARN', info: 'INFO' }[finding.level];
    console.log(`  [${label}] ${finding.tool}: ${finding.message}`);
  }

  if (errors.length === 0 && warnings.length === 0 && infos.length === 0) {
    console.log('  All expected tools and parameters present.');
  }

  console.log('');
  if (errors.length > 0) {
    console.log(`Parity check FAILED: ${errors.length} breaking difference(s).`);
    console.log('Update references/workflow-details.md and scripts/fetch_pinmeto_data.js.');
    process.exit(1);
  }

  console.log(`Parity check passed${warnings.length ? ` (${warnings.length} warning(s))` : ''}.`);
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error.message);
    process.exit(2);
  });
}

module.exports = { check, EXPECTED_TOOLS, EXPECTED_ENUMS };
