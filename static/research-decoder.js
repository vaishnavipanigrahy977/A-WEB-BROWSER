(() => {
  const form = document.getElementById("research-decoder-form");
  if (!form) return;

  const input = document.getElementById("research-abstract");
  const counter = document.getElementById("research-counter");
  const clear = document.getElementById("research-clear");
  const button = document.getElementById("research-decode-button");
  const loading = document.getElementById("research-loading");
  const loadingMessage = document.getElementById("research-loading-message");
  const maxLength = Number(input.maxLength);
  const messages = [
    "Reading your research abstract...",
    "Identifying study methodology...",
    "Analysing research findings...",
    "Explaining medical terminology...",
    "Preparing your decoded research..."
  ];
  let loadingTimer;
  let submitted = false;

  const updateCounter = () => {
    const text = input.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    counter.textContent = `${words.toLocaleString()} words · ${text.length.toLocaleString()} / ${maxLength.toLocaleString()} characters`;
    input.setCustomValidity(text.trim() ? "" : "Paste a research abstract before decoding.");
  };

  input.addEventListener("input", updateCounter);
  clear.addEventListener("click", () => {
    input.value = "";
    updateCounter();
    input.focus();
  });
  form.addEventListener("submit", (event) => {
    updateCounter();
    if (!form.reportValidity()) {
      event.preventDefault();
      return;
    }
    if (submitted) {
      event.preventDefault();
      return;
    }
    submitted = true;
    button.disabled = true;
    button.textContent = "Decoding...";
    loading.hidden = false;
    let index = 0;
    loadingTimer = window.setInterval(() => {
      index = (index + 1) % messages.length;
      loadingMessage.textContent = messages[index];
    }, 1700);
  });
  document.querySelectorAll(".research-followup-form").forEach((followup) => {
    let followupSubmitted = false;
    followup.addEventListener("submit", (event) => {
      if (!followup.reportValidity()) {
        event.preventDefault();
        return;
      }
      if (followupSubmitted) {
        event.preventDefault();
        return;
      }
      followupSubmitted = true;
      const followupButton = followup.querySelector('button[type="submit"]');
      followupButton.disabled = true;
      followupButton.textContent = "Sending...";
    });
  });
  window.addEventListener("pagehide", () => window.clearInterval(loadingTimer));
  updateCounter();
})();
