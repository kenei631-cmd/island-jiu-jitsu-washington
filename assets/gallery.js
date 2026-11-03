(() => {
  const root = document.querySelector('[data-gallery]');
  if (!root) return;
  const filters = [...root.querySelectorAll('[data-gallery-filter]')];
  const sections = [...root.querySelectorAll('[data-gallery-section]')];
  const status = document.getElementById('gallery-status');
  const dialog = document.getElementById('gallery-viewer');
  const image = document.getElementById('gallery-viewer-image');
  const caption = document.getElementById('gallery-viewer-title');
  const counter = document.getElementById('gallery-viewer-counter');
  const previous = dialog.querySelector('[data-gallery-previous]');
  const next = dialog.querySelector('[data-gallery-next]');
  let category = 'gym';
  let current = 0;
  let opener = null;
  const label = value => value === 'competition' ? 'Competition & Medals' : 'In the Gym';
  const currentLinks = () => [...root.querySelectorAll(`[data-gallery-section="${category}"] .gallery-open`)];

  function selectCategory(value, updateHash = true) {
    category = value === 'competition' ? 'competition' : 'gym';
    sections.forEach(section => { section.hidden = section.dataset.gallerySection !== category; });
    filters.forEach(button => {
      const selected = button.dataset.galleryFilter === category;
      button.setAttribute('aria-pressed', String(selected));
      button.classList.toggle('selected', selected);
    });
    status.textContent = `${currentLinks().length} photos · ${label(category)}`;
    if (updateHash && location.hash !== `#${category}`) history.replaceState(null, '', `#${category}`);
  }

  function renderPhoto(index) {
    const links = currentLinks();
    current = (index + links.length) % links.length;
    const link = links[current];
    const thumbnail = link.querySelector('img');
    image.src = link.href;
    image.alt = thumbnail.alt;
    caption.textContent = link.closest('figure').querySelector('figcaption h3').textContent;
    counter.textContent = `${current + 1} of ${links.length} · ${label(category)}`;
    document.getElementById('gallery-original').href = link.href;
    previous.disabled = next.disabled = links.length < 2;
  }

  filters.forEach(button => button.addEventListener('click', () => selectCategory(button.dataset.galleryFilter)));
  root.querySelectorAll('.gallery-open').forEach(link => link.addEventListener('click', event => {
    if (!dialog.showModal || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    category = link.closest('[data-gallery-section]').dataset.gallerySection;
    opener = link;
    renderPhoto(currentLinks().indexOf(link));
    dialog.showModal();
    document.documentElement.classList.add('gallery-viewer-open');
    dialog.querySelector('[data-gallery-close]').focus();
  }));
  dialog.querySelector('[data-gallery-close]').addEventListener('click', () => dialog.close());
  previous.addEventListener('click', () => renderPhoto(current - 1));
  next.addEventListener('click', () => renderPhoto(current + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); renderPhoto(current - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); renderPhoto(current + 1); }
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('gallery-viewer-open');
    if (opener) opener.focus({ preventScroll: true });
    image.removeAttribute('src');
  });
  window.addEventListener('hashchange', () => selectCategory(location.hash.slice(1), false));
  selectCategory(location.hash.slice(1), false);
})();
