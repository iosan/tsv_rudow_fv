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
        if (!list || !Array.isArray(results)) {
            return;
        }

        if (results.length === 0) {
            list.innerHTML = "<li><strong>Keine aktuellen Ergebnisse</strong>: Der aktuelle Datenfeed liefert derzeit keine vergangenen Spiele.</li>";
            return;
        }

        function formatScore(entry) {
            if (!entry || !entry.scoreAvailable) {
                return "Ergebnis: offen";
            }

            if (typeof entry.score === "string" && entry.score.trim() !== "") {
                return "Ergebnis: " + entry.score;
            }

            if (entry.score && typeof entry.score === "object") {
                var home = entry.score.home;
                var away = entry.score.away;
                if (home !== undefined && home !== null && away !== undefined && away !== null) {
                    return "Ergebnis: " + String(home) + " : " + String(away);
                }
            }

            return "Ergebnis: offen";
        }

        function resultBadge(entry) {
            if (!entry || !entry.scoreAvailable) {
                return "";
            }

            if (entry.resultState === "official") {
                return " <span class=\"result-badge result-badge-official\">offiziell</span>";
            }

            return " <span class=\"result-badge result-badge-provisional\">vorlaeufig</span>";
        }

        list.innerHTML = results.map(function (entry) {
            var homeTeam = text(entry.homeTeam, "Heimteam offen");
            var awayTeam = text(entry.awayTeam, "Auswaertsteam offen");
            var fixture = escapeHtml(homeTeam) + " vs. " + escapeHtml(awayTeam);
            var info = escapeHtml(text(entry.dateLabel, "Datum offen")) + " · " + fixture;
            var scoreInfo = escapeHtml(formatScore(entry));
            var badge = resultBadge(entry);
            var link = entry.matchUrl
                ? " <a href=\"" + escapeHtml(entry.matchUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Spieldetails</a>"
                : "";
            return "<li><strong>" + escapeHtml(text(entry.team, "TSV Rudow")) + "</strong>: " + info + " · " + scoreInfo + badge + link + "</li>";
        }).join("");
    }

    function renderUpcomingMatches(matches) {
        var tbody = document.getElementById("live-upcoming-body");
        if (!tbody || !Array.isArray(matches) || matches.length === 0) {
            return;
        }

        tbody.innerHTML = matches.map(function (match) {
            var homeTeam = text(match.homeTeam, "");
            var awayTeam = text(match.awayTeam, "");
            var meeting;

            if (homeTeam && awayTeam) {
                meeting = escapeHtml(homeTeam) + " vs. " + escapeHtml(awayTeam);
            } else if (text(match.location, "") === "Heim") {
                meeting = escapeHtml(text(match.team, "TSV Rudow")) + " vs. " + escapeHtml(text(match.opponent, "Gegner offen"));
            } else {
                meeting = escapeHtml(text(match.opponent, "Gegner offen")) + " vs. " + escapeHtml(text(match.team, "TSV Rudow"));
            }

            return [
                "<tr>",
                "<td>" + escapeHtml(text(match.dateLabel, "Datum offen")) + "</td>",
                "<td>" + escapeHtml(text(match.team, "TSV Rudow")) + "</td>",
                "<td>" + meeting + "</td>",
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
                "</article>"
            ].join("");
        }).join("");
    }

    function renderStandingsCards(teams) {
        var container = document.getElementById("live-standings-cards");
        if (!container || !Array.isArray(teams) || teams.length === 0) {
            return;
        }

        function renderTeamMark(row, fallbackName) {
            var teamName = text(row && row.team, fallbackName || "TSV Rudow");
            var logoUrl = row && row.logoUrl ? String(row.logoUrl) : "";

            if (!logoUrl) {
                return "<span class=\"standings-team-fallback\" title=\"" + escapeHtml(teamName) + "\">" + escapeHtml(teamName) + "</span>";
            }

            return "<img class=\"standings-team-logo\" src=\"" + escapeHtml(logoUrl) + "\" alt=\"\" title=\"" + escapeHtml(teamName) + "\" loading=\"lazy\">";
        }

        container.innerHTML = teams.map(function (team) {
            var standing = team.standing || {};
            var tableRows = Array.isArray(team.tableRows) ? team.tableRows : [];
            var bodyHtml;

            if (tableRows.length > 0) {
                bodyHtml = tableRows.map(function (row) {
                    return [
                        "<tr>",
                        "<td>" + escapeHtml(text(row.rank, "-")) + "</td>",
                        "<td class=\"standings-team-cell\">" + renderTeamMark(row, team.name) + "</td>",
                        "<td>" + escapeHtml(text(row.played, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.won, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.draw, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.lost, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.goals, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.goalDiff, "-")) + "</td>",
                        "<td>" + escapeHtml(text(row.points, "-")) + "</td>",
                        "</tr>"
                    ].join("");
                }).join("");
            } else {
                bodyHtml = [
                    "<tr>",
                    "<td>" + escapeHtml(text(standing.rank, "-")) + "</td>",
                    "<td class=\"standings-team-cell\">" + renderTeamMark({ team: team.name, logoUrl: team.logoUrl }, team.name) + "</td>",
                    "<td>" + escapeHtml(text(standing.played, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.won, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.draw, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.lost, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.goals, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.goalDiff, "-")) + "</td>",
                    "<td>" + escapeHtml(text(standing.points, "-")) + "</td>",
                    "</tr>"
                ].join("");
            }

            return [
                "<article class=\"update-card\">",
                "<h3>" + escapeHtml(text(team.name, "TSV Rudow")) + "</h3>",
                "<div class=\"table-scroll\">",
                "<table class=\"data-table standings-table\">",
                "<thead><tr><th>Pl.</th><th>Team</th><th>Sp.</th><th>G</th><th>U</th><th>V</th><th>Tore</th><th>Diff.</th><th>Pkt.</th></tr></thead>",
                "<tbody>" + bodyHtml + "</tbody>",
                "</table>",
                "</div>",
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
        renderStandingsCards(payload.teams);
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
