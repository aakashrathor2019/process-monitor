const AUTO_INTERVAL_MS = 10000; // 10s
let autoTimer = null;
let currentData = null;

const $ = (q) => document.querySelector(q);

async function getHosts() {
  const res = await fetch('/api/v1/hosts');
  const data = await res.json();
  return data.hosts || [];
}

async function getLatest(hostname) {
  const res = await fetch('/api/v1/snapshots/latest?hostname=' + encodeURIComponent(hostname));
  if (!res.ok) throw new Error('Failed: ' + res.status);
  return await res.json();
}

function fmtMB(bytes) {
  return (bytes/1024/1024).toFixed(1) + " MB";
}
function cpuClass(cpu) {
  if (cpu >= 30) return "high";
  if (cpu >= 5) return "mid";
  return "good";
}

function rowLabel(p) {
  return `
    <span class="name">${p.name}</span>
    <span class="pid">(PID ${p.pid}${p.ppid !== undefined ? `, PPID ${p.ppid}` : ""})</span>
    <span class="chips">
      <span class="chip cpu ${cpuClass(p.cpu_percent)}">CPU ${p.cpu_percent.toFixed(1)}%</span>
      <span class="chip mem">RSS ${fmtMB(p.mem_rss)}</span>
    </span>
  `;
}

function renderNode(p) {
  if (p.children && p.children.length) {
    const det = document.createElement('details');
    const sum = document.createElement('summary');
    sum.innerHTML = rowLabel(p);
    det.appendChild(sum);
    const ul = document.createElement('ul');
    p.children.forEach(c => {
      const li = document.createElement('li');
      li.appendChild(renderNode(c));
      ul.appendChild(li);
    });
    det.appendChild(ul);
    return det;
  } else {
    const span = document.createElement('div');
    span.className = "proc-leaf";
    span.innerHTML = rowLabel(p);
    return span;
  }
}

function renderTree(data, filter = "") {
  const tree = $("#tree");
  const empty = $("#empty");
  const stamp = $("#stamp");
  const count = $("#count");

  if (!data || !data.process_tree || !data.process_tree.length) {
    tree.innerHTML = "";
    empty.style.display = "block";
    stamp.textContent = "";
    count.textContent = "";
    return;
  }
  empty.style.display = "none";
  stamp.textContent = `Host: ${data.hostname} • Collected at: ${data.collected_at}`;

  // Filter (name or PID)
  let filteredRoots = data.process_tree;
  if (filter) {
    const q = filter.toLowerCase();
    const match = (n) => (n.name?.toLowerCase().includes(q) || String(n.pid).includes(q));
    const walk = (n) => {
      const kids = (n.children || []).map(walk).filter(Boolean);
      if (match(n) || kids.length) {
        return { ...n, children: kids };
      }
      return null;
    };
    filteredRoots = data.process_tree.map(walk).filter(Boolean);
  }

  const container = document.createElement('ul');
  let visibleCount = 0;
  filteredRoots.forEach(p => {
    const li = document.createElement('li');
    li.appendChild(renderNode(p));
    container.appendChild(li);
    const tally = (n) => 1 + (n.children||[]).reduce((a,c)=>a+tally(c),0);
    visibleCount += tally(p);
  });

  tree.innerHTML = "";
  tree.appendChild(container);
  count.textContent = `${visibleCount.toLocaleString()} processes`;

  currentData = data;
}

async function loadLatest() {
  const hostSel = $("#host");
  const tree = $("#tree");
  tree.innerHTML = `<div class="muted">Loading…</div>`;
  try {
    const data = await getLatest(hostSel.value);
    renderTree(data, $("#search").value.trim());
  } catch (e) {
    $("#empty").style.display = "block";
    $("#empty").textContent = e.message;
    $("#stamp").textContent = "";
  }
}

async function hydrate() {
  const hosts = await getHosts();
  const hostSel = $("#host");

  hostSel.innerHTML = hosts.map(h => `<option>${h}</option>`).join('');
  if (!hosts.length) {
    $("#empty").style.display = "block";
    $("#empty").textContent = "No hosts yet. Run the agent to ingest a snapshot.";
    return;
  }
  if (!hostSel.value) hostSel.value = hosts[0];

  await loadLatest();

  // Bind controls
  $("#refresh").onclick = loadLatest;
  $("#expandAll").onclick = () => document.querySelectorAll("#tree details").forEach(d => d.open = true);
  $("#collapseAll").onclick = () => document.querySelectorAll("#tree details").forEach(d => d.open = false);
  $("#search").addEventListener("input", (e) => {
    if (currentData) renderTree(currentData, e.target.value.trim());
  });

  const auto = $("#autorefresh");
  auto.onchange = () => {
    if (auto.checked) {
      autoTimer = setInterval(loadLatest, AUTO_INTERVAL_MS);
    } else {
      if (autoTimer) clearInterval(autoTimer);
      autoTimer = null;
    }
  };
}

hydrate();
