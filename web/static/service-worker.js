/* O.M.N.I.S — Service Worker (PWA)
 * Estrategia:
 *   - Recursos estáticos (shell): cache-first para carga rápida y uso offline.
 *   - API y streams (/api/): siempre red (network-only), nunca se cachean
 *     para no servir resultados de inteligencia obsoletos.
 */
const CACHE = "omnis-v1";
const SHELL = [
  "/",
  "/static/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((claves) =>
      Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // Nunca cachear la API ni los streams SSE — siempre datos frescos.
  if (url.pathname.startsWith("/api/")) {
    return; // deja pasar la petición a la red normalmente
  }

  // Recursos estáticos y shell: cache-first con actualización en segundo plano.
  e.respondWith(
    caches.match(e.request).then((cacheada) => {
      const red = fetch(e.request)
        .then((resp) => {
          if (resp && resp.status === 200 && e.request.method === "GET") {
            const copia = resp.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copia)).catch(() => {});
          }
          return resp;
        })
        .catch(() => cacheada);
      return cacheada || red;
    })
  );
});
