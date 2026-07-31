/* In-page PDF viewer modal, shared by index.html and pages/publications.html.
   Any link with class="pdf-link" and data-pdf="/path/to/file.pdf" opens that
   PDF in an overlay instead of navigating away. Falls back to a normal link
   (href points at the same PDF) if JS fails to load. */
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
          <button class="pdf-modal-close" type="button" aria-label="Close PDF viewer">&times;</button>
        </div>
        <iframe class="pdf-modal-frame" id="pdf-modal-frame" title="PDF viewer"></iframe>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) closePdfModal(); });
    modal.querySelector('.pdf-modal-close').addEventListener('click', closePdfModal);
    return modal;
  }

  function openPdfModal(url){
    if (!modalEl) modalEl = buildModal();
    document.getElementById('pdf-modal-frame').src = url;
    document.getElementById('pdf-modal-open').href = url;
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
    const link = e.target.closest('.pdf-link');
    if (!link) return;
    e.preventDefault();
    openPdfModal(link.dataset.pdf);
  });
})();
