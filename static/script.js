async function processVideo() {
  const url = document.getElementById('yt-url').value.trim();
  const status = document.getElementById('status');
  const link = document.getElementById('download-link');
  if (!url) {
    status.textContent = '⚠ Please paste a YouTube URL first.';
    return;
  }
  status.textContent = '⏳ Processing... this may take 1-2 minutes. Please wait.';
  link.hidden = true;
  try {
    const res = await fetch('/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    if (!res.ok) {
      const errorText = await res.text();
      console.error(errorText);
      status.textContent = '❌ Something went wrong. Check Render logs.';
      return;
    }
    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    link.href = downloadUrl;
    link.download = 'clean_video.mp4';
    link.hidden = false;
    status.textContent = '✅ Done! Your clean video is ready.';
  } catch (e) {
    console.error(e);
    status.textContent = '❌ Cannot connect to backend.';
  }
}

function openFileExplorer() {
  document.getElementById("fileInput").click();
}

document.getElementById("fileInput").addEventListener("change", async function(event) {
  const file = event.target.files[0];
  if (!file) return;

  const status = document.getElementById('status');
  const link = document.getElementById('download-link');

  status.textContent = '⏳ Processing... please wait, this may take a few minutes.';
  link.hidden = true;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/process-file', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(errorText);
      status.textContent = '❌ Something went wrong. Check logs.';
      return;
    }

    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    link.href = downloadUrl;
    link.download = 'clean_audio.wav';
    link.hidden = false;
    status.textContent = '✅ Done! Your clean file is ready.';

  } catch (e) {
    console.error(e);
    status.textContent = '❌ Cannot connect to backend.';
  }
});
