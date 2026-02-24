/* =========================================================================
   app.js -- Static dashboard that reads pre-computed results from Supabase.
   No backend server required. Deployed on Cloudflare Pages.
   ========================================================================= */

const SUPABASE_URL  = "https://ltgghjqptfokkidbiaif.supabase.co";
const SUPABASE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjM2ODgsImV4cCI6MjA4NzQ5OTY4OH0.VUVXG33fT8rlBdHwuyzqsCKnQeK21Bd92namuMdRWFY";

const sb = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const COLORS = ["#0f3460", "#e94560", "#16c79a", "#f5a623", "#7b68ee", "#00bcd4", "#ff6b6b", "#6c5ce7"];
const SET2   = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"];

const plotLayout = {
    font: { family: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size: 12 },
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { l: 50, r: 20, t: 40, b: 40 },
};

/* -- Navigation ----------------------------------------------------------- */

document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
        document.getElementById("page-" + btn.dataset.page).classList.add("active");
    });
});

/* -- Helpers -------------------------------------------------------------- */

function fmt(n) { return typeof n === "number" ? n.toLocaleString(undefined, { maximumFractionDigits: 2 }) : n; }
function title(s) { return s.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()); }

function metricCard(label, value, sub) {
    return `<div class="metric-card"><div class="metric-label">${label}</div><div class="metric-value">${value}</div>${sub ? `<div class="metric-sub">${sub}</div>` : ""}</div>`;
}

function makeTable(headers, rows) {
    let h = "<table class='data-table'><thead><tr>" + headers.map(h => `<th>${h}</th>`).join("") + "</tr></thead><tbody>";
    rows.forEach(r => { h += "<tr>" + r.map(c => `<td>${fmt(c)}</td>`).join("") + "</tr>"; });
    return h + "</tbody></table>";
}

function showLoading()  { document.getElementById("loading").classList.remove("hidden"); }
function hideLoading()  { document.getElementById("loading").classList.add("hidden"); }

function setStatus(ok) {
    const dot  = document.querySelector(".status-dot");
    const text = document.querySelector(".status-text");
    dot.className = "status-dot " + (ok ? "connected" : "error");
    text.textContent = ok ? "Supabase Connected" : "Connection Failed";
}

/* -- Data fetchers -------------------------------------------------------- */

async function fetchAll(table) {
    let all = [], offset = 0, limit = 1000;
    while (true) {
        const { data, error } = await sb.from(table).select("*").range(offset, offset + limit - 1);
        if (error) throw error;
        if (!data || data.length === 0) break;
        all = all.concat(data);
        if (data.length < limit) break;
        offset += limit;
    }
    return all;
}

/* -- Page: Overview ------------------------------------------------------- */

async function renderOverview() {
    const stats = await fetchAll("data_stats");
    if (!stats.length) return;

    const rowCount = stats[0].row_count;
    const metricsHtml = metricCard("Total Records", rowCount.toLocaleString()) +
        metricCard("Features", stats.length) +
        metricCard("Numeric Features", stats.length);
    document.getElementById("overview-metrics").innerHTML = metricsHtml;

    // Stats table
    const headers = ["Feature", "Mean", "Std Dev", "Min", "Max", "Median"];
    const rows = stats.map(s => [title(s.feature_name), s.mean_val, s.std_val, s.min_val, s.max_val, s.median_val]);
    document.getElementById("stats-table-wrap").innerHTML = makeTable(headers, rows);

    // Distribution histograms from raw_data
    const raw = await fetchAll("raw_data");
    if (!raw.length) return;

    const container = document.getElementById("distribution-charts");
    container.innerHTML = "";
    const features = ["cpu_usage", "memory_usage", "network_usage", "disk_io", "energy_consumption", "service_latency"];
    features.forEach((feat, i) => {
        const vals = raw.map(r => r[feat]).filter(v => v != null);
        if (!vals.length) return;
        const div = document.createElement("div");
        div.id = "dist-" + feat;
        container.appendChild(div);
        Plotly.newPlot(div.id, [{
            x: vals, type: "histogram", nbinsx: 30,
            marker: { color: COLORS[0] },
        }], {
            ...plotLayout,
            title: { text: title(feat), font: { size: 13 } },
            height: 260,
            xaxis: { title: "" },
            yaxis: { title: "Count" },
        }, { responsive: true, displayModeBar: false });
    });
}

/* -- Page: Outliers ------------------------------------------------------- */

async function renderOutliers() {
    const data = await fetchAll("outlier_counts");
    if (!data.length) return;

    const total = data.reduce((s, d) => s + d.outlier_count, 0);
    const sorted = [...data].sort((a, b) => b.outlier_count - a.outlier_count);

    document.getElementById("outlier-metrics").innerHTML =
        metricCard("Total Outliers", total.toLocaleString()) +
        metricCard("Most Outliers", title(sorted[0].feature_name)) +
        metricCard("Fewest Outliers", title(sorted[sorted.length - 1].feature_name));

    const sortedAsc = [...data].sort((a, b) => a.outlier_count - b.outlier_count);
    Plotly.newPlot("outlier-chart", [{
        y: sortedAsc.map(d => title(d.feature_name)),
        x: sortedAsc.map(d => d.outlier_count),
        type: "bar", orientation: "h",
        marker: { color: sortedAsc.map((_, i) => `rgba(15,52,96,${0.3 + 0.7 * i / sortedAsc.length})`) },
    }], {
        ...plotLayout,
        height: Math.max(300, data.length * 30),
        xaxis: { title: "Number of Outliers" },
        yaxis: { title: "" },
    }, { responsive: true, displayModeBar: false });

    const headers = ["Feature", "Outlier Count"];
    const rows = sorted.map(d => [title(d.feature_name), d.outlier_count]);
    document.getElementById("outlier-table-wrap").innerHTML = makeTable(headers, rows);
}

/* -- Page: Correlation ---------------------------------------------------- */

async function renderCorrelation() {
    const data = await fetchAll("correlation_data");
    if (!data.length) return;

    const columns = JSON.parse(data[0].columns_list);
    const matrix  = JSON.parse(data[0].matrix_data);
    const labels  = columns.map(title);

    const annotations = [];
    for (let i = 0; i < matrix.length; i++) {
        for (let j = 0; j < matrix[i].length; j++) {
            annotations.push({
                x: labels[j], y: labels[i],
                text: matrix[i][j].toFixed(2),
                showarrow: false,
                font: { size: 10, color: Math.abs(matrix[i][j]) > 0.5 ? "#fff" : "#333" },
            });
        }
    }

    Plotly.newPlot("correlation-chart", [{
        z: matrix, x: labels, y: labels,
        type: "heatmap", colorscale: "RdBu", reversescale: true,
        zmid: 0, zmin: -1, zmax: 1,
    }], {
        ...plotLayout,
        height: 550, width: null,
        annotations: annotations,
        xaxis: { tickangle: -45 },
    }, { responsive: true, displayModeBar: false });
}

/* -- Page: Elbow ---------------------------------------------------------- */

async function renderElbow() {
    const data = await fetchAll("elbow_data");
    if (!data.length) return;

    const sorted = [...data].sort((a, b) => a.k - b.k);
    Plotly.newPlot("elbow-chart", [{
        x: sorted.map(d => d.k),
        y: sorted.map(d => d.inertia),
        type: "scatter", mode: "lines+markers",
        line: { color: COLORS[0], width: 2 },
        marker: { size: 8 },
    }], {
        ...plotLayout,
        height: 400,
        title: { text: "Elbow Method - Inertia vs Number of Clusters", font: { size: 14 } },
        xaxis: { title: "Number of Clusters (K)", dtick: 1 },
        yaxis: { title: "Inertia" },
    }, { responsive: true, displayModeBar: false });
}

/* -- Page: Clustering ----------------------------------------------------- */

async function renderClustering() {
    const summary = await fetchAll("cluster_summary");
    if (!summary.length) return;

    const sorted = [...summary].sort((a, b) => a.cluster_id - b.cluster_id);
    const totalRecords = sorted.reduce((s, c) => s + (c.record_count || 0), 0);

    document.getElementById("cluster-metrics").innerHTML =
        metricCard("Clusters", sorted.length) +
        metricCard("Total Records", totalRecords.toLocaleString()) +
        metricCard("Largest Cluster", "Cluster " + sorted.reduce((a, b) => (b.record_count || 0) > (a.record_count || 0) ? b : a).cluster_id);

    // Pie
    Plotly.newPlot("cluster-pie-chart", [{
        labels: sorted.map(c => "Cluster " + c.cluster_id),
        values: sorted.map(c => c.record_count),
        type: "pie",
        marker: { colors: SET2 },
        textinfo: "label+percent",
    }], { ...plotLayout, height: 340, showlegend: false }, { responsive: true, displayModeBar: false });

    // Bar
    Plotly.newPlot("cluster-bar-chart", [{
        x: sorted.map(c => "Cluster " + c.cluster_id),
        y: sorted.map(c => c.record_count),
        type: "bar",
        marker: { color: SET2.slice(0, sorted.length) },
    }], { ...plotLayout, height: 340, xaxis: { title: "" }, yaxis: { title: "Count" } }, { responsive: true, displayModeBar: false });

    // Summary table
    const featureCols = ["cpu_usage_mean", "memory_usage_mean", "network_usage_mean", "disk_io_mean", "energy_consumption_mean", "service_latency_mean"];
    const availCols = featureCols.filter(f => sorted[0][f] !== undefined);
    const headers = ["Cluster", "Records", ...availCols.map(c => title(c.replace("_mean", "")))];
    const rows = sorted.map(c => [c.cluster_id, c.record_count, ...availCols.map(f => c[f] != null ? c[f].toFixed(2) : "-")]);
    document.getElementById("cluster-summary-table-wrap").innerHTML = makeTable(headers, rows);
}

/* -- Page: Exploration ---------------------------------------------------- */

async function renderExploration() {
    const summary = await fetchAll("cluster_summary");
    if (!summary.length) return;

    const sorted = [...summary].sort((a, b) => a.cluster_id - b.cluster_id);
    const featureCols = ["cpu_usage_mean", "memory_usage_mean", "network_usage_mean", "disk_io_mean", "energy_consumption_mean", "service_latency_mean"];
    const featureNames = ["CPU Usage", "Memory Usage", "Network Usage", "Disk IO", "Energy", "Latency"];
    const availIdx = featureCols.map((f, i) => sorted[0][f] !== undefined ? i : -1).filter(i => i >= 0);

    // Radar
    const radarTraces = sorted.map((c, ci) => {
        const vals = availIdx.map(i => c[featureCols[i]] || 0);
        return {
            r: [...vals, vals[0]],
            theta: [...availIdx.map(i => featureNames[i]), featureNames[availIdx[0]]],
            type: "scatterpolar", fill: "toself",
            name: `Cluster ${c.cluster_id} (n=${c.record_count || "?"})`,
            line: { color: SET2[ci % SET2.length] },
            opacity: 0.65,
        };
    });
    Plotly.newPlot("radar-chart", radarTraces, {
        ...plotLayout, height: 480,
        polar: { radialaxis: { visible: true } },
        title: { text: "Cluster Feature Profiles (Radar Chart)", font: { size: 14 } },
    }, { responsive: true, displayModeBar: false });

    // Grouped bar comparison
    const barTraces = sorted.map((c, ci) => ({
        x: availIdx.map(i => featureNames[i]),
        y: availIdx.map(i => c[featureCols[i]] || 0),
        name: "Cluster " + c.cluster_id,
        type: "bar",
        marker: { color: SET2[ci % SET2.length] },
    }));
    Plotly.newPlot("comparison-chart", barTraces, {
        ...plotLayout, height: 400, barmode: "group",
        xaxis: { title: "" }, yaxis: { title: "Mean Value" },
    }, { responsive: true, displayModeBar: false });
}

/* -- Page: t-SNE ---------------------------------------------------------- */

async function renderTSNE() {
    const data = await fetchAll("tsne_data");
    if (!data.length) return;

    const clusters = [...new Set(data.map(d => d.cluster_id))].sort();
    const traces = clusters.map(cid => {
        const pts = data.filter(d => d.cluster_id === cid);
        return {
            x: pts.map(p => p.x), y: pts.map(p => p.y),
            mode: "markers", type: "scatter",
            name: "Cluster " + cid,
            marker: { size: 5, opacity: 0.7, color: SET2[cid % SET2.length] },
        };
    });

    Plotly.newPlot("tsne-chart", traces, {
        ...plotLayout, height: 550,
        title: { text: "t-SNE Cluster Visualization", font: { size: 14 } },
        xaxis: { title: "t-SNE 1" },
        yaxis: { title: "t-SNE 2" },
    }, { responsive: true, displayModeBar: false });
}

/* -- Init ----------------------------------------------------------------- */

async function init() {
    showLoading();
    try {
        // Quick connectivity check
        const { data, error } = await sb.from("data_stats").select("feature_name").limit(1);
        if (error) throw error;
        setStatus(true);

        await Promise.all([
            renderOverview(),
            renderOutliers(),
            renderCorrelation(),
            renderElbow(),
            renderClustering(),
            renderExploration(),
            renderTSNE(),
        ]);
    } catch (e) {
        setStatus(false);
        console.error("Init error:", e);
    }
    hideLoading();
}

init();
