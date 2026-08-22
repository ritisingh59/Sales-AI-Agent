// Northstar AI Agent Client Application

let sessionId = "ns-session-" + Math.random().toString(36).substring(2, 9);
let voiceAudioEnabled = true;
let availableVoices = [];

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const typingIndicator = document.getElementById("typingIndicator");
const ttsToggleBtn = document.getElementById("ttsToggleBtn");
const ttsIcon = document.getElementById("ttsIcon");
const ttsLabel = document.getElementById("ttsLabel");
const resetChatBtn = document.getElementById("resetChatBtn");
const endSessionBtn = document.getElementById("endSessionBtn");
const toolActivityFeed = document.getElementById("toolActivityFeed");
const analyticsPlaceholder = document.getElementById("analyticsPlaceholder");
const analyticsResults = document.getElementById("analyticsResults");
const micBtn = document.getElementById("micBtn");
const voiceLangSelect = document.getElementById("voiceLangSelect");

// Analytics fields
const anInterest = document.getElementById("anInterest");
const anConfig = document.getElementById("anConfig");
const anBudget = document.getElementById("anBudget");
const anVisitStatus = document.getElementById("anVisitStatus");
const anObjections = document.getElementById("anObjections");
const anFollowUpFlag = document.getElementById("anFollowUpFlag");
const anFollowUpNote = document.getElementById("anFollowUpNote");
const anEscalation = document.getElementById("anEscalation");
const anSummary = document.getElementById("anSummary");
const anRawJson = document.getElementById("anRawJson");
const leadBadge = document.getElementById("leadBadge");

// Initialize Speech Voices
function loadVoices() {
  if ("speechSynthesis" in window) {
    availableVoices = window.speechSynthesis.getVoices();
  }
}

if ("speechSynthesis" in window) {
  loadVoices();
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  renderInitialGreeting();
  setupEventListeners();
  setupQuickScenarios();
});

function renderInitialGreeting() {
  chatMessages.innerHTML = "";
  appendAgentMessage("Namaste and welcome to Northstar Homes! I'm Riti. How may I assist you with Northstar One in Sector 79, Gurugram today?");
}

function setupEventListeners() {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;
    
    userInput.value = "";
    await handleUserMessage(message);
  });

  resetChatBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId })
      });
      sessionId = "ns-session-" + Math.random().toString(36).substring(2, 9);
      renderInitialGreeting();
      toolActivityFeed.innerHTML = '<p class="text-slate-500">Session reset. Ready for new interactions.</p>';
      analyticsPlaceholder.classList.remove("hidden");
      analyticsResults.classList.add("hidden");
      leadBadge.textContent = "Active Conversation";
      leadBadge.className = "text-[11px] px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-medium border border-slate-700";
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    } catch (err) {
      console.error("Error resetting session:", err);
    }
  });

  endSessionBtn.addEventListener("click", async () => {
    await fetchAndRenderAnalytics();
  });

  ttsToggleBtn.addEventListener("click", () => {
    voiceAudioEnabled = !voiceAudioEnabled;
    if (voiceAudioEnabled) {
      ttsIcon.className = "fa-solid fa-volume-high text-amber-400";
      ttsLabel.textContent = "Voice: ON";
    } else {
      ttsIcon.className = "fa-solid fa-volume-xmark text-slate-400";
      ttsLabel.textContent = "Voice: OFF";
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    }
  });

  // Enhanced Speech Recognition (Microphone Voice Input)
  setupMicrophoneHandler();
}

let isRecording = false;
let speechRecognizer = null;

function setupMicrophoneHandler() {
  const listeningIndicator = document.getElementById("listeningIndicator");
  const listeningText = document.getElementById("listeningText");
  const stopListeningBtn = document.getElementById("stopListeningBtn");
  const micHelperToast = document.getElementById("micHelperToast");
  const micHelperText = document.getElementById("micHelperText");
  const closeToastBtn = document.getElementById("closeToastBtn");

  if (closeToastBtn) {
    closeToastBtn.addEventListener("click", () => {
      micHelperToast.classList.add("hidden");
    });
  }

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRec) {
    micBtn.addEventListener("click", () => {
      showMicToast("⚠️ Web Speech API is not supported in this browser. Please use Google Chrome or Microsoft Edge.", "error");
    });
    return;
  }

  try {
    speechRecognizer = new SpeechRec();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = true;
    speechRecognizer.maxAlternatives = 1;

    speechRecognizer.onstart = () => {
      isRecording = true;
      micBtn.classList.add("bg-rose-500", "text-white", "animate-pulse");
      micBtn.classList.remove("bg-slate-800", "text-slate-300");
      listeningIndicator.classList.remove("hidden");
      listeningText.textContent = "🔴 Listening... Speak now (Hindi, Hinglish, or English)";
    };

    speechRecognizer.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (interimTranscript) {
        userInput.value = interimTranscript;
        listeningText.textContent = `🎙️ "${interimTranscript}..."`;
      }

      if (finalTranscript) {
        userInput.value = finalTranscript;
        stopRecording();
        handleUserMessage(finalTranscript);
      }
    };

    speechRecognizer.onerror = (event) => {
      console.warn("Speech recognition event error:", event.error);
      stopRecording();
      
      if (event.error === "not-allowed" || event.error === "permission-denied") {
        showMicToast("🔒 Microphone access was blocked. Please allow microphone permissions in your browser URL bar.", "error");
      } else if (event.error === "no-speech") {
        showMicToast("ℹ️ No speech was heard. Click the mic button and try speaking again.", "info");
      } else if (event.error === "network") {
        showMicToast("⚠️ Speech recognition network connection error.", "error");
      }
    };

    speechRecognizer.onend = () => {
      stopRecording();
    };

    micBtn.addEventListener("click", async () => {
      if (isRecording) {
        stopRecording();
        return;
      }

      // Check / request microphone permission
      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        }
      } catch (permErr) {
        console.warn("Microphone permission error:", permErr);
        showMicToast("🔒 Please allow microphone access in your browser to use voice input.", "error");
        return;
      }

      startRecording();
    });

    if (stopListeningBtn) {
      stopListeningBtn.addEventListener("click", () => {
        const text = userInput.value.trim();
        stopRecording();
        if (text) {
          handleUserMessage(text);
        }
      });
    }

  } catch (err) {
    console.error("Speech recognition initialization error:", err);
  }
}

function startRecording() {
  if (!speechRecognizer) return;
  try {
    // Choose appropriate recognition language
    const selLang = voiceLangSelect ? voiceLangSelect.value : "auto";
    if (selLang === "hi-IN") {
      speechRecognizer.lang = "hi-IN";
    } else if (selLang === "en-US") {
      speechRecognizer.lang = "en-US";
    } else {
      speechRecognizer.lang = "en-IN"; // handles Indian English & Hinglish natively
    }

    userInput.placeholder = "Listening to your voice...";
    speechRecognizer.start();
  } catch (err) {
    console.warn("Recognition already started or error:", err);
  }
}

function stopRecording() {
  isRecording = false;
  const listeningIndicator = document.getElementById("listeningIndicator");
  if (listeningIndicator) {
    listeningIndicator.classList.add("hidden");
  }
  micBtn.classList.remove("bg-rose-500", "text-white", "animate-pulse");
  micBtn.classList.add("bg-slate-800", "text-slate-300");
  userInput.placeholder = "Type or click 🎙️ Mic to speak (English, Hindi, or Hinglish)...";

  if (speechRecognizer) {
    try {
      speechRecognizer.stop();
    } catch (e) {}
  }
}

function showMicToast(message, type = "info") {
  const toast = document.getElementById("micHelperToast");
  const text = document.getElementById("micHelperText");
  if (toast && text) {
    text.textContent = message;
    toast.className = `px-4 py-2 text-xs flex items-center justify-between ${type === "error" ? "bg-rose-500/20 text-rose-300 border-t border-rose-500/40" : "bg-amber-500/15 text-amber-300 border-t border-amber-500/30"}`;
    toast.classList.remove("hidden");
    setTimeout(() => {
      toast.classList.add("hidden");
    }, 6000);
  }
}

function setupQuickScenarios() {
  document.querySelectorAll(".scenario-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-text");
      if (prompt) {
        userInput.value = "";
        handleUserMessage(prompt);
      }
    });
  });
}

async function handleUserMessage(message) {
  appendUserMessage(message);
  showTyping(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    showTyping(false);

    // Handle tool execution log display
    if (data.tool_executed && data.tools && data.tools.length > 0) {
      renderToolExecution(data.tools);
    }

    appendAgentMessage(data.response);

    // Speak response if voice audio is enabled
    if (voiceAudioEnabled) {
      speakText(data.response);
    }
  } catch (err) {
    showTyping(false);
    appendAgentMessage("I apologize, but I encountered a connection issue. Please allow me a moment to reconnect.");
    console.error("Chat error:", err);
  }
}

function appendUserMessage(text) {
  const el = document.createElement("div");
  el.className = "flex justify-end animate-fade-in";
  el.innerHTML = `
    <div class="user-bubble px-4 py-2.5 max-w-[80%] text-sm shadow-md">
      ${escapeHtml(text)}
    </div>
  `;
  chatMessages.appendChild(el);
  scrollToBottom();
}

function appendAgentMessage(text) {
  const el = document.createElement("div");
  el.className = "flex justify-start items-start space-x-2.5 animate-fade-in";
  el.innerHTML = `
    <div class="w-7 h-7 rounded-full bg-slate-800 border border-amber-500/30 flex-shrink-0 flex items-center justify-center text-amber-400 text-xs font-bold mt-0.5">
      A
    </div>
    <div class="agent-bubble px-4 py-2.5 max-w-[85%] text-sm leading-relaxed shadow-md">
      ${escapeHtml(text)}
    </div>
  `;
  chatMessages.appendChild(el);
  scrollToBottom();
}

function renderToolExecution(tools) {
  tools.forEach((t) => {
    const toolName = t.tool || "book_site_visit";
    const res = t.result || {};
    const isSuccess = res.status === "success";

    // Update Live Activity Feed on right panel
    const logEntry = document.createElement("div");
    logEntry.className = `p-1.5 rounded text-[11px] border ${isSuccess ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : "border-amber-500/30 bg-amber-500/10 text-amber-300"}`;
    logEntry.innerHTML = `
      <div class="flex justify-between">
        <strong>⚡ ${toolName}()</strong>
        <span>${isSuccess ? "✅ SUCCESS" : "⚠️ " + (res.error_code || "FAILED")}</span>
      </div>
      <div class="text-[10px] text-slate-400 mt-0.5">${JSON.stringify(t.arguments)}</div>
    `;
    toolActivityFeed.prepend(logEntry);

    // Also add subtle card inside chat stream
    const toolChatBadge = document.createElement("div");
    toolChatBadge.className = "flex justify-center my-2 animate-fade-in";
    toolChatBadge.innerHTML = `
      <div class="tool-badge px-3 py-1 rounded-full text-[11px] font-mono text-amber-300 flex items-center space-x-1.5">
        <i class="fa-solid fa-gear ${isSuccess ? 'text-emerald-400' : 'text-amber-400'}"></i>
        <span>[Tool: ${toolName}] &rarr; ${isSuccess ? 'Slot Reserved (' + res.booking_id + ')' : 'Slot Full (Fallback triggered)'}</span>
      </div>
    `;
    chatMessages.appendChild(toolChatBadge);
  });
  scrollToBottom();
}

async function fetchAndRenderAnalytics() {
  try {
    const response = await fetch("/api/end-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId })
    });

    const data = await response.json();
    const a = data.analytics;

    analyticsPlaceholder.classList.add("hidden");
    analyticsResults.classList.remove("hidden");

    // Populate fields
    anInterest.textContent = a.interest_level || "Warm";
    anConfig.textContent = a.preferred_configuration || "2 & 3 BHK";
    anBudget.textContent = a.budget || "Not Disclosed";
    anVisitStatus.textContent = a.site_visit_status || "Not Discussed";
    
    // Objections
    anObjections.innerHTML = "";
    if (a.objections_raised && a.objections_raised.length > 0) {
      a.objections_raised.forEach((obj) => {
        const span = document.createElement("span");
        span.className = "px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[10px]";
        span.textContent = obj;
        anObjections.appendChild(span);
      });
    } else {
      anObjections.innerHTML = '<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">None</span>';
    }

    // Follow-up
    anFollowUpFlag.textContent = a.follow_up_required ? "Yes (Required)" : "No (DND/Closed)";
    anFollowUpNote.textContent = a.follow_up_note || "Standard follow-up";

    // Escalation
    anEscalation.textContent = a.escalation_required ? `Yes (${a.escalation_reason || "Escalation requested"})` : "No (Handled by AI)";
    anEscalation.className = a.escalation_required ? "font-semibold text-rose-400" : "font-medium text-slate-300";

    // Summary & Raw JSON
    anSummary.textContent = a.executive_summary || "Conversation concluded.";
    anRawJson.textContent = JSON.stringify(a, null, 2);

    // Update Top Badge
    if (a.interest_level === "Hot") {
      leadBadge.textContent = "🔥 HOT LEAD";
      leadBadge.className = "text-[11px] px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold border border-rose-500/40";
    } else if (a.interest_level === "Dead" || a.purchase_intent === "DND") {
      leadBadge.textContent = "🛑 DND / CLOSED";
      leadBadge.className = "text-[11px] px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 font-medium border border-slate-700";
    } else {
      leadBadge.textContent = "☀️ " + a.interest_level.toUpperCase() + " LEAD";
      leadBadge.className = "text-[11px] px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/40";
    }
  } catch (err) {
    console.error("Error generating analytics:", err);
  }
}

function showTyping(show) {
  if (show) {
    typingIndicator.classList.remove("hidden");
  } else {
    typingIndicator.classList.add("hidden");
  }
  scrollToBottom();
}

/**
 * Intelligent Multi-Language Voice Synthesis (TTS)
 * Automatically adapts between Hindi, Hinglish, and English voices.
 */
function speakText(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  
  // Make sure voice list is loaded
  if (availableVoices.length === 0) {
    availableVoices = window.speechSynthesis.getVoices();
  }

  // Pre-process text for natural spoken pronunciation (e.g. ₹ to Rupees)
  let cleanText = text
    .replace(/₹\s*([0-9.]+)\s*(Crore|crore|Cr|cr)/gi, "$1 Crore Rupees")
    .replace(/₹\s*([0-9.]+)/g, "$1 Rupees")
    .replace(/2\s*BHK/gi, "2 B H K")
    .replace(/3\s*BHK/gi, "3 B H K");

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 0.95; // slightly relaxed for natural clarity
  utterance.pitch = 1.0;

  // Accurate Language Detection for Voice Synthesis
  const hasDevanagari = /[\u0900-\u097F]/.test(text);
  const textLower = text.toLowerCase();
  
  // Real Hindi / Hinglish lexical markers (excludes English loan words like BHK, Sector, Crore)
  const trueHinglishMarkers = ["namaste", "bilkul", "samajh", "hai", "kya", "aap", "mein", "hote", "chahiye", "kar rahe", "sakte", "shubh", "shukriya", "dijiye", "bataiye", "batao", "kitna", "accha", "bahut badhiya"];
  const isHinglishText = trueHinglishMarkers.some(k => textLower.includes(k));
  
  const userSelectedLang = voiceLangSelect ? voiceLangSelect.value : "auto";
  let targetLang = "en-US";

  if (userSelectedLang === "hi-IN" || (userSelectedLang === "auto" && hasDevanagari)) {
    targetLang = "hi-IN";
  } else if (userSelectedLang === "en-IN" || (userSelectedLang === "auto" && isHinglishText)) {
    targetLang = "en-IN";
  } else if (userSelectedLang === "en-US") {
    targetLang = "en-US";
  } else {
    // Pure English default
    targetLang = "en-US";
  }

  utterance.lang = targetLang;

  // Voice Selection Strategy
  let chosenVoice = null;
  if (targetLang === "hi-IN") {
    // 1. Pure Hindi Voices
    chosenVoice = availableVoices.find(v => v.lang.includes("hi") || v.name.toLowerCase().includes("hindi") || v.name.includes("Kalpana") || v.name.includes("Hemant") || v.name.includes("Swara") || v.name.includes("Madhur"));
    if (!chosenVoice) {
      chosenVoice = availableVoices.find(v => v.lang.includes("en-IN") || v.name.includes("Indian"));
    }
  } else if (targetLang === "en-IN") {
    // 2. Hinglish / Indian English Voices
    chosenVoice = availableVoices.find(v => v.lang.includes("en-IN") || v.name.includes("Indian") || v.name.includes("Ravi") || v.name.includes("Heera") || v.name.includes("Neerja") || v.name.includes("Prabhat") || v.name.includes("Zira"));
    if (!chosenVoice) {
      chosenVoice = availableVoices.find(v => v.lang.startsWith("en"));
    }
  } else {
    // 3. Clear Natural English Voices (US / UK / Natural)
    chosenVoice = availableVoices.find(v => (v.lang === "en-US" || v.lang === "en-GB" || v.lang.startsWith("en")) && !v.lang.includes("hi"));
  }

  if (chosenVoice) {
    utterance.voice = chosenVoice;
  }

  window.speechSynthesis.speak(utterance);
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
