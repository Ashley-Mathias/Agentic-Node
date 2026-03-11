/**
 * Renders API response payloads into bot bubble HTML.
 */
import { escapeHtml } from "./utils.js";

let _downloadId = 0;

export function buildBotContentHtml(data) {
  let html = "";

  if (data.error) {
    html += '<div class="bubble-error">' + escapeHtml(data.error) + "</div>";
  }

  if (data.summary) {
    html += "<p>" + escapeHtml(data.summary).replace(/\n/g, "<br>") + "</p>";
  }

  if (data.table && Array.isArray(data.table) && data.table.length > 0) {
    const keys = Object.keys(data.table[0]);
    let thead = "<tr>";
    keys.forEach((k) => { thead += "<th>" + escapeHtml(k) + "</th>"; });
    thead += "</tr>";
    let tbody = "";
    data.table.forEach((row) => {
      tbody += "<tr>";
      keys.forEach((k) => {
        const val = row[k];
        tbody += "<td>" + escapeHtml(val != null ? String(val) : "") + "</td>";
      });
      tbody += "</tr>";
    });
    const tableId = "dl-table-" + (++_downloadId);
    html += '<div class="bubble-table-wrap" id="' + tableId + '"><table><thead>' + thead + "</thead><tbody>" + tbody + "</tbody></table></div>";
    html += '<button type="button" class="btn-download btn-download-csv" data-table-id="' + tableId + '">'
      + '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>'
      + " Download CSV</button>";
  }

  if (data.chart_image) {
    const chartId = "dl-chart-" + (++_downloadId);
    html += '<div class="bubble-chart"><img id="' + chartId + '" src="data:image/png;base64,' + data.chart_image + '" alt="Chart" /></div>';
    html += '<button type="button" class="btn-download btn-download-png" data-chart-id="' + chartId + '">'
      + '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>'
      + " Download PNG</button>";
  }

  if (data.sql_query) {
    html += '<div class="bubble-sql"><span class="bubble-sql-label">Generated SQL</span>' + escapeHtml(data.sql_query) + "</div>";
  }

  return html || "<p>No response content.</p>";
}

/* ---- Download handlers (delegated from messages container) ---- */

function downloadCsv(tableWrap) {
  const table = tableWrap.querySelector("table");
  if (!table) return;
  const rows = [];
  table.querySelectorAll("tr").forEach((tr) => {
    const cells = [];
    tr.querySelectorAll("th, td").forEach((td) => {
      let text = td.textContent.replace(/"/g, '""');
      cells.push('"' + text + '"');
    });
    rows.push(cells.join(","));
  });
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  triggerDownload(blob, "table-data.csv");
}

function downloadPng(img) {
  if (!img || !img.src) return;
  const a = document.createElement("a");
  a.href = img.src;
  a.download = "chart.png";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function initDownloadHandlers(container) {
  container.addEventListener("click", (e) => {
    const csvBtn = e.target.closest(".btn-download-csv");
    if (csvBtn) {
      const wrap = document.getElementById(csvBtn.dataset.tableId);
      if (wrap) downloadCsv(wrap);
      return;
    }
    const pngBtn = e.target.closest(".btn-download-png");
    if (pngBtn) {
      const img = document.getElementById(pngBtn.dataset.chartId);
      if (img) downloadPng(img);
    }
  });
}
