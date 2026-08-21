/* 정처기 학습 앱 — 오프라인 지원 서비스 워커
   교재/모의고사를 캐시해 두어 지하철·비행기에서도 열립니다.
   가져오는 방식은 '네트워크 우선' 이다 — 인터넷이 되면 늘 최신 파일을 받아오고,
   인터넷이 없을 때만 저장해 둔 것을 쓴다. 그래서 내용 갱신에 판 올리기가 꼭 필요하지는 않다.
   VERSION 은 캐시 이름이자 화면에 보여 줄 판 번호로 쓴다(옛 캐시 청소 + 갱신 확인용). */
const VERSION = 'jcg-v9';
const ASSETS = [
  './',
  './index.html',
  './exam.html',
  './textbook.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

// 설치 : 핵심 파일을 미리 담아 둔다
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION)
      .then((c) => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
      .catch(() => {})   // 일부 파일이 없어도 설치는 계속
  );
});

// 활성화 : 옛 판 캐시를 지운다
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 요청 : 네트워크를 먼저 시도하고(최신 우선), 실패하면 캐시로 답한다
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 폰트 등 외부 자원은 건드리지 않음

  e.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('./index.html')))
  );
});
