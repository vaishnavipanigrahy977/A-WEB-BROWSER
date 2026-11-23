(() => {
  const form = document.querySelector(".prompt-form");
  const prompt = document.querySelector("#study-prompt");
  const listenButton = document.querySelector("#voice-listen");
  const readButton = document.querySelector("#voice-read");
  const stopButton = document.querySelector("#voice-stop");
  const status = document.querySelector("#voice-status");
  if (!form || !prompt || !listenButton || !readButton || !stopButton || !status) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const speechSynthesis = window.speechSynthesis;
  const voiceLanguage = navigator.language || "en-US";
  let recognition = null;
  let transcript = "";
  let recognitionFailed = false;
  let stoppingRecognition = false;

  const answerText = () => {
    const reply = document.querySelector(".chat-bubble.reply");
    const greeting = document.querySelector(".tutor-card > .chat-bubble");
    return (reply || greeting)?.innerText.replace(/^Study buddy\s*/i, "").trim() || "";
  };

  const speakAnswer = () => {
    if (!speechSynthesis) {
      status.textContent = "Spoken answers are not supported in this browser.";
      return;
    }
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
  };

  readButton.addEventListener("click", speakAnswer);
  stopButton.addEventListener("click", () => {
    if (speechSynthesis) speechSynthesis.cancel();
    if (recognition) {
      stoppingRecognition = true;
      recognition.abort();
    }
    status.textContent = "Voice stopped.";
  });

  if (!SpeechRecognition) {
    listenButton.disabled = true;
    status.textContent = "Voice input is not supported in this browser. You can type your question instead.";
  } else {
    try {
      recognition = new SpeechRecognition();
      recognition.lang = voiceLanguage;
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        transcript = "";
        recognitionFailed = false;
        stoppingRecognition = false;
        listenButton.disabled = true;
        status.textContent = "Listening… speak your question.";
      };
      recognition.onresult = (event) => {
        transcript = Array.from(event.results)
          .map((result) => result[0].transcript)
          .join(" ")
          .trim();
      };
      recognition.onerror = (event) => {
        if (stoppingRecognition) return;
        recognitionFailed = true;
        status.textContent = event.error === "not-allowed"
          ? "Microphone permission was denied. Allow microphone access or type your question."
          : "Voice input stopped. Try again or type your question.";
      };
      recognition.onend = () => {
        listenButton.disabled = false;
        if (stoppingRecognition) {
          stoppingRecognition = false;
          return;
        }
        if (recognitionFailed) return;
        if (!transcript) {
          status.textContent = "No speech was detected. Try again or type your question.";
          return;
        }
        prompt.value = transcript;
        status.textContent = "Question heard. Sending it to your study buddy…";
        const voiceField = document.createElement("input");
        voiceField.type = "hidden";
        voiceField.name = "voice";
        voiceField.value = "1";
        form.appendChild(voiceField);
        form.requestSubmit();
      };

      listenButton.addEventListener("click", () => {
        try {
          recognition.start();
        } catch (_error) {
          status.textContent = "Voice input is busy. Wait a moment and try again.";
        }
      });
    } catch (_error) {
      listenButton.disabled = true;
      status.textContent = "Voice input could not start in this browser. You can type your question instead.";
    }
  }

  const voiceResponse = document.querySelector('[data-speak-response="true"]');
  if (voiceResponse) speakAnswer();
})();
