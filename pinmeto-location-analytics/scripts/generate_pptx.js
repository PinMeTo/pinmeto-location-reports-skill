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
      // Page number placeholder
      {
        text: {
          text: "SLIDE_NUMBER",
          options: {
            x: 9,
            y: 5.3,
            w: 0.5,
            h: 0.25,
            fontSize: 8,
            color: BRAND.colors.midGrey,
            fontFace: BRAND.fonts.body,
            align: "right",
          },
        },
      },
    ],
    slideNumber: { x: 9.3, y: 5.3, fontSize: 8, color: BRAND.colors.midGrey },
  });
}

// =============================================================================
// Title Slide
// =============================================================================
function createTitleSlide(pptx, data) {
  const slide = pptx.addSlide();

  // Dark background
  slide.background = { color: BRAND.colors.blueMarine };

  // Logo placeholder (if logo path provided)
  if (data.logoPath && fs.existsSync(data.logoPath)) {
    slide.addImage({
      path: data.logoPath,
      x: 0.5,
      y: 0.5,
      w: 2,
      h: 0.7,
    });
  }

  // Main title
  slide.addText(data.title || "Location Analytics Report", {
    x: 0.5,
    y: 2,
    w: 9,
    h: 1,
    fontSize: 36,
    fontFace: BRAND.fonts.heading,
    color: BRAND.colors.white,
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

  // Date range
  slide.addText(data.dateRange || "", {
    x: 0.5,
    y: 3.6,
    w: 9,
    h: 0.3,
    fontSize: 14,
    fontFace: BRAND.fonts.body,
    color: BRAND.colors.lightBlue,
  });

  // Generation date
  const today = new Date().toISOString().split("T")[0];
  slide.addText(`Generated: ${today}`, {
    x: 0.5,
    y: 5,
    w: 4,
    h: 0.3,
    fontSize: 10,
    fontFace: BRAND.fonts.body,
    color: BRAND.colors.lightBlue,
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
function createMetricsSlide(pptx, title, metricsData) {
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
      w: 9,
      fontFace: BRAND.fonts.body,
      fontSize: 10,
      border: { pt: 0.5, color: BRAND.colors.lightBlue },
    });
  }

  // Chart section
  const chartData = metricsData.chartData || [];
  if (chartData.length > 0) {
    slide.addChart(pptx.ChartType.bar, [
      {
        name: title,
        labels: chartData.map(d => d.label),
        values: chartData.map(d => d.value),
      },
    ], {
      x: 0.5,
      y: 3.2,
      w: 5,
      h: 2,
      chartColors: [BRAND.colors.blue],
      showLegend: false,
      showTitle: false,
      barGapWidthPct: 50,
    });
  }
}

// =============================================================================
// Keywords Slide
// =============================================================================
function createKeywordsSlide(pptx, keywordsData) {
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

  // Category distribution pie chart
  const categories = keywordsData.categoryDistribution || [];
  if (categories.length > 0) {
    slide.addChart(pptx.ChartType.pie, [
      {
        name: "Categories",
        labels: categories.map(c => c.label),
        values: categories.map(c => c.value),
      },
    ], {
      x: 6.2,
      y: 1,
      w: 3.3,
      h: 2.5,
      chartColors: CHART_COLORS,
      showLegend: true,
      legendPos: "b",
      showTitle: false,
    });

    slide.addText("Category Distribution", {
      x: 6.2,
      y: 3.6,
      w: 3.3,
      h: 0.3,
      fontSize: 10,
      fontFace: BRAND.fonts.body,
      color: BRAND.colors.midGrey,
      align: "center",
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
function generateReport(data, outputPath) {
  const pptx = new PptxGenJS();

  // Presentation setup
  pptx.layout = "LAYOUT_16x9";
  pptx.title = data.title || "Location Analytics Report";
  pptx.author = "PinMeTo";
  pptx.company = "PinMeTo";

  // Setup slide master
  setupSlideMaster(pptx);

  // Create slides
  createTitleSlide(pptx, data);
  createExecutiveSummary(pptx, data);

  // Platform metrics
  if (data.google) {
    createMetricsSlide(pptx, "Google Business Profile", data.google);
  }

  if (data.facebook) {
    createMetricsSlide(pptx, "Facebook Performance", data.facebook);
  }

  if (data.apple) {
    createMetricsSlide(pptx, "Apple Maps Performance", data.apple);
  }

  // Keywords
  if (data.keywords) {
    createKeywordsSlide(pptx, data.keywords);
  }

  // Recommendations
  if (data.recommendations && data.recommendations.length > 0) {
    createRecommendationsSlide(pptx, data.recommendations);
  }

  // Save presentation
  pptx.writeFile({ fileName: outputPath })
    .then(() => {
      console.log(`Presentation generated: ${outputPath}`);
    })
    .catch((err) => {
      console.error("Error generating presentation:", err);
      process.exit(1);
    });
}

// =============================================================================
// CLI Interface
// =============================================================================
function main() {
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

  // Load data
  const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
  data.periodType = data.periodType || period;

  // Generate report
  generateReport(data, outputPath);
}

main();
