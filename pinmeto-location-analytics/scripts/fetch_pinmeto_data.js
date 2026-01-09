#!/usr/bin/env node
/**
 * Fetch real data from PinMeTo MCP server and format for report generation.
 *
 * Usage:
 *   node scripts/fetch_pinmeto_data.js --year 2025 --output real_data.json
 */

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// MCP Server configuration
const MCP_SERVER_PATH = path.join(
  process.env.HOME,
  'Library/Application Support/Claude/Claude Extensions/local.mcpb.pinmeto.pinmetopinmeto-location-mcp/build/index.js'
);

// Environment variables for authentication (must be set externally)
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

const MCP_ENV = {
  ...process.env
  // Credentials are read from process.env:
  // - PINMETO_ACCOUNT_ID
  // - PINMETO_APP_ID
  // - PINMETO_APP_SECRET
};

class MCPClient {
  constructor() {
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.serverProcess = null;
    this.rl = null;
  }

  async start() {
    return new Promise((resolve, reject) => {
      this.serverProcess = spawn('node', [MCP_SERVER_PATH], {
        env: MCP_ENV,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.rl = readline.createInterface({
        input: this.serverProcess.stdout,
        crlfDelay: Infinity
      });

      this.rl.on('line', (line) => {
        try {
          const response = JSON.parse(line);
          const pending = this.pendingRequests.get(response.id);
          if (pending) {
            this.pendingRequests.delete(response.id);
            if (response.error) {
              pending.reject(new Error(response.error.message));
            } else {
              pending.resolve(response.result);
            }
          }
        } catch (e) {
          // Ignore non-JSON lines (like stderr messages)
        }
      });

      this.serverProcess.stderr.on('data', (data) => {
        const msg = data.toString();
        if (msg.includes('PinMeTo MCP running')) {
          // Server is ready, initialize it
          this.initialize().then(resolve).catch(reject);
        } else {
          console.error('[MCP]', msg.trim());
        }
      });

      this.serverProcess.on('error', reject);
    });
  }

  async sendRequest(method, params = {}) {
    const id = ++this.requestId;
    const request = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');

      // Timeout after 60 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error(`Request timeout: ${method}`));
        }
      }, 60000);
    });
  }

  async initialize() {
    return this.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'pinmeto-report-generator',
        version: '1.0.0'
      }
    });
  }

  async callTool(name, args) {
    const result = await this.sendRequest('tools/call', { name, arguments: args });
    return result;
  }

  /**
   * Call a tool with automatic retry on failure.
   * Uses exponential backoff: 1s, 2s, 4s delays between retries.
   */
  async callToolWithRetry(name, args, maxRetries = 3) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await this.callTool(name, args);
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries - 1) {
          const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
          console.log(`[Retry ${attempt + 1}/${maxRetries}] ${name} failed: ${error.message}. Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw new Error(`${name} failed after ${maxRetries} attempts: ${lastError.message}`);
  }

  stop() {
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
  }
}

// Helper to extract structured content from MCP response
function extractData(result) {
  if (result.structuredContent) {
    return result.structuredContent;
  }
  // Try to parse from text content
  if (result.content && result.content[0] && result.content[0].text) {
    try {
      return JSON.parse(result.content[0].text);
    } catch (e) {
      return { raw: result.content[0].text };
    }
  }
  return result;
}

// Format large numbers for display
function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return String(num);
}

// Calculate change percentage
function calcChange(current, prior) {
  if (!prior || prior === 0) return 'N/A';
  const change = ((current - prior) / prior * 100).toFixed(0);
  return change >= 0 ? `+${change}%` : `${change}%`;
}

async function fetchPinMeToData(year) {
  const client = new MCPClient();

  console.log('Starting PinMeTo MCP server...');
  await client.start();
  console.log('MCP server ready');

  // Date ranges for full year
  const fromDate = `${year}-01-01`;
  const toDate = `${year}-12-31`;
  const priorFromDate = `${year - 1}-01-01`;
  const priorToDate = `${year - 1}-12-31`;

  // For keywords (monthly format)
  const fromMonth = `${year}-01`;
  const toMonth = `${year}-12`;

  const reportData = {
    companyName: 'PinMeTo',
    title: 'Location Analytics Report',
    period: `${year}`,
    priorPeriod: `${year - 1}`,
    dateRange: `January 1 - December 31, ${year}`,
    priorDateRange: `January 1 - December 31, ${year - 1}`,
    highlights: [],
    kpis: [],
    google: { metrics: [], chartData: [] },
    facebook: { metrics: [], chartData: [] },
    apple: { metrics: [], chartData: [] },
    keywords: { topKeywords: [], categoryDistribution: [] },
    reviews: {
      totalReviews: 0,
      averageRating: 0,
      ratingChange: '',
      sentiment: { positive: 0, neutral: 0, negative: 0 },
      topThemes: [],
      recentHighlights: []
    },
    recommendations: []
  };

  try {
    // Fetch Google Insights with YoY comparison
    console.log('Fetching Google insights...');
    const googleResult = await client.callToolWithRetry('pinmeto_get_google_insights', {
      from: fromDate,
      to: toDate,
      aggregation: 'monthly',
      compare_with: 'prior_year',
      response_format: 'json'
    });
    const googleData = extractData(googleResult);
    console.log('Google insights received');

    if (googleData.insights) {
      // Process Google metrics
      const insights = Array.isArray(googleData.insights) ? googleData.insights : [googleData.insights];

      // Aggregate totals
      let totalViews = 0, totalSearches = 0, totalWebClicks = 0, totalDirections = 0, totalCalls = 0;
      let priorViews = 0, priorSearches = 0, priorWebClicks = 0, priorDirections = 0, priorCalls = 0;

      for (const insight of insights) {
        if (insight.metrics) {
          totalViews += insight.metrics.BUSINESS_IMPRESSIONS_DESKTOP_MAPS || 0;
          totalViews += insight.metrics.BUSINESS_IMPRESSIONS_MOBILE_MAPS || 0;
          totalSearches += insight.metrics.BUSINESS_IMPRESSIONS_DESKTOP_SEARCH || 0;
          totalSearches += insight.metrics.BUSINESS_IMPRESSIONS_MOBILE_SEARCH || 0;
          totalWebClicks += insight.metrics.WEBSITE_CLICKS || 0;
          totalDirections += insight.metrics.BUSINESS_DIRECTION_REQUESTS || 0;
          totalCalls += insight.metrics.CALL_CLICKS || 0;
        }
        if (insight.comparison) {
          priorViews += insight.comparison.BUSINESS_IMPRESSIONS_DESKTOP_MAPS?.prior || 0;
          priorViews += insight.comparison.BUSINESS_IMPRESSIONS_MOBILE_MAPS?.prior || 0;
          priorSearches += insight.comparison.BUSINESS_IMPRESSIONS_DESKTOP_SEARCH?.prior || 0;
          priorSearches += insight.comparison.BUSINESS_IMPRESSIONS_MOBILE_SEARCH?.prior || 0;
          priorWebClicks += insight.comparison.WEBSITE_CLICKS?.prior || 0;
          priorDirections += insight.comparison.BUSINESS_DIRECTION_REQUESTS?.prior || 0;
          priorCalls += insight.comparison.CALL_CLICKS?.prior || 0;
        }
      }

      reportData.google.metrics = [
        { name: 'Profile Views', value: totalViews, periodChange: 'N/A', yearChange: calcChange(totalViews, priorViews) },
        { name: 'Search Impressions', value: totalSearches, periodChange: 'N/A', yearChange: calcChange(totalSearches, priorSearches) },
        { name: 'Website Clicks', value: totalWebClicks, periodChange: 'N/A', yearChange: calcChange(totalWebClicks, priorWebClicks) },
        { name: 'Direction Requests', value: totalDirections, periodChange: 'N/A', yearChange: calcChange(totalDirections, priorDirections) },
        { name: 'Phone Calls', value: totalCalls, periodChange: 'N/A', yearChange: calcChange(totalCalls, priorCalls) }
      ];

      // Build chart data from monthly breakdown
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      reportData.google.chartData = monthNames.map((label, i) => {
        const monthInsight = insights.find(ins => {
          const date = ins.date || ins.period;
          return date && date.includes(`${year}-${String(i + 1).padStart(2, '0')}`);
        });
        const value = monthInsight?.metrics ?
          (monthInsight.metrics.BUSINESS_IMPRESSIONS_DESKTOP_MAPS || 0) +
          (monthInsight.metrics.BUSINESS_IMPRESSIONS_MOBILE_MAPS || 0) : 0;
        return { label, value, priorValue: 0 };
      });

      // Add to KPIs
      reportData.kpis.push(
        { name: 'Google Views', value: formatNumber(totalViews), change: calcChange(totalViews, priorViews) }
      );
    }

    // Fetch Facebook Insights
    console.log('Fetching Facebook insights...');
    try {
      const fbResult = await client.callToolWithRetry('pinmeto_get_facebook_insights', {
        from: fromDate,
        to: toDate,
        aggregation: 'monthly',
        compare_with: 'prior_year',
        response_format: 'json'
      });
      const fbData = extractData(fbResult);
      console.log('Facebook insights received');

      if (fbData.insights) {
        const insights = Array.isArray(fbData.insights) ? fbData.insights : [fbData.insights];

        let totalPageViews = 0, totalReach = 0, totalEngagement = 0, totalClicks = 0;
        let priorPageViews = 0, priorReach = 0, priorEngagement = 0, priorClicks = 0;

        for (const insight of insights) {
          if (insight.metrics) {
            totalPageViews += insight.metrics.PAGE_VIEWS_TOTAL || 0;
            totalReach += insight.metrics.PAGE_IMPRESSIONS || 0;
            totalEngagement += insight.metrics.PAGE_ENGAGED_USERS || 0;
            totalClicks += insight.metrics.PAGE_CONSUMPTIONS || 0;
          }
        }

        reportData.facebook.metrics = [
          { name: 'Page Views', value: totalPageViews, periodChange: 'N/A', yearChange: calcChange(totalPageViews, priorPageViews) },
          { name: 'Reach', value: totalReach, periodChange: 'N/A', yearChange: calcChange(totalReach, priorReach) },
          { name: 'Engagement', value: totalEngagement, periodChange: 'N/A', yearChange: calcChange(totalEngagement, priorEngagement) },
          { name: 'Post Clicks', value: totalClicks, periodChange: 'N/A', yearChange: calcChange(totalClicks, priorClicks) }
        ];

        reportData.kpis.push(
          { name: 'FB Reach', value: formatNumber(totalReach), change: calcChange(totalReach, priorReach) }
        );
      }
    } catch (e) {
      console.log('Facebook insights not available:', e.message);
    }

    // Fetch Apple Insights
    console.log('Fetching Apple insights...');
    try {
      const appleResult = await client.callToolWithRetry('pinmeto_get_apple_insights', {
        from: fromDate,
        to: toDate,
        aggregation: 'monthly',
        compare_with: 'prior_year',
        response_format: 'json'
      });
      const appleData = extractData(appleResult);
      console.log('Apple insights received');

      if (appleData.insights) {
        const insights = Array.isArray(appleData.insights) ? appleData.insights : [appleData.insights];

        let totalViews = 0, totalDirections = 0, totalWebClicks = 0;

        for (const insight of insights) {
          if (insight.metrics) {
            totalViews += insight.metrics.TOTAL_VIEWS || insight.metrics.totalViews || 0;
            totalDirections += insight.metrics.TOTAL_DIRECTIONS || insight.metrics.totalDirections || 0;
            totalWebClicks += insight.metrics.TOTAL_WEBSITE || insight.metrics.totalWebsite || 0;
          }
        }

        reportData.apple.metrics = [
          { name: 'Discovery Views', value: totalViews, periodChange: 'N/A', yearChange: 'N/A' },
          { name: 'Direction Requests', value: totalDirections, periodChange: 'N/A', yearChange: 'N/A' },
          { name: 'Website Clicks', value: totalWebClicks, periodChange: 'N/A', yearChange: 'N/A' }
        ];
      }
    } catch (e) {
      console.log('Apple insights not available:', e.message);
    }

    // Fetch Google Keywords
    console.log('Fetching Google keywords...');
    try {
      const kwResult = await client.callToolWithRetry('pinmeto_get_google_keywords', {
        from: fromMonth,
        to: toMonth,
        response_format: 'json'
      });
      const kwData = extractData(kwResult);
      console.log('Keywords received');

      if (kwData.data && Array.isArray(kwData.data)) {
        // Aggregate keywords across all locations
        const keywordMap = new Map();
        for (const locationData of kwData.data) {
          const keywords = locationData.keywords || [];
          for (const kw of keywords) {
            const existing = keywordMap.get(kw.keyword) || { keyword: kw.keyword, impressions: 0 };
            existing.impressions += kw.impressions || 0;
            keywordMap.set(kw.keyword, existing);
          }
        }

        // Sort by impressions and take top 10
        const sortedKeywords = Array.from(keywordMap.values())
          .sort((a, b) => b.impressions - a.impressions)
          .slice(0, 10);

        // Categorize keywords
        reportData.keywords.topKeywords = sortedKeywords.map(kw => {
          let category = 'Discovery';
          if (kw.keyword.toLowerCase().includes('pinmeto')) category = 'Branded';
          else if (kw.keyword.toLowerCase().includes('login') || kw.keyword.toLowerCase().includes('pricing')) category = 'Navigational';
          return { keyword: kw.keyword, impressions: kw.impressions, category };
        });

        // Calculate distribution
        const categories = { Branded: 0, Discovery: 0, Navigational: 0 };
        for (const kw of reportData.keywords.topKeywords) {
          categories[kw.category] += kw.impressions;
        }
        const total = Object.values(categories).reduce((a, b) => a + b, 0);
        reportData.keywords.categoryDistribution = Object.entries(categories).map(([label, value]) => ({
          label,
          value: total > 0 ? Math.round(value / total * 100) : 0
        }));
      }
    } catch (e) {
      console.log('Keywords not available:', e.message);
    }

    // Fetch Google Ratings
    console.log('Fetching Google ratings...');
    try {
      const ratingsResult = await client.callToolWithRetry('pinmeto_get_google_ratings', {
        from: fromDate,
        to: toDate,
        response_format: 'json'
      });
      const ratingsData = extractData(ratingsResult);
      console.log('Ratings received');

      if (ratingsData.data) {
        const data = Array.isArray(ratingsData.data) ? ratingsData.data : [ratingsData.data];
        let totalReviews = 0, totalRatingSum = 0;
        const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };

        for (const loc of data) {
          totalReviews += loc.totalReviews || 0;
          totalRatingSum += (loc.averageRating || 0) * (loc.totalReviews || 0);
          if (loc.distribution) {
            for (const [rating, count] of Object.entries(loc.distribution)) {
              distribution[rating] = (distribution[rating] || 0) + count;
            }
          }
        }

        const avgRating = totalReviews > 0 ? (totalRatingSum / totalReviews).toFixed(1) : 0;

        reportData.reviews.totalReviews = totalReviews;
        reportData.reviews.averageRating = parseFloat(avgRating);
        reportData.reviews.ratingChange = '+0.0'; // Would need prior year data

        // Calculate sentiment from distribution
        const positive = distribution[4] + distribution[5];
        const neutral = distribution[3];
        const negative = distribution[1] + distribution[2];
        const sentimentTotal = positive + neutral + negative;

        reportData.reviews.sentiment = {
          positive: sentimentTotal > 0 ? Math.round(positive / sentimentTotal * 100) : 0,
          neutral: sentimentTotal > 0 ? Math.round(neutral / sentimentTotal * 100) : 0,
          negative: sentimentTotal > 0 ? Math.round(negative / sentimentTotal * 100) : 0
        };

        reportData.kpis.push(
          { name: 'Avg Rating', value: String(avgRating), change: '+0.0' },
          { name: 'Reviews', value: formatNumber(totalReviews), change: 'N/A' }
        );
      }
    } catch (e) {
      console.log('Ratings not available:', e.message);
    }

    // Fetch recent reviews for highlights
    console.log('Fetching recent reviews...');
    try {
      const reviewsResult = await client.callToolWithRetry('pinmeto_get_google_reviews', {
        from: fromDate,
        to: toDate,
        limit: 10,
        minRating: 4,
        response_format: 'json'
      });
      const reviewsData = extractData(reviewsResult);
      console.log('Reviews received');

      if (reviewsData.data && Array.isArray(reviewsData.data)) {
        reportData.reviews.recentHighlights = reviewsData.data
          .filter(r => r.comment && r.comment.length > 10)
          .slice(0, 3)
          .map(r => ({
            text: r.comment.substring(0, 100) + (r.comment.length > 100 ? '...' : ''),
            rating: r.rating,
            date: r.date
          }));
      }
    } catch (e) {
      console.log('Reviews not available:', e.message);
    }

    // Generate highlights based on data
    const googleViews = reportData.google.metrics.find(m => m.name === 'Profile Views');
    if (googleViews && googleViews.value > 0) {
      reportData.highlights.push(`Total Google views: ${formatNumber(googleViews.value)} (${googleViews.yearChange} YoY)`);
    }
    if (reportData.reviews.averageRating > 0) {
      reportData.highlights.push(`Average Google rating: ${reportData.reviews.averageRating} stars across all locations`);
    }
    if (reportData.reviews.totalReviews > 0) {
      reportData.highlights.push(`Received ${formatNumber(reportData.reviews.totalReviews)} reviews during the period`);
    }

    // Generate recommendations
    reportData.recommendations = [
      {
        title: 'Optimize Google Business Profiles',
        description: 'Review and update location descriptions with high-performing keywords to improve discovery visibility.',
        impact: 'Projected increase in search impressions'
      },
      {
        title: 'Respond to Reviews',
        description: 'Maintain high response rates to customer reviews to improve engagement and customer satisfaction.',
        impact: 'Improved customer trust and loyalty'
      },
      {
        title: 'Monitor Competitor Activity',
        description: 'Track competitor presence on local platforms to identify opportunities for differentiation.',
        impact: 'Better market positioning'
      }
    ];

  } catch (e) {
    console.error('Error fetching data:', e);
  } finally {
    client.stop();
  }

  return reportData;
}

// Main
async function main() {
  // Validate credentials before proceeding
  validateCredentials();

  const args = process.argv.slice(2);
  let year = 2025;
  let outputPath = 'real_data.json';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--year' && args[i + 1]) {
      year = parseInt(args[i + 1], 10);
    }
    if (args[i] === '--output' && args[i + 1]) {
      outputPath = args[i + 1];
    }
  }

  console.log(`Fetching PinMeTo data for ${year}...`);
  const data = await fetchPinMeToData(year);

  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
  console.log(`Data saved to ${outputPath}`);
}

main().catch(console.error);
