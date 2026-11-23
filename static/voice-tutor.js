(() => {
  const readButton = document.querySelector("#voice-read");
  const stopButton = document.querySelector("#voice-stop");
  const status = document.querySelector("#voice-status");
  if (!readButton || !stopButton || !status) return;

  const speechSynthesis = window.speechSynthesis;
  const voiceLanguage = navigator.language || "en-US";
  if (!speechSynthesis || !window.SpeechSynthesisUtterance) {
    readButton.disabled = true;
    stopButton.disabled = true;
    status.textContent = "Spoken answers are not supported in this browser.";
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
      status.textContent = "Ask a question first, then your answer can be read aloud.";
      return;
    }
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = voiceLanguage;
    utterance.onstart = () => { status.textContent = "Reading the answer aloud."; };
    utterance.onend = () => { status.textContent = "Finished reading the answer."; };
    utterance.onerror = () => { status.textContent = "Audio playback stopped or is unavailable."; };
    speechSynthesis.speak(utterance);
  });

  stopButton.addEventListener("click", () => {
    speechSynthesis.cancel();
    status.textContent = "Audio stopped.";
  });
})();
