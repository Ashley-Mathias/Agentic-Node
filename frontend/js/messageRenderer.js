/**
 * Renders API response payloads into bot bubble HTML.
 */
import { escapeHtml } from "./utils.js";

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
    html += '<div class="bubble-table-wrap"><table><thead>' + thead + "</thead><tbody>" + tbody + "</tbody></table></div>";
  }

  if (data.chart_image) {
    html += '<div class="bubble-chart"><img src="data:image/png;base64,' + escapeHtml(data.chart_image) + '" alt="Chart" /></div>';
  }

  if (data.sql_query) {
    html += '<div class="bubble-sql"><span class="bubble-sql-label">Generated SQL</span>' + escapeHtml(data.sql_query) + "</div>";
  }

  return html || "<p>No response content.</p>";
}
