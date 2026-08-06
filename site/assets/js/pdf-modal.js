/* In-page media viewer modal, shared across the site's pages.
   - Any link with class="pdf-link" and data-pdf="/path/to/file.pdf" opens
     that PDF in an overlay instead of navigating away.
   - Any link with class="video-link" and data-video="<embed URL>" (e.g. a
     youtube.com/embed/<id> URL) opens that video the same way. Optionally
     set data-open="<watch URL>" for a nicer "Open in new tab" target than
     the bare embed URL.
   Falls back to a normal link (href points at the PDF/video page) if JS
   fails to load. */
(function(){
  let modalEl = null;

  function buildModal(){
    const modal = document.createElement('div');
    modal.className = 'pdf-modal';
    modal.id = 'pdf-modal';
    modal.innerHTML = `
      <div class="pdf-modal-inner">
        <div class="pdf-modal-bar">
          <a id="pdf-modal-open" target="_blank" rel="noopener">Open in new tab &#8599;</a>
          <button class="pdf-modal-close" type="button" aria-label="Close viewer">&times;</button>
        </div>
        <iframe class="pdf-modal-frame" id="pdf-modal-frame" title="Media viewer"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen></iframe>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) closePdfModal(); });
    modal.querySelector('.pdf-modal-close').addEventListener('click', closePdfModal);
    return modal;
  }

  function openPdfModal(embedUrl, openUrl){
    if (!modalEl) modalEl = buildModal();
    document.getElementById('pdf-modal-frame').src = embedUrl;
    document.getElementById('pdf-modal-open').href = openUrl || embedUrl;
    modalEl.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closePdfModal(){
    if (!modalEl) return;
    modalEl.classList.remove('open');
    document.getElementById('pdf-modal-frame').src = '';
    document.body.style.overflow = '';
  }

  window.openPdfModal = openPdfModal;
  window.closePdfModal = closePdfModal;

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closePdfModal(); });
  document.addEventListener('click', e => {
    const link = e.target.closest('.pdf-link, .video-link');
    if (!link) return;
    e.preventDefault();
    const embedUrl = link.dataset.pdf || link.dataset.video;
    openPdfModal(embedUrl, link.dataset.open || embedUrl);
  });
})();
