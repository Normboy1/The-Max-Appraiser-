document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("appraise-form");
  const resultSection = document.getElementById("result");
  const scoresDiv = document.getElementById("scores");
  const overallP = document.getElementById("overall");
  const valuationP = document.getElementById("valuation");
  const explanationP = document.getElementById("explanation");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultSection.classList.add("hidden");

    const payload = {
      idea: document.getElementById("idea").value.trim(),
      plan: document.getElementById("plan").value.trim(),
      roadmap: document.getElementById("roadmap").value.trim(),
      currency: document.getElementById("currency").value,
    };


    try {
      const res = await fetch("/evaluate/idea", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      renderResult(data);
    } catch (err) {
      alert("Error: " + err);
    }
  });

  function renderResult(data) {
    scoresDiv.innerHTML = "";
    [
      ["Originality", data.originality],
      ["Functional Value", data.functional_value],
      ["Scalability", data.scalability],
      ["Competition", data.competition],
    ].forEach(([label, score]) => {
      const wrapper = document.createElement("div");
      wrapper.className = "score-wrapper";
      const text = document.createElement("div");
      text.textContent = `${label}: ${(score * 100).toFixed(0)}%`;
      const bar = document.createElement("div");
      bar.className = "score-bar";
      bar.style.width = `${score * 100}%`;
      wrapper.appendChild(text);
      wrapper.appendChild(bar);
      scoresDiv.appendChild(wrapper);
    });
    overallP.textContent = `Overall Grade: ${data.grade} (${(data.overall_score * 100).toFixed(1)}%)`;
    valuationP.textContent = `Estimated Valuation: ${data.valuation.amount.toLocaleString()} ${data.valuation.currency}`;
    explanationP.textContent = data.explanation;

    resultSection.classList.remove("hidden");
    resultSection.scrollIntoView({ behavior: "smooth" });
  }

  // Add answered class animation
  document.querySelectorAll("textarea").forEach((ta) => {
    ta.addEventListener("input", () => {
      const filled = ta.value.trim().length > 0;
      ta.classList.toggle("answered", filled);
      if (filled) {
        const current = ta.closest('.question');
        const next = current && current.nextElementSibling;
        if (next && next.classList.contains('question') && !next.classList.contains('active')) {
          next.classList.add('active');
        }
        // enable submit after roadmap filled
        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = document.getElementById('roadmap').value.trim().length === 0;
      }
    });
  });
});
