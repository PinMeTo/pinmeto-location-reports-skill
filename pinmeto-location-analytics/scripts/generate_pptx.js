#!/usr/bin/env node
/**
 * PinMeTo Location Analytics PowerPoint Generator
 *
 * Generates professional PPTX presentations from PinMeTo analytics data.
 * Uses PptxGenJS for slide creation with PinMeTo brand styling.
 *
 * Usage:
 *   node generate_pptx.js --data report_data.json --output report.pptx --period quarterly
 *
 * Dependencies:
 *   npm install pptxgenjs
 *
 * Author: PinMeTo
 */

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { ChartJSNodeCanvas } = require("chartjs-node-canvas");

// Chart image generator (for Keynote compatibility)
const chartWidth = 800;
const chartHeight = 500;
const chartJSNodeCanvas = new ChartJSNodeCanvas({ width: chartWidth, height: chartHeight, backgroundColour: "white" });

// Auto-detect logo path relative to script location
const SCRIPT_DIR = __dirname;
const ASSETS_DIR = path.join(SCRIPT_DIR, "..", "assets");
// Use JPG logo with white title slide background
const DEFAULT_LOGO = path.join(ASSETS_DIR, "logos", "PinMeTo_Logo_Landscape.jpg");

// =============================================================================
// PinMeTo Brand Constants
// =============================================================================
const BRAND = {
  colors: {
    blue: "3399FF",
    orange: "FF8854",
    blueMarine: "001334",
    lightBlue: "bbd9fa",
    grey: "F2F3F4",
    midGrey: "333333",
    white: "FFFFFF",
  },
  fonts: {
    heading: "Arial", // Fallback for Montserrat
    body: "Arial",
  },
};

// Chart color palette
const CHART_COLORS = [
  BRAND.colors.blue,
  BRAND.colors.orange,
  BRAND.colors.lightBlue,
  BRAND.colors.midGrey,
];

// Slide dimensions (16:9)
const SLIDE = {
  width: 10, // inches
  height: 5.625, // inches
};

// =============================================================================
// Chart Image Generation (for Keynote compatibility)
// =============================================================================

/**
 * Generate a bar chart image as base64 data URL.
 * Returns null if data is invalid or empty.
 */
async function generateBarChartImage(chartData, title, hasPriorData) {
  // Guard against empty or invalid data
  if (!chartData || !Array.isArray(chartData) || chartData.length === 0) {
    console.warn(`Warning: Empty chart data for "${title}", skipping chart`);
    return null;
  }

  const labels = chartData.map(d => d.label);
  const currentValues = chartData.map(d => d.value);
  const priorValues = chartData.map(d => d.priorValue || 0);

  const datasets = [
    {
      label: "Current Period",
      data: currentValues,
      backgroundColor: `#${BRAND.colors.blue}`,
      borderColor: `#${BRAND.colors.blue}`,
      borderWidth: 1,
    },
  ];

  if (hasPriorData) {
    datasets.push({
      label: "Prior Period",
      data: priorValues,
      backgroundColor: `#${BRAND.colors.lightBlue}`,
      borderColor: `#${BRAND.colors.lightBlue}`,
      borderWidth: 1,
    });
  }

  const configuration = {
    type: "bar",
    data: {
      labels: labels,
      datasets: datasets,
    },
    options: {
      responsive: false,
      plugins: {
        title: {
          display: true,
          text: title,
          font: { size: 16, family: "Arial" },
          color: `#${BRAND.colors.midGrey}`,
        },
        legend: {
          display: hasPriorData,
          position: "bottom",
          labels: { font: { size: 12, family: "Arial" } },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { font: { size: 11, family: "Arial" } },
        },
        x: {
          ticks: { font: { size: 11, family: "Arial" } },
        },
      },
    },
  };

  const imageBuffer = await chartJSNodeCanvas.renderToBuffer(configuration);
  return `data:image/png;base64,${imageBuffer.toString("base64")}`;
}

/**
 * Generate a pie chart image as base64 data URL
 * Uses square dimensions to prevent distortion
 */
async function generatePieChartImage(data, title) {
  // Guard against empty or invalid data
  if (!data || !Array.isArray(data) || data.length === 0) {
    console.warn(`Warning: Empty pie chart data for "${title}", skipping chart`);
    return null;
  }

  // Use square canvas for pie charts to prevent distortion
  const pieChartCanvas = new ChartJSNodeCanvas({ width: 500, height: 500, backgroundColour: "white" });

  const labels = data.map(d => d.label || d.name);
  const values = data.map(d => d.value);
  const colors = data.map((_, i) => `#${CHART_COLORS[i % CHART_COLORS.length]}`);

  const configuration = {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: colors.map(() => "#FFFFFF"),
        borderWidth: 2,
      }],
    },
    options: {
      responsive: false,
      plugins: {
        title: {
          display: true,
          text: title,
          font: { size: 18, family: "Arial" },
          color: `#${BRAND.colors.midGrey}`,
        },
        legend: {
          display: true,
          position: "bottom",
          labels: { font: { size: 14, family: "Arial" } },
        },
      },
    },
  };

  const imageBuffer = await pieChartCanvas.renderToBuffer(configuration);
  return `data:image/png;base64,${imageBuffer.toString("base64")}`;
}

// =============================================================================
// Slide Master Setup
// =============================================================================
function setupSlideMaster(pptx) {
  // Define slide master with PinMeTo branding
  pptx.defineSlideMaster({
    title: "PINMETO_MASTER",
    background: { color: BRAND.colors.white },
    objects: [
      // Header line
      {
        rect: {
          x: 0,
          y: 0,
          w: "100%",
          h: 0.05,
          fill: { color: BRAND.colors.blue },
        },
      },
      // Footer
      {
        text: {
          text: "PinMeTo Location Analytics",
          options: {
            x: 0.5,
            y: 5.3,
            w: 3,
            h: 0.25,
            fontSize: 8,
            color: BRAND.colors.midGrey,
            fontFace: BRAND.fonts.body,
          },
        },
      },
    ],
    slideNumber: { x: 9.2, y: 5.3, fontSize: 8, color: BRAND.colors.midGrey },
  });
}

// =============================================================================
// Title Slide
// =============================================================================
function createTitleSlide(pptx, data) {
  const slide = pptx.addSlide();

  // White background with JPG logo
  slide.background = { color: BRAND.colors.white };

  // Logo - use provided path or default
  // Logo aspect ratio is 2784x1259 (~2.21:1)
  const logoPath = data.logoPath || DEFAULT_LOGO;
  if (fs.existsSync(logoPath)) {
    slide.addImage({
      path: logoPath,
      x: 0.5,
      y: 0.4,
      w: 1.8,
      h: 0.81,
    });
  }

  // Company/Brand name
  const companyName = data.companyName || data.company_name;
  if (companyName) {
    slide.addText(companyName, {
      x: 0.5,
      y: 1.5,
      w: 9,
      h: 0.4,
      fontSize: 16,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
    });
  }

  // Main title
  slide.addText(data.title || "Location Analytics Report", {
    x: 0.5,
    y: companyName ? 2 : 2,
    w: 9,
    h: 1,
    fontSize: 36,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blueMarine,
    bold: true,
  });

  // Period subtitle
  slide.addText(data.period || "", {
    x: 0.5,
    y: 3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
  });

  // Current period date range
  const currentLabel = `Current Period: ${data.dateRange || ""}`;
  slide.addText(currentLabel, {
    x: 0.5,
    y: 3.6,
    w: 9,
    h: 0.3,
    fontSize: 12,
    fontFace: BRAND.fonts.body,
    color: BRAND.colors.midGrey,
  });

  // Prior period date range (for YoY comparison)
  if (data.priorPeriod && data.priorDateRange) {
    const priorLabel = `Prior Period (${data.priorPeriod}): ${data.priorDateRange}`;
    slide.addText(priorLabel, {
      x: 0.5,
      y: 3.95,
      w: 9,
      h: 0.3,
      fontSize: 12,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
    });
  }

  // Generation date
  const today = new Date().toISOString().split("T")[0];
  slide.addText(`Generated: ${today}`, {
    x: 0.5,
    y: 5,
    w: 4,
    h: 0.3,
    fontSize: 10,
    fontFace: BRAND.fonts.body,
    color: BRAND.colors.midGrey,
  });
}

// =============================================================================
// Executive Summary Slide
// =============================================================================
function createExecutiveSummary(pptx, data) {
  const slide = pptx.addSlide({ masterName: "PINMETO_MASTER" });

  // Title
  slide.addText("Executive Summary", {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
    bold: true,
  });

  // Key highlights
  const highlights = data.highlights || [];
  if (highlights.length > 0) {
    slide.addText("Key Highlights", {
      x: 0.5,
      y: 0.9,
      w: 4,
      h: 0.3,
      fontSize: 14,
      fontFace: BRAND.fonts.heading,
      color: BRAND.colors.blueMarine,
      bold: true,
    });

    highlights.forEach((highlight, i) => {
      slide.addText(`• ${highlight}`, {
        x: 0.5,
        y: 1.3 + i * 0.35,
        w: 4.5,
        h: 0.3,
        fontSize: 11,
        fontFace: BRAND.fonts.body,
        color: BRAND.colors.midGrey,
      });
    });
  }

  // KPI boxes
  const kpis = data.kpis || [];
  if (kpis.length > 0) {
    slide.addText("Performance Metrics", {
      x: 5.5,
      y: 0.9,
      w: 4,
      h: 0.3,
      fontSize: 14,
      fontFace: BRAND.fonts.heading,
      color: BRAND.colors.blueMarine,
      bold: true,
    });

    kpis.slice(0, 4).forEach((kpi, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 5.5 + col * 2.2;
      const y = 1.3 + row * 1.5;

      // KPI box
      slide.addShape(pptx.ShapeType.rect, {
        x: x,
        y: y,
        w: 2,
        h: 1.3,
        fill: { color: BRAND.colors.grey },
        line: { color: BRAND.colors.lightBlue, width: 1 },
      });

      // KPI value
      slide.addText(kpi.value || "N/A", {
        x: x,
        y: y + 0.2,
        w: 2,
        h: 0.5,
        fontSize: 20,
        fontFace: BRAND.fonts.heading,
        color: BRAND.colors.blue,
        bold: true,
        align: "center",
      });

      // KPI label
      slide.addText(kpi.name || "", {
        x: x,
        y: y + 0.7,
        w: 2,
        h: 0.25,
        fontSize: 9,
        fontFace: BRAND.fonts.body,
        color: BRAND.colors.midGrey,
        align: "center",
      });

      // KPI change
      const changeColor =
        kpi.change && kpi.change.startsWith("-")
          ? BRAND.colors.orange
          : "27ae60";
      slide.addText(kpi.change || "", {
        x: x,
        y: y + 0.95,
        w: 2,
        h: 0.2,
        fontSize: 10,
        fontFace: BRAND.fonts.body,
        color: changeColor,
        align: "center",
      });
    });
  }
}

// =============================================================================
// Metrics Slide
// =============================================================================
async function createMetricsSlide(pptx, title, metricsData, periodInfo) {
  const slide = pptx.addSlide({ masterName: "PINMETO_MASTER" });

  // Title
  slide.addText(title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
    bold: true,
  });

  // Period in footer (center, non-intrusive)
  if (periodInfo && periodInfo.period) {
    const periodText = periodInfo.priorPeriod
      ? `${periodInfo.period} vs ${periodInfo.priorPeriod}`
      : periodInfo.period;
    slide.addText(periodText, {
      x: 4,
      y: 5.3,
      w: 2,
      h: 0.25,
      fontSize: 8,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
      align: "center",
    });
  }

  // Metrics table
  const metrics = metricsData.metrics || [];
  if (metrics.length > 0) {
    const tableData = [
      [
        { text: "Metric", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Value", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "vs Prior Period", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "vs Prior Year", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
      ],
    ];

    metrics.forEach((metric, i) => {
      const rowFill = i % 2 === 0 ? BRAND.colors.white : BRAND.colors.grey;
      tableData.push([
        { text: metric.name || "", options: { fill: { color: rowFill } } },
        { text: String(metric.value || ""), options: { fill: { color: rowFill } } },
        { text: metric.periodChange || "N/A", options: { fill: { color: rowFill } } },
        { text: metric.yearChange || "N/A", options: { fill: { color: rowFill } } },
      ]);
    });

    slide.addTable(tableData, {
      x: 0.5,
      y: 1,
      w: 4.3,
      fontFace: BRAND.fonts.body,
      fontSize: 9,
      border: { pt: 0.5, color: BRAND.colors.lightBlue },
    });
  }

  // Chart section - as image for Keynote compatibility
  const chartData = metricsData.chartData || [];
  if (chartData.length > 0) {
    const hasPriorData = chartData.some(d => d.priorValue !== undefined);
    console.log(`  Adding chart image for ${title} with ${chartData.length} data points (comparison: ${hasPriorData})`);

    const chartTitle = hasPriorData ? "Current vs Prior Period" : "Monthly Trend";
    const chartImage = await generateBarChartImage(chartData, chartTitle, hasPriorData);

    slide.addImage({
      data: chartImage,
      x: 5,
      y: 1,
      w: 4.5,
      h: 3.5,
    });
  }
}

// =============================================================================
// Keywords Slide
// =============================================================================
async function createKeywordsSlide(pptx, keywordsData, periodInfo) {
  const slide = pptx.addSlide({ masterName: "PINMETO_MASTER" });

  // Title
  slide.addText("Search Keywords Analysis", {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
    bold: true,
  });

  // Period in footer (center, non-intrusive)
  if (periodInfo && periodInfo.period) {
    const periodText = periodInfo.priorPeriod
      ? `${periodInfo.period} vs ${periodInfo.priorPeriod}`
      : periodInfo.period;
    slide.addText(periodText, {
      x: 4,
      y: 5.3,
      w: 2,
      h: 0.25,
      fontSize: 8,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
      align: "center",
    });
  }

  // Keywords table
  const keywords = keywordsData.topKeywords || [];
  if (keywords.length > 0) {
    const tableData = [
      [
        { text: "#", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Keyword", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Impressions", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Category", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
      ],
    ];

    keywords.slice(0, 10).forEach((kw, i) => {
      const rowFill = i % 2 === 0 ? BRAND.colors.white : BRAND.colors.grey;
      tableData.push([
        { text: String(i + 1), options: { fill: { color: rowFill } } },
        { text: kw.keyword || "", options: { fill: { color: rowFill } } },
        { text: String(kw.impressions || ""), options: { fill: { color: rowFill } } },
        { text: kw.category || "", options: { fill: { color: rowFill } } },
      ]);
    });

    slide.addTable(tableData, {
      x: 0.5,
      y: 0.9,
      w: 5.5,
      fontFace: BRAND.fonts.body,
      fontSize: 9,
      border: { pt: 0.5, color: BRAND.colors.lightBlue },
    });
  }

  // Category distribution pie chart - as image for Keynote compatibility
  const categories = keywordsData.categoryDistribution || [];
  if (categories.length > 0) {
    console.log(`  Adding pie chart image with ${categories.length} categories`);
    const chartImage = await generatePieChartImage(categories, "Category Distribution");

    slide.addImage({
      data: chartImage,
      x: 6.2,
      y: 0.9,
      w: 3.2,
      h: 3.2,
    });
  }
}

// =============================================================================
// Reviews Sentiment Slide
// =============================================================================
async function createReviewsSlide(pptx, reviewsData, periodInfo) {
  if (!reviewsData) return;

  const slide = pptx.addSlide({ masterName: "PINMETO_MASTER" });

  // Title
  slide.addText("Review Sentiment Analysis", {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
    bold: true,
  });

  // Period in footer (center, non-intrusive)
  if (periodInfo && periodInfo.period) {
    const periodText = periodInfo.priorPeriod
      ? `${periodInfo.period} vs ${periodInfo.priorPeriod}`
      : periodInfo.period;
    slide.addText(periodText, {
      x: 4,
      y: 5.3,
      w: 2,
      h: 0.25,
      fontSize: 8,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
      align: "center",
    });
  }

  // Summary stats
  const totalReviews = reviewsData.totalReviews || 0;
  const avgRating = reviewsData.averageRating || 0;
  const ratingChange = reviewsData.ratingChange || "";

  slide.addText(`Total Reviews: ${totalReviews.toLocaleString()}  |  Average Rating: ${avgRating} (${ratingChange})`, {
    x: 0.5,
    y: 0.85,
    w: 9,
    h: 0.3,
    fontSize: 11,
    fontFace: BRAND.fonts.body,
    color: BRAND.colors.midGrey,
  });

  // Sentiment pie chart - as image for Keynote compatibility
  const sentiment = reviewsData.sentiment || {};
  if (sentiment.positive || sentiment.neutral || sentiment.negative) {
    console.log(`  Adding sentiment pie chart image`);

    // Use square canvas for pie charts to prevent distortion
    const sentimentChartCanvas = new ChartJSNodeCanvas({ width: 500, height: 500, backgroundColour: "white" });
    const configuration = {
      type: "pie",
      data: {
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [{
          data: [sentiment.positive || 0, sentiment.neutral || 0, sentiment.negative || 0],
          backgroundColor: ["#27ae60", `#${BRAND.colors.lightBlue}`, `#${BRAND.colors.orange}`],
          borderColor: ["#FFFFFF", "#FFFFFF", "#FFFFFF"],
          borderWidth: 2,
        }],
      },
      options: {
        responsive: false,
        plugins: {
          title: {
            display: true,
            text: "Sentiment Distribution (%)",
            font: { size: 18, family: "Arial" },
            color: `#${BRAND.colors.midGrey}`,
          },
          legend: {
            display: true,
            position: "bottom",
            labels: { font: { size: 14, family: "Arial" } },
          },
        },
      },
    };

    const imageBuffer = await sentimentChartCanvas.renderToBuffer(configuration);
    const chartImage = `data:image/png;base64,${imageBuffer.toString("base64")}`;

    slide.addImage({
      data: chartImage,
      x: 0.5,
      y: 1.2,
      w: 3,
      h: 3,
    });
  }

  // Top themes table
  const themes = reviewsData.topThemes || [];
  if (themes.length > 0) {
    const tableData = [
      [
        { text: "Theme", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Mentions", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
        { text: "Sentiment", options: { bold: true, fill: { color: BRAND.colors.blue }, color: BRAND.colors.white } },
      ],
    ];

    themes.slice(0, 5).forEach((theme, i) => {
      const rowFill = i % 2 === 0 ? BRAND.colors.white : BRAND.colors.grey;
      const sentimentColor = theme.sentiment === "positive" ? "27ae60" :
                            theme.sentiment === "negative" ? BRAND.colors.orange : BRAND.colors.midGrey;
      tableData.push([
        { text: theme.theme || "", options: { fill: { color: rowFill } } },
        { text: String(theme.mentions || ""), options: { fill: { color: rowFill } } },
        { text: (theme.sentiment || "").charAt(0).toUpperCase() + (theme.sentiment || "").slice(1),
          options: { fill: { color: rowFill }, color: sentimentColor } },
      ]);
    });

    // Add label above the table
    slide.addText("Top Review Themes", {
      x: 4,
      y: 1.0,
      w: 5.5,
      h: 0.3,
      fontSize: 10,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
      align: "center",
    });

    slide.addTable(tableData, {
      x: 4,
      y: 1.35,
      w: 5.5,
      fontFace: BRAND.fonts.body,
      fontSize: 9,
      border: { pt: 0.5, color: BRAND.colors.lightBlue },
    });
  }
}

// =============================================================================
// Recommendations Slide
// =============================================================================
function createRecommendationsSlide(pptx, recommendations) {
  const slide = pptx.addSlide({ masterName: "PINMETO_MASTER" });

  // Title
  slide.addText("Strategic Recommendations", {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.5,
    fontSize: 24,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.blue,
    bold: true,
  });

  // Recommendations
  const recs = recommendations || [];
  recs.slice(0, 3).forEach((rec, i) => {
    const y = 1 + i * 1.4;

    // Number circle
    slide.addShape(pptx.ShapeType.ellipse, {
      x: 0.5,
      y: y,
      w: 0.4,
      h: 0.4,
      fill: { color: BRAND.colors.orange },
    });

    slide.addText(String(i + 1), {
      x: 0.5,
      y: y,
      w: 0.4,
      h: 0.4,
      fontSize: 14,
      fontFace: BRAND.fonts.heading,
      color: BRAND.colors.white,
      bold: true,
      align: "center",
      valign: "middle",
    });

    // Title
    slide.addText(rec.title || "", {
      x: 1.1,
      y: y,
      w: 8.4,
      h: 0.35,
      fontSize: 14,
      fontFace: BRAND.fonts.heading,
      color: BRAND.colors.blueMarine,
      bold: true,
    });

    // Description
    slide.addText(rec.description || "", {
      x: 1.1,
      y: y + 0.4,
      w: 8.4,
      h: 0.5,
      fontSize: 11,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
    });

    // Impact
    if (rec.impact) {
      slide.addText(`Expected Impact: ${rec.impact}`, {
        x: 1.1,
        y: y + 0.9,
        w: 8.4,
        h: 0.3,
        fontSize: 10,
        fontFace: BRAND.fonts.body,
        color: BRAND.colors.blue,
        italic: true,
      });
    }
  });
}

// =============================================================================
// Main Generation Function
// =============================================================================
async function generateReport(data, outputPath) {
  const pptx = new PptxGenJS();

  // Presentation setup
  pptx.layout = "LAYOUT_16x9";
  pptx.title = data.title || "Location Analytics Report";
  pptx.author = "PinMeTo";
  pptx.company = "PinMeTo";

  // Setup slide master
  setupSlideMaster(pptx);

  // Period info for subtitles
  const periodInfo = { period: data.period, priorPeriod: data.priorPeriod };

  // Create slides
  createTitleSlide(pptx, data);
  createExecutiveSummary(pptx, data);

  // Platform metrics (async - generates chart images)
  if (data.google) {
    await createMetricsSlide(pptx, "Google Business Profile", data.google, periodInfo);
  }

  if (data.facebook) {
    await createMetricsSlide(pptx, "Facebook Performance", data.facebook, periodInfo);
  }

  if (data.apple) {
    await createMetricsSlide(pptx, "Apple Maps Performance", data.apple, periodInfo);
  }

  // Keywords (async - generates pie chart image)
  if (data.keywords) {
    await createKeywordsSlide(pptx, data.keywords, periodInfo);
  }

  // Reviews and Sentiment (async - generates pie chart image)
  if (data.reviews) {
    await createReviewsSlide(pptx, data.reviews, periodInfo);
  }

  // Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    createRecommendationsSlide(pptx, data.recommendations);
  }

  // Save presentation
  try {
    await pptx.writeFile({ fileName: outputPath });
    console.log(`Presentation generated: ${outputPath}`);
  } catch (err) {
    console.error("Error generating presentation:", err);
    process.exit(1);
  }
}

// =============================================================================
// CLI Interface
// =============================================================================
async function main() {
  const args = process.argv.slice(2);

  // Parse arguments
  let dataPath = null;
  let outputPath = null;
  let period = "monthly";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--data" && args[i + 1]) {
      dataPath = args[i + 1];
      i++;
    } else if (args[i] === "--output" && args[i + 1]) {
      outputPath = args[i + 1];
      i++;
    } else if (args[i] === "--period" && args[i + 1]) {
      period = args[i + 1];
      i++;
    }
  }

  if (!dataPath || !outputPath) {
    console.error("Usage: node generate_pptx.js --data <json> --output <pptx> [--period <type>]");
    process.exit(1);
  }

  // Load data with error handling
  let data;
  try {
    if (!fs.existsSync(dataPath)) {
      console.error(`Error: Data file not found: ${dataPath}`);
      process.exit(1);
    }
    data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
  } catch (e) {
    if (e instanceof SyntaxError) {
      console.error(`Error: Invalid JSON in ${dataPath}: ${e.message}`);
    } else {
      console.error(`Error reading data file: ${e.message}`);
    }
    process.exit(1);
  }

  data.periodType = data.periodType || period;

  // Generate report with error handling
  try {
    await generateReport(data, outputPath);
  } catch (e) {
    if (e.code === 'EACCES') {
      console.error(`Error: Cannot write to ${outputPath} - permission denied`);
    } else {
      console.error(`Error generating presentation: ${e.message}`);
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error("Fatal error:", err.message || err);
  process.exit(1);
});
