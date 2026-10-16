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
            var dateInfo = escapeHtml(text(entry.dateLabel, "Datum offen"));
            var scoreInfo = escapeHtml(formatScore(entry));
            var badge = resultBadge(entry);
            var link = entry.matchUrl
                ? " <a href=\"" + escapeHtml(entry.matchUrl) + "\" target=\"_blank\" rel=\"noopener noreferrer\">Spieldetails</a>"
                : "";
            return "<li><strong>" + escapeHtml(text(entry.team, "TSV Rudow")) + "</strong>: " + dateInfo + "<br>" + fixture + "<br>" + scoreInfo + badge + link + "</li>";
        }).join("");
    }

    function renderUpcomingMatches(matches, teams) {
        var tbody = document.getElementById("live-upcoming-body");
        if (!tbody || !Array.isArray(matches) || matches.length === 0) {
            return;
        }

        var logoByTeam = {};
        if (Array.isArray(teams)) {
            teams.forEach(function (team) {
                if (!team || !team.name) {
                    return;
                }

                if (Array.isArray(team.tableRows)) {
                    team.tableRows.forEach(function (row) {
                        if (row && row.team && row.logoUrl && !logoByTeam[row.team]) {
                            logoByTeam[row.team] = String(row.logoUrl);
                        }
                    });
                }

                if (!logoByTeam[team.name] && Array.isArray(team.tableRows)) {
                    for (var i = 0; i < team.tableRows.length; i += 1) {
                        var candidate = team.tableRows[i];
                        if (candidate && candidate.team === team.name && candidate.logoUrl) {
                            logoByTeam[team.name] = String(candidate.logoUrl);
                            break;
                        }
                    }
                }
            });
        }

        function teamMark(teamName) {
            var normalizedName = text(teamName, "TSV Rudow");
            var logoUrl = logoByTeam[normalizedName] || "";

            if (logoUrl) {
                return "<img class=\"upcoming-team-logo\" src=\"" + escapeHtml(logoUrl) + "\" alt=\"\" title=\"" + escapeHtml(normalizedName) + "\" loading=\"lazy\">";
            }

            return "<span class=\"upcoming-team-fallback\" title=\"" + escapeHtml(normalizedName) + "\">•</span>";
        }

        tbody.innerHTML = matches.map(function (match) {
            var homeTeam = text(match.homeTeam, "");
            var awayTeam = text(match.awayTeam, "");
            var meetingHome;
            var meetingAway;

            if (homeTeam && awayTeam) {
                meetingHome = homeTeam;
                meetingAway = awayTeam;
            } else if (text(match.location, "") === "Heim") {
                meetingHome = text(match.team, "TSV Rudow");
                meetingAway = text(match.opponent, "Gegner offen");
            } else {
                meetingHome = text(match.opponent, "Gegner offen");
                meetingAway = text(match.team, "TSV Rudow");
            }

            var meetingTitle = escapeHtml(meetingHome + " vs. " + meetingAway);
            var meeting = [
                "<span class=\"upcoming-fixture-mark\" title=\"" + meetingTitle + "\">",
                teamMark(meetingHome),
                "<span class=\"upcoming-vs\">vs.</span>",
                teamMark(meetingAway),
                "<span class=\"sr-only\">" + meetingTitle + "</span>",
                "</span>"
            ].join("");

            return [
                "<tr>",
                "<td>" + escapeHtml(text(match.dateLabel, "Datum offen")) + "</td>",
                "<td>" + escapeHtml(text(match.team, "TSV Rudow")) + "</td>",
                "<td><span class=\"upcoming-fixture\">" + meeting + "</span></td>",
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
                return "<span class=\"standings-team-mark\"><span class=\"standings-team-fallback\" title=\"" + escapeHtml(teamName) + "\">" + escapeHtml(teamName) + "</span></span>";
            }

            return [
                "<span class=\"standings-team-mark\">",
                "<img class=\"standings-team-logo\" src=\"" + escapeHtml(logoUrl) + "\" alt=\"\" title=\"" + escapeHtml(teamName) + "\" loading=\"lazy\">",
                "<span class=\"standings-team-name\">" + escapeHtml(teamName) + "</span>",
                "</span>"
            ].join("");
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
                "<thead><tr><th>Pl.</th><th>Team</th><th>Sp.</th><th>Diff.</th><th>Pkt.</th></tr></thead>",
                "<tbody>" + bodyHtml + "</tbody>",
                "</table>",
                "</div>",
                "</article>"
            ].join("");
        }).join("");
    }

    function renderStatus() {
        var status = document.getElementById("live-data-status");
        if (!status) {
            return;
        }
        status.textContent = "";
    }

    function renderFromPayload(payload) {
        if (!payload || !payload.homepage) {
            return false;
        }

        renderTableRows(payload.homepage.tableRows);
        renderRecentResults(payload.homepage.recentResults);
        renderUpcomingMatches(payload.homepage.upcomingMatches, payload.teams);
        renderStandingsCards(payload.teams);
        renderTeamCards(payload.teams);
        renderStatus();
        return true;
    }

    function isFreshPayload(payload, maxAgeMinutes) {
        if (!payload || !payload.generatedAt) {
            return false;
        }

        var generatedAt = new Date(payload.generatedAt);
        if (Number.isNaN(generatedAt.getTime())) {
            return false;
        }

        var ageMinutes = (Date.now() - generatedAt.getTime()) / 60000;
        return ageMinutes <= maxAgeMinutes;
    }

    function setOfflineStatus() {
        var status = document.getElementById("live-data-status");
        if (!status) {
            return;
        }
        status.textContent = "";
    }

    function loadLiveData() {
        var cachedPayload = window.__LEAGUE_DATA__;
        if (isFreshPayload(cachedPayload, 60)) {
            renderFromPayload(cachedPayload);
            return;
        }

        fetch("data/league-data.json?ts=" + Date.now(), { cache: "no-store" })
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
                if (!renderFromPayload(cachedPayload)) {
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
