function descargar() {
  const url = document.getElementById("youtubeURL").value;
  fetch("/descargar", {
    method: "POST",
    body: new URLSearchParams({ url })
  }).then(res => res.json()).then(data => {
    if (data.video_url) {
      document.getElementById("videoPlayer").src = data.video_url;
    }
  });
}
