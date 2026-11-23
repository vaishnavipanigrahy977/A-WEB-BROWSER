(() => {
  const readButton = document.querySelector("#voice-read");
  const stopButton = document.querySelector("#voice-stop");
  const status = document.querySelector("#voice-status");
  if (!readButton || !stopButton || !status) return;

  const speechSynthesis = window.speechSynthesis;
  const geminiSpeechEnabled = document.body.dataset.voiceGeminiEnabled === "true";
  const browserSpeechAvailable = !!speechSynthesis && !!window.SpeechSynthesisUtterance;
  let activeAudio = null;
  let activeAudioUrl = null;
  const pageLanguage = document.documentElement.lang;
  const voicePreferences = {
    en: ["en-US", "en-GB", "en"],
    hi: ["hi-IN", "hi"],
    "hi-Latn": ["hi-IN", "hi", "en-IN"],
  };
  const preferredLanguages = voicePreferences[pageLanguage] || voicePreferences.en;
  const hinglishPronunciations = {
    samjhayein: "समझाएँ",
    samjhaayein: "समझाएँ",
    samjhaein: "समझाएँ",
    samjhaaye: "समझाए",
    poochhein: "पूछें",
    seekhein: "सीखें",
    dekhein: "देखें",
    karein: "करें",
    banaayein: "बनाएँ",
    chunein: "चुनें",
    sunein: "सुनें",
    jaayein: "जाएँ",
    padhein: "पढ़ें",
    samjhein: "समझें",
    aap: "आप",
    aapke: "आपके",
    apni: "अपनी",
    apne: "अपने",
    hain: "हैं",
    hai: "है",
    kya: "क्या",
    ka: "का",
    ki: "की",
    ke: "के",
    mein: "में",
    aur: "और",
    yeh: "यह",
    ek: "एक",
    se: "से",
    ko: "को",
    par: "पर",
    liye: "लिए",
    madad: "मदद",
    jawaab: "जवाब",
    sawaal: "सवाल",
    jaankari: "जानकारी",
  };
  const languageName = pageLanguage === "hi"
    ? document.body.dataset.voiceHindiName
    : pageLanguage === "hi-Latn"
      ? document.body.dataset.voiceHinglishName
      : document.body.dataset.voiceEnglishName;

  if (!browserSpeechAvailable && !geminiSpeechEnabled) {
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

  const hinglishForHindiVoice = (text) => text.replace(/\b[\p{L}]+\b/gu, (word) => (
      hinglishPronunciations[word.toLowerCase()] || word
    ));

  const stopAudio = () => {
    if (activeAudio) {
      activeAudio.pause();
      activeAudio = null;
    }
    if (activeAudioUrl) {
      URL.revokeObjectURL(activeAudioUrl);
      activeAudioUrl = null;
    }
  };

  const speakWithGemini = async (text) => {
    status.textContent = document.body.dataset.voiceCloudLoading;
    const speechText = pageLanguage === "hi-Latn"
      ? hinglishForHindiVoice(text)
      : text;
    const response = await fetch("/study/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: speechText, language: pageLanguage === "hi-Latn" ? "hinglish" : pageLanguage }),
    });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || document.body.dataset.voiceError);
    }

    activeAudioUrl = URL.createObjectURL(await response.blob());
    activeAudio = new Audio(activeAudioUrl);
    activeAudio.onended = () => {
      stopAudio();
      status.textContent = document.body.dataset.voiceFinished;
    };
    activeAudio.onerror = () => {
      stopAudio();
      status.textContent = document.body.dataset.voiceError;
    };
    await activeAudio.play();
    status.textContent = document.body.dataset.voiceReading;
  };

  const matchingVoice = (voices) => {
    for (const language of preferredLanguages) {
      const match = voices.find((voice) => (
        voice.lang.toLowerCase().replace(/_/g, "-")
          .startsWith(language.toLowerCase())
      ));
      if (match) return match;
    }
    return null;
  };

  const availableVoices = () => new Promise((resolve) => {
    const voices = speechSynthesis.getVoices();
    if (voices.length) {
      resolve(voices);
      return;
    }

    let settled = false;
    const finish = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      speechSynthesis.removeEventListener("voiceschanged", finish);
      resolve(speechSynthesis.getVoices());
    };
    const timeout = setTimeout(finish, 1500);
    speechSynthesis.addEventListener("voiceschanged", finish);
  });

  readButton.addEventListener("click", async () => {
    const text = answerText();
    if (!text) {
      status.textContent = document.body.dataset.voiceAskFirst;
      return;
    }

    if (speechSynthesis) speechSynthesis.cancel();
    stopAudio();
    readButton.disabled = true;
    status.textContent = document.body.dataset.voiceLoading;
    try {
      if (!browserSpeechAvailable) {
        await speakWithGemini(text);
        return;
      }
      const voice = matchingVoice(await availableVoices());
      if (!voice) {
        if (geminiSpeechEnabled) {
          await speakWithGemini(text);
          return;
        }
        status.textContent = document.body.dataset.voiceMissing.replace(
          "{language}",
          languageName,
        );
        return;
      }

      speechSynthesis.cancel();
      stopAudio();
      const speechText = pageLanguage === "hi-Latn" && voice.lang.toLowerCase().startsWith("hi")
        ? hinglishForHindiVoice(text)
        : text;
      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.voice = voice;
      utterance.lang = voice.lang;
      utterance.onstart = () => { status.textContent = document.body.dataset.voiceReading; };
      utterance.onend = () => { status.textContent = document.body.dataset.voiceFinished; };
      utterance.onerror = () => { status.textContent = document.body.dataset.voiceError; };
      speechSynthesis.speak(utterance);
    } catch (error) {
      status.textContent = error instanceof Error && error.message
        ? error.message
        : document.body.dataset.voiceError;
    } finally {
      readButton.disabled = false;
    }
  });

  stopButton.addEventListener("click", () => {
    if (speechSynthesis) speechSynthesis.cancel();
    stopAudio();
    status.textContent = document.body.dataset.voiceStopped;
  });
})();
