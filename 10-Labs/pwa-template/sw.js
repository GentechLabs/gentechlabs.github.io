/* GenTech PWA Template — Service Worker
   Cache-first for the static shell, network-first for <surface>-state.json.
   Proven pattern: steward-dashboard PWA. */
const CACHE = "{SURFACE}-v1";
const CORE = [
  "/{SURFACE_PATH}/index.html",
  "/{SURFACE_PATH}/manifest.json",
  "/{SURFACE_PATH}/{SURFACE}-state.json"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for the state file (always fresh), cache-first for the shell.
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.includes("-state.json")) {
    e.respondWith(
      fetch(e.request).then((r) => {
        const copy = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return r;
      }).catch(() => caches.match(e.request))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
