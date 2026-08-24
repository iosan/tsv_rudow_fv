(function () {
    "use strict";

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function text(value, fallback) {
        if (value === null || value === undefined || value === "") {
            return fallback;
        }
        return String(value);
    }

    function renderTableRows(rows) {
        var tbody = document.getElementById("live-table-body");
        if (!tbody || !Array.isArray(rows) || rows.length === 0) {
            return;
        }

        tbody.innerHTML = rows.map(function (row) {
            return [
                "<tr>",
                "<td>" + escapeHtml(text(row.team, "-")) + "</td>",
                "<td>" + escapeHtml(text(row.rank, "-")) + "</td>",
                "<td>" + escapeHtml(text(row.played, "-")) + "</td>",
                "<td>" + escapeHtml(text(row.points, "-")) + "</td>",
                "</tr>"
            ].join("");
        }).join("");
    }

    function renderRecentResults(results) {
        var list = document.getElementById("live-results-list");
        if (!list || !Array.isArray(results) || results.length === 0) {
            return;
        }

        list.innerHTML = results.map(function (entry) {
            var info = escapeHtml(text(entry.dateLabel, "Datum offen")) + " · gegen " + escapeHtml(text(entry.opponent, "Gegner offen"));
            var link = entry.matchUrl
                ? " <a href=\"" + escapeHtml(entry.matchUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Spieldetails</a>"
                : "";
            return "<li><strong>" + escapeHtml(text(entry.team, "TSV Rudow")) + "</strong>: " + info + " (Ergebnis extern)" + link + "</li>";
        }).join("");
    }

    function renderUpcomingMatches(matches) {
        var tbody = document.getElementById("live-upcoming-body");
        if (!tbody || !Array.isArray(matches) || matches.length === 0) {
            return;
        }

        tbody.innerHTML = matches.map(function (match) {
            var meeting = escapeHtml(text(match.team, "TSV Rudow")) + " vs. " + escapeHtml(text(match.opponent, "Gegner offen"));
            var location = escapeHtml(text(match.location, "-"));
            var linkCell = match.matchUrl
                ? "<a href=\"" + escapeHtml(match.matchUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Link</a>"
                : "-";

            return [
                "<tr>",
                "<td>" + escapeHtml(text(match.dateLabel, "Datum offen")) + "</td>",
                "<td>" + escapeHtml(text(match.team, "TSV Rudow")) + "</td>",
                "<td>" + meeting + "</td>",
                "<td>" + location + "</td>",
                "<td>" + linkCell + "</td>",
                "</tr>"
            ].join("");
        }).join("");
    }

    function renderTeamCards(teams) {
        var container = document.getElementById("live-team-cards");
        if (!container || !Array.isArray(teams) || teams.length === 0) {
            return;
        }

        container.innerHTML = teams.map(function (team) {
            var standing = team.standing || {};
            var nextMatch = team.nextMatch || {};
            var tableUrl = team.tableUrl
                ? "<p><a href=\"" + escapeHtml(team.tableUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Offizielle Tabelle</a></p>"
                : "";
            var nextMatchLink = nextMatch.matchUrl
                ? "<a href=\"" + escapeHtml(nextMatch.matchUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Spieldetails</a>"
                : "";

            return [
                "<article class=\"update-card\">",
                "<h3>" + escapeHtml(text(team.name, "TSV Rudow")) + "</h3>",
                "<p><strong>Platz:</strong> " + escapeHtml(text(standing.rank, "-")) +
                    " | <strong>Spiele:</strong> " + escapeHtml(text(standing.played, "-")) +
                    " | <strong>Punkte:</strong> " + escapeHtml(text(standing.points, "-")) + "</p>",
                "<p><strong>Naechstes Spiel:</strong> " + escapeHtml(text(nextMatch.dateLabel, "Datum offen")) +
                    " · gegen " + escapeHtml(text(nextMatch.opponent, "Gegner offen")) + " (" +
                    escapeHtml(text(nextMatch.location, "offen")) + ") " + nextMatchLink + "</p>",
                tableUrl,
                "</article>"
            ].join("");
        }).join("");
    }

    function renderStatus(data) {
        var status = document.getElementById("live-data-status");
        if (!status) {
            return;
        }

        var generatedAt = data && data.generatedAt ? new Date(data.generatedAt) : null;
        if (!generatedAt || Number.isNaN(generatedAt.getTime())) {
            status.textContent = "Automatische Daten aktiv.";
            return;
        }

        status.textContent = "Automatische Daten aktiv. Letzte Aktualisierung: " + generatedAt.toLocaleString("de-DE");
    }

    function renderFromPayload(payload) {
        if (!payload || !payload.homepage) {
            return false;
        }

        renderTableRows(payload.homepage.tableRows);
        renderRecentResults(payload.homepage.recentResults);
        renderUpcomingMatches(payload.homepage.upcomingMatches);
        renderTeamCards(payload.teams);
        renderStatus(payload);
        return true;
    }

    function setOfflineStatus() {
        var status = document.getElementById("live-data-status");
        if (!status) {
            return;
        }
        status.textContent = "Live-Daten konnten nicht geladen werden (Datei-Modus oder Netzwerkblockade).";
    }

    function loadLiveData() {
        if (renderFromPayload(window.__LEAGUE_DATA__)) {
            return;
        }

        fetch("data/league-data.json", { cache: "no-store" })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Fetch failed: " + response.status);
                }
                return response.json();
            })
            .then(function (payload) {
                renderFromPayload(payload);
            })
            .catch(function () {
                if (!renderFromPayload(window.__LEAGUE_DATA__)) {
                    // Keep static fallback content when live feed is unavailable.
                    setOfflineStatus();
                }
            });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", loadLiveData);
    } else {
        loadLiveData();
    }
})();
