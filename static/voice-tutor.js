(() => {
  const readButton = document.querySelector("#voice-read");
  const stopButton = document.querySelector("#voice-stop");
  const status = document.querySelector("#voice-status");
  if (!readButton || !stopButton || !status) return;

  const speechSynthesis = window.speechSynthesis;
  const pageLanguage = document.documentElement.lang;
  const voiceLanguage = pageLanguage === "hi" || pageLanguage === "hi-Latn"
    ? "hi-IN"
    : pageLanguage || navigator.language || "en-US";
  if (!speechSynthesis || !window.SpeechSynthesisUtterance) {
    readButton.disabled = true;
    stopButton.disabled = true;
    status.textContent = document.body.dataset.voiceUnsupported;
    return;
  }

  const answerText = () => {
    const reply = document.querySelector(".chat-bubble.reply");
    const greeting = document.querySelector(".tutor-card > .chat-bubble");
    return (reply || greeting)?.innerText.replace(/^Study buddy\s*/i, "").trim() || "";
  };

  readButton.addEventListener("click", () => {
    const text = answerText();
    if (!text) {
      status.textContent = document.body.dataset.voiceAskFirst;
      return;
    }
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = voiceLanguage;
    utterance.onstart = () => { status.textContent = document.body.dataset.voiceReading; };
    utterance.onend = () => { status.textContent = document.body.dataset.voiceFinished; };
    utterance.onerror = () => { status.textContent = document.body.dataset.voiceError; };
    speechSynthesis.speak(utterance);
  });

  stopButton.addEventListener("click", () => {
    speechSynthesis.cancel();
    status.textContent = document.body.dataset.voiceStopped;
  });
})();
