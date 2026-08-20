
async function api(url, options={}) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
function setExperiment(obj) {
  document.getElementById("experiment").textContent = JSON.stringify(obj, null, 2);
}
async function load() {
  try {
    const caps = await api("/api/crypto/capabilities");
    document.getElementById("caps").textContent = JSON.stringify(caps, null, 2);
    document.getElementById("openssl").textContent = caps.openssl;

    const assets = await api("/api/inventory");
    document.getElementById("totalAssets").textContent = assets.length;
    const high = assets.filter(a => a.quantum_risk_score >= 70).length;
    const avgRisk = assets.reduce((s,a)=>s+a.quantum_risk_score,0)/assets.length;
    const avgReady = assets.reduce((s,a)=>s+a.readiness_score,0)/assets.length;
    document.getElementById("highRisk").textContent = high;
    document.getElementById("avgRisk").textContent = avgRisk.toFixed(1);
    document.getElementById("avgReady").textContent = avgReady.toFixed(1);

    const tbody = document.getElementById("inventory");
    tbody.innerHTML = "";
    assets.forEach(a => {
      const tr = document.createElement("tr");
      const riskClass = a.quantum_risk_score >= 70 ? "risk-high" :
                        a.quantum_risk_score >= 40 ? "risk-medium" : "risk-low";
      tr.innerHTML = `<td>${a.asset_name}</td><td>${a.zone}</td>
        <td>${a.current_algorithm}</td><td>${a.secrecy_years} yr</td>
        <td>${a.migration_months} mo</td><td>${a.criticality}</td>
        <td class="${riskClass}">${a.quantum_risk_score}</td>
        <td>${a.readiness_score}</td>`;
      tbody.appendChild(tr);
    });

    const bars = document.getElementById("riskBars");
    bars.innerHTML = "";
    [...assets].sort((a,b)=>b.quantum_risk_score-a.quantum_risk_score).forEach(a => {
      const row = document.createElement("div");
      row.className = "barrow";
      row.innerHTML = `<span>${a.asset_name}</span>
        <div class="bar"><div class="fill" style="width:${a.quantum_risk_score}%"></div></div>
        <b>${a.quantum_risk_score}</b>`;
      bars.appendChild(row);
    });
  } catch(e) {
    document.getElementById("experiment").textContent = e.message;
  }
}

document.querySelectorAll("[data-mode]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const mode = btn.dataset.mode;
    btn.disabled = true;
    try {
      const payload = {
        mode,
        message: {
          message_id: "OP-0001",
          message_type: "critical-operation",
          sender: "NODE-A",
          receiver: "NODE-B",
          amount: 125000,
          currency: "USD",
          timestamp: new Date().toISOString()
        }
      };
      const envelope = await api("/api/crypto/encrypt", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
      });
      const signed = await api("/api/crypto/sign", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({envelope})
      });
      const verified = await api("/api/crypto/verify", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({envelope:signed})
      });
      const plaintext = await api("/api/crypto/decrypt", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({envelope})
      });
      setExperiment({
        mode,
        signed_envelope_size_bytes: new Blob([JSON.stringify(signed)]).size,
        verification: verified,
        round_trip_plaintext: plaintext
      });
    } catch(e) {
      setExperiment({error:e.message});
    } finally { btn.disabled = false; }
  });
});

document.getElementById("benchmark").addEventListener("click", async () => {
  const button = document.getElementById("benchmark");
  button.disabled = true;
  try {
    setExperiment({status:"Running measured benchmark..."});
    const result = await api("/api/benchmark", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({iterations:3})
    });
    setExperiment(result);
  } catch(e) {
    setExperiment({error:e.message});
  } finally { button.disabled = false; }
});

load();
