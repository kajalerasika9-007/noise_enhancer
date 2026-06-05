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
    const res = await fetch('https://noise-enhancer-6.onrender.com/process', {
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
