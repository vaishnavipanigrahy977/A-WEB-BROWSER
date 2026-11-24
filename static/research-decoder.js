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
  document.querySelectorAll(".research-download").forEach((downloadForm) => {
    let downloadSubmitted = false;
    const downloadButton = downloadForm.querySelector('button[type="submit"]');
    const downloadStatus = downloadForm.querySelector(".research-download-status");
    downloadForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (downloadSubmitted) return;
      downloadSubmitted = true;
      downloadButton.disabled = true;
      downloadButton.textContent = "Preparing PDF...";
      downloadStatus.hidden = false;
      downloadStatus.textContent = "Preparing your decoded research PDF...";
      try {
        const response = await fetch(downloadForm.getAttribute("action"), {
          method: "POST",
          body: new URLSearchParams(new FormData(downloadForm)),
          headers: { Accept: "application/pdf" }
        });
        if (!response.ok) {
          downloadStatus.textContent = `PDF download failed (HTTP ${response.status}). Please try again.`;
          return;
        }
        const contentType = response.headers.get("Content-Type") || "";
        if (!contentType.toLowerCase().includes("application/pdf")) {
          downloadStatus.textContent = "WellNote did not return a PDF. Please try again.";
          return;
        }
        const blob = await response.blob();
        if (!blob.size) {
          downloadStatus.textContent = "The generated PDF was empty. Please try again.";
          return;
        }
        const disposition = response.headers.get("Content-Disposition") || "";
        const filenameMatch = disposition.match(/filename="([^"]+)"/i);
        const filename = filenameMatch
          ? filenameMatch[1]
          : "Wellnote_Research_Decoder.pdf";
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = filename;
        link.hidden = true;
        document.body.append(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
        downloadStatus.textContent = "Your PDF download has started. Check your browser downloads.";
      } catch (_error) {
        downloadStatus.textContent = "Could not reach WellNote to create the PDF. Check your connection and try again.";
      } finally {
        downloadSubmitted = false;
        downloadButton.disabled = false;
        downloadButton.textContent = "Download Decoded PDF";
      }
    });
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
