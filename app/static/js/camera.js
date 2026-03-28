(function () {

  let stream = null;
  let opening = false;

  // ─── Para a câmera e libera o stream ───────────────────────────────
  function stopCamera() {
    if (!stream) return;
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }

  // ─── Aguarda o vídeo ter dimensões válidas ─────────────────────────
  // Edge às vezes dispara loadedmetadata com width/height = 0
  function waitForVideoDimensions(videoEl, timeout = 5000) {
    return new Promise((resolve, reject) => {
      const start = Date.now();

      function check() {
        if (videoEl.videoWidth > 0 && videoEl.videoHeight > 0) {
          resolve();
        } else if (Date.now() - start > timeout) {
          reject(new Error("Timeout aguardando dimensões do vídeo"));
        } else {
          requestAnimationFrame(check);
        }
      }

      // Se metadata já carregou, vai direto checar dimensões
      if (videoEl.readyState >= 1) {
        check();
      } else {
        videoEl.addEventListener("loadedmetadata", check, { once: true });
      }
    });
  }

  // ─── Abre a câmera ─────────────────────────────────────────────────
  async function openCamera(videoEl) {

    if (opening) return;
    opening = true;

    // Garante que câmera anterior foi liberada
    stopCamera();

    // Reseta o elemento de vídeo (evita estado sujo no Edge)
    videoEl.pause();
    videoEl.srcObject = null;

    try {

      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      });

      videoEl.srcObject = stream;

      // ✅ Aguarda metadata + dimensões válidas (fix Edge)
      await waitForVideoDimensions(videoEl);

      // play() pode rejeitar no Edge se não for muted/playsinline
      await videoEl.play();

      console.log(
        `Câmera iniciada: ${videoEl.videoWidth}x${videoEl.videoHeight}`
      );

    } catch (err) {

      console.error("Erro câmera:", err);

      // Mensagens amigáveis por tipo de erro
      const messages = {
        NotAllowedError:
          "Permissão negada. Permita o acesso à câmera nas configurações do Edge.",
        NotFoundError:
          "Nenhuma câmera encontrada no dispositivo.",
        NotReadableError:
          "A câmera está sendo usada por outro aplicativo.",
        OverconstrainedError:
          "A câmera não suporta as configurações solicitadas.",
        SecurityError:
          "Bloqueado por política de segurança. A página precisa estar em HTTPS.",
      };

      const msg = messages[err.name] ?? `${err.name}: ${err.message}`;
      alert(`❌ Câmera falhou:\n\n${msg}`);

      stopCamera();

    } finally {
      opening = false;
    }
  }

  // ─── Captura frame atual do vídeo ──────────────────────────────────
  function capture(videoEl) {

    if (!stream || videoEl.videoWidth === 0) {
      alert("Câmera não está ativa ou ainda está carregando.");
      return null;
    }

    const canvas = document.createElement("canvas");
    canvas.width  = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;

    const ctx = canvas.getContext("2d");

    // ✅ Espelha horizontalmente (mais natural para selfie)
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);

    ctx.drawImage(videoEl, 0, 0);

    return canvas.toDataURL("image/jpeg", 0.9);
  }

  // ─── Fecha a câmera ────────────────────────────────────────────────
  function closeCamera(videoEl) {
    stopCamera();

    // ✅ Ordem correta para Edge: pause → srcObject = null
    videoEl.pause();
    videoEl.srcObject = null;
  }

  // ─── Inicializa todos os blocos [data-camera="1"] ──────────────────
  window.initCameraBlocks = function () {

    document.querySelectorAll('[data-camera="1"]').forEach(block => {

      const video   = block.querySelector("video");
      const preview = block.querySelector("[data-preview]");
      const input   = block.querySelector('input[name="photo_data_url"]');

      const btnOpen    = block.querySelector("[data-open]");
      const btnCapture = block.querySelector("[data-capture]");
      const btnClose   = block.querySelector("[data-close]");
      const btnEnable  = block.querySelector("[data-enable-on-capture]");

      btnOpen?.addEventListener("click", () => openCamera(video));

      btnCapture?.addEventListener("click", () => {
        const img = capture(video);
        if (!img) return;

        input.value = img;

        if (preview) {
          preview.src = img;
          preview.style.display = "block";
        }

        if (btnEnable) btnEnable.disabled = false;
      });

      btnClose?.addEventListener("click", () => closeCamera(video));

      // Libera câmera ao sair da página
      window.addEventListener("beforeunload", stopCamera);
    });
  };

  // Inicializa no DOMContentLoaded ou imediatamente se já carregou
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.initCameraBlocks);
  } else {
    window.initCameraBlocks();
  }

})();
