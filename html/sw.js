var CACHE_NAME = "tsv-rudow-image-cache-v1";
var LOGO_PATH_FRAGMENT = "/export.media/-/action/getLogo/";

self.addEventListener("install", function (event) {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", function (event) {
    event.waitUntil(self.clients.claim());
});

function shouldCacheImage(requestUrl, request) {
    if (request.method !== "GET" || request.destination !== "image") {
        return false;
    }

    if (requestUrl.origin === self.location.origin) {
        return true;
    }

    return requestUrl.hostname === "www.fussball.de" && requestUrl.pathname.indexOf(LOGO_PATH_FRAGMENT) !== -1;
}

async function cacheFirstImage(request) {
    var cache = await caches.open(CACHE_NAME);
    var cached = await cache.match(request, { ignoreVary: true, ignoreSearch: false });

    if (cached) {
        return cached;
    }

    var response = await fetch(request);
    if (response && (response.ok || response.type === "opaque")) {
        cache.put(request, response.clone());
    }

    return response;
}

async function networkThenCacheImage(request) {
    var cache = await caches.open(CACHE_NAME);

    try {
        var response = await fetch(request);
        if (response && (response.ok || response.type === "opaque")) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        var cached = await cache.match(request, { ignoreVary: true, ignoreSearch: false });
        if (cached) {
            return cached;
        }
        throw error;
    }
}

self.addEventListener("fetch", function (event) {
    var request = event.request;
    var requestUrl = new URL(request.url);

    if (!shouldCacheImage(requestUrl, request)) {
        return;
    }

    if (requestUrl.hostname === "www.fussball.de" && requestUrl.pathname.indexOf(LOGO_PATH_FRAGMENT) !== -1) {
        event.respondWith(cacheFirstImage(request));
        return;
    }

    event.respondWith(networkThenCacheImage(request));
});
