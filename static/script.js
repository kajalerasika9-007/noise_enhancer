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

    // check file type and set correct download format
    const fileName = file.name.toLowerCase();
    const isVideo = fileName.endsWith('.mp4') || 
                    fileName.endsWith('.mov') || 
                    fileName.endsWith('.avi');

    if (isVideo) {
      link.download = 'clean_video.mp4';  // mp4 opens on every device
      status.textContent = '✅ Done! Your clean video is ready.';
    } else {
      link.download = 'clean_audio.mp3';  // mp3 opens on every device
      status.textContent = '✅ Done! Your clean audio is ready.';
    }

    link.hidden = false;

  } catch (e) {
    console.error(e);
    status.textContent = '❌ Cannot connect to backend.';
  }
});
