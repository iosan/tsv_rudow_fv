(function () {
    "use strict";

    var separatorId = "site-header-separator";
    var tickerId = "site-news-ticker";
    var tickerAnimationFrame = null;
    var tickerLastTimestamp = 0;
    var tickerOffset = 0;
    var tickerSpeedPxPerSecond = 38;

    function getHeaderAnchorParent() {
        var header = document.querySelector("header");
        if (header && header.parentNode) {
            return {
                parent: header.parentNode,
                anchor: header
            };
        }

        var topNav = document.querySelector(".top-nav");
        if (topNav && topNav.parentNode) {
            return {
                parent: topNav.parentNode,
                anchor: topNav
            };
        }

        return null;
    }

    function createHeaderSeparator() {
        if (document.getElementById(separatorId)) {
            return document.getElementById(separatorId);
        }

        var anchorPoint = getHeaderAnchorParent();
        var separator;

        if (!anchorPoint) {
            return null;
        }

        separator = document.createElement("div");
        separator.id = separatorId;
        separator.className = "header-separator";
        separator.setAttribute("aria-hidden", "true");

        if (anchorPoint.anchor.nextSibling) {
            anchorPoint.parent.insertBefore(separator, anchorPoint.anchor.nextSibling);
        } else {
            anchorPoint.parent.appendChild(separator);
        }

        return separator;
    }

    function createTickerElement() {
        if (document.getElementById(tickerId)) {
            return document.getElementById(tickerId);
        }

        var anchorPoint = getHeaderAnchorParent();
        var separator = createHeaderSeparator();
        var ticker;
        var label;
        var viewport;
        var track;

        if (!anchorPoint) {
            return null;
        }

        ticker = document.createElement("aside");
        ticker.id = tickerId;
        ticker.className = "news-ticker";
        ticker.setAttribute("aria-label", "Aktuelles-Ticker");

        label = document.createElement("span");
        label.className = "news-ticker-label";
        label.textContent = "Aktuelles";

        viewport = document.createElement("div");
        viewport.className = "news-ticker-viewport";

        track = document.createElement("ul");
        track.className = "news-ticker-track";
        track.setAttribute("aria-live", "off");

        viewport.appendChild(track);
        ticker.appendChild(label);
        ticker.appendChild(viewport);

        if (separator && separator.parentNode) {
            if (separator.nextSibling) {
                separator.parentNode.insertBefore(ticker, separator.nextSibling);
            } else {
                separator.parentNode.appendChild(ticker);
            }
        } else if (anchorPoint.anchor.nextSibling) {
            anchorPoint.parent.insertBefore(ticker, anchorPoint.anchor.nextSibling);
        } else {
            anchorPoint.parent.appendChild(ticker);
        }

        return ticker;
    }

    function createTickerEntry(textValue) {
        var li = document.createElement("li");
        var link = document.createElement("a");

        link.href = "aktuelles.html";
        link.textContent = textValue;
        link.setAttribute("aria-label", textValue);

        li.appendChild(link);
        return li;
    }

    function buildTickerItemsFromPayload(payload) {
        var items = [];
        var homepage = payload && payload.homepage;
        var recentResults = homepage && Array.isArray(homepage.recentResults) ? homepage.recentResults : [];
        var upcomingMatches = homepage && Array.isArray(homepage.upcomingMatches) ? homepage.upcomingMatches : [];

        function formatResultLabel(entry) {
            if (!entry || !entry.scoreAvailable) {
                return "offen";
            }

            var scoreText = (typeof entry.score === "string" && entry.score.trim() !== "")
                ? entry.score
                : "offen";
            return scoreText;
        }

        recentResults.slice(0, 3).forEach(function (entry) {
            var homeTeam = String(entry.homeTeam || "Heimteam offen");
            var awayTeam = String(entry.awayTeam || "Auswaertsteam offen");
            items.push({
                text: "Ergebnis: " + homeTeam + " vs. " + awayTeam +
                    " - " + formatResultLabel(entry),
                href: entry.matchUrl || "aktuelles.html"
            });
        });

        upcomingMatches.slice(0, 3).forEach(function (entry) {
            items.push({
                text: "Vorschau: " + String(entry.team || "TSV Rudow") + " spielt am " + String(entry.dateLabel || "Termin offen") + " gegen " + String(entry.opponent || "Gegner offen"),
                href: entry.matchUrl || "aktuelles.html"
            });
        });

        if (items.length === 0) {
            items.push({ text: "Aktuelle News, Termine und Team-Updates im Bereich Aktuelles.", href: "aktuelles.html" });
            items.push({ text: "Foerderverein und Spielbetrieb: Alles Wichtige auf einen Blick.", href: "aktuelles.html" });
            items.push({ text: "Tabellenstand, Ergebnisse und kommende Spieltage jetzt ansehen.", href: "aktuelles.html" });
        }

        return items;
    }

    function renderTicker(items) {
        var ticker = createTickerElement();
        var track;
        var minimumItems = 6;

        if (!ticker) {
            return;
        }

        track = ticker.querySelector(".news-ticker-track");
        if (!track) {
            return;
        }

        track.innerHTML = "";
        ticker.classList.remove("is-ready");

        items.forEach(function (item) {
            track.appendChild(createTickerEntry(item.text));
        });

        while (track.children.length < minimumItems) {
            items.forEach(function (item) {
                if (track.children.length < minimumItems) {
                    track.appendChild(createTickerEntry(item.text));
                }
            });
        }

        Array.prototype.slice.call(track.children).forEach(function (node) {
            track.appendChild(node.cloneNode(true));
        });

        ticker.classList.add("is-ready");
        startTickerMotion(ticker, track);
    }

    function stopTickerMotion() {
        if (tickerAnimationFrame !== null) {
            window.cancelAnimationFrame(tickerAnimationFrame);
            tickerAnimationFrame = null;
        }
        tickerLastTimestamp = 0;
    }

    function startTickerMotion(ticker, track) {
        var viewport = ticker.querySelector(".news-ticker-viewport");

        if (!viewport || !track) {
            return;
        }

        stopTickerMotion();
        tickerOffset = 0;

        function step(timestamp) {
            var contentWidth;
            var deltaSeconds;

            if (!ticker.isConnected) {
                stopTickerMotion();
                return;
            }

            if (tickerLastTimestamp === 0) {
                tickerLastTimestamp = timestamp;
            }

            deltaSeconds = (timestamp - tickerLastTimestamp) / 1000;
            tickerLastTimestamp = timestamp;
            tickerOffset += tickerSpeedPxPerSecond * deltaSeconds;

            contentWidth = track.scrollWidth / 2;
            if (contentWidth <= 0) {
                tickerAnimationFrame = window.requestAnimationFrame(step);
                return;
            }

            if (tickerOffset >= contentWidth) {
                tickerOffset = tickerOffset % contentWidth;
            }

            track.style.transform = "translateX(" + (-tickerOffset) + "px)";
            tickerAnimationFrame = window.requestAnimationFrame(step);
        }

        tickerAnimationFrame = window.requestAnimationFrame(step);
    }

    function loadTicker() {
        if (window.__LEAGUE_DATA__) {
            renderTicker(buildTickerItemsFromPayload(window.__LEAGUE_DATA__));
            return;
        }

        fetch("data/league-data.json", { cache: "no-store" })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Ticker fetch failed: " + response.status);
                }
                return response.json();
            })
            .then(function (payload) {
                renderTicker(buildTickerItemsFromPayload(payload));
            })
            .catch(function () {
                renderTicker(buildTickerItemsFromPayload(null));
            });
    }

    createHeaderSeparator();
    createTickerElement();
    loadTicker();

    window.addEventListener("beforeunload", stopTickerMotion);
})();
