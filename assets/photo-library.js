/* Public, unlisted asset catalog. No upload, promotion, or third-party dependencies. */
(() => {
  'use strict';

  const CANONICAL_ORIGIN = 'https://island-jiu-jitsu-washington.netlify.app/';
  const PAGE_SIZE = 24;
  const VARIANT_NAMES = ['thumbnail', 'medium', 'large'];
  const numberFormat = new Intl.NumberFormat('en-US');
  const byId = (id) => document.getElementById(id);
  const grid = byId('pl-grid');
  const search = byId('pl-search');
  const orientation = byId('pl-orientation');
  const clear = byId('pl-clear');
  const results = byId('pl-results');
  const dialog = byId('pl-dialog');
  const preview = byId('pl-preview-image');
  const previous = byId('pl-previous');
  const next = byId('pl-next');
  let photos = [];
  let filtered = [];
  let page = 1;
  let selectedPhoto = null;
  let opener = null;
  let loading = false;
  let copySequence = 0;

  // Preserve the homepage's menu hook, without loading its promotion script.
  const header = document.querySelector('.site-header');
  const menu = header.querySelector('.menu-toggle');
  const nav = header.querySelector('.nav');
  menu.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(opened));
  });
  header.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      nav.classList.remove('open');
      menu.setAttribute('aria-expanded', 'false');
      menu.focus();
    }
  });

  function makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = String(text);
    return element;
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
    const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    return `${numberFormat.format(Number((bytes / (1024 ** index)).toFixed(index === 0 ? 0 : 1)))} ${units[index]}`;
  }

  function isInteger(value, minimum = 0) {
    return Number.isSafeInteger(value) && value >= minimum;
  }

  function isPhotoPath(path) {
    // Keep both local previews and canonical links inside the photo assets directory.
    return typeof path === 'string'
      && path.startsWith('assets/photos/')
      && path.toLowerCase().endsWith('.webp')
      && !/[\\?#\u0000-\u001f\u007f]/.test(path)
      && path.split('/').every((part) => part && part !== '.' && part !== '..');
  }

  function encodedPath(path) {
    return path.split('/').map((part) => encodeURIComponent(part)).join('/');
  }

  function canonicalURL(path) {
    if (!isPhotoPath(path)) throw new Error('Invalid image path.');
    return new URL(encodedPath(path), CANONICAL_ORIGIN).href;
  }

  function localURL(path) {
    return `./${encodedPath(path)}`;
  }

  function validateLibrary(data) {
    if (!data || typeof data !== 'object' || !data.summary || !Array.isArray(data.photos)) {
      throw new Error('The library inventory is missing its summary or photos.');
    }
    const summaryFields = [
      'sourcePhotoCount', 'uniquePhotoCount', 'duplicateCount',
      'originalPhotoBytes', 'optimizedTotalBytes', 'largeTotalBytes'
    ];
    if (!summaryFields.every((field) => isInteger(data.summary[field]))) {
      throw new Error('The inventory contains invalid summary totals.');
    }
    const ids = new Set();
    for (const photo of data.photos) {
      const valid = photo && typeof photo.id === 'string' && photo.id.length > 0
        && !ids.has(photo.id) && typeof photo.name === 'string'
        && Array.isArray(photo.sourceFiles) && photo.sourceFiles.length > 0
        && photo.sourceFiles.every((name) => typeof name === 'string' && name.length > 0)
        && isInteger(photo.sourceWidth, 1) && isInteger(photo.sourceHeight, 1)
        && ['landscape', 'portrait', 'square'].includes(photo.orientation)
        && photo.variants && VARIANT_NAMES.every((name) => {
          const variant = photo.variants[name];
          return variant && isPhotoPath(variant.path) && isInteger(variant.width, 1)
            && isInteger(variant.height, 1) && isInteger(variant.bytes);
        });
      if (!valid) throw new Error('The inventory contains an invalid photo entry.');
      ids.add(photo.id);
    }
    return data;
  }

  function renderSummary(summary) {
    byId('pl-source-count').textContent = numberFormat.format(summary.sourcePhotoCount);
    byId('pl-unique-count').textContent = numberFormat.format(summary.uniquePhotoCount);
    byId('pl-duplicate-count').textContent = numberFormat.format(summary.duplicateCount);
    byId('pl-original-bytes').textContent = formatBytes(summary.originalPhotoBytes);
    byId('pl-optimized-bytes').textContent = formatBytes(summary.optimizedTotalBytes);
    const savedBytes = summary.originalPhotoBytes - summary.optimizedTotalBytes;
    const savedPercent = summary.originalPhotoBytes > 0
      ? (savedBytes / summary.originalPhotoBytes) * 100 : 0;
    byId('pl-savings').textContent = summary.originalPhotoBytes === 0 ? 'Not available'
      : savedBytes >= 0 ? `${savedPercent.toFixed(1)}%` : `${Math.abs(savedPercent).toFixed(1)}% larger`;
    const comparison = savedBytes >= 0
      ? `${formatBytes(savedBytes)} saved versus the original photos`
      : `${formatBytes(Math.abs(savedBytes))} more than the original photos`;
    byId('pl-summary-note').textContent = `${comparison}. All WebP variants includes thumbnail, medium, and large files; large files alone total ${formatBytes(summary.largeTotalBytes)}. Original totals include duplicate source files.`;
  }

  function createCard(photo) {
    const thumbnail = photo.variants.thumbnail;
    const item = makeElement('li', 'pl-card');
    const button = makeElement('button', 'pl-card-button');
    button.type = 'button';
    button.setAttribute('aria-label', `Open photo: ${photo.sourceFiles[0]}`);
    button.setAttribute('aria-haspopup', 'dialog');
    const frame = makeElement('span', 'pl-thumbnail-frame');
    const image = makeElement('img');
    image.alt = ''; // The button is named by the actual original filename.
    image.width = thumbnail.width;
    image.height = thumbnail.height;
    image.loading = 'lazy';
    image.decoding = 'async';
    image.addEventListener('error', () => {
      image.hidden = true;
      frame.append(makeElement('span', 'pl-thumbnail-error', 'Thumbnail unavailable'));
    }, { once: true });
    image.src = localURL(thumbnail.path);
    frame.append(image);
    const copy = makeElement('span', 'pl-card-copy');
    copy.append(makeElement('span', 'pl-card-name', photo.sourceFiles[0]));
    const aliases = photo.sourceFiles.length > 1 ? ` · ${photo.sourceFiles.length} original filenames` : '';
    copy.append(makeElement('span', 'pl-card-meta', `${photo.sourceWidth} × ${photo.sourceHeight} · ${photo.orientation}${aliases}`));
    button.append(frame, copy);
    button.addEventListener('click', () => openPhoto(photo, button));
    item.append(button);
    return item;
  }

  function renderPage(moveFocus = false) {
    const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    page = Math.min(Math.max(page, 1), pageCount);
    const start = (page - 1) * PAGE_SIZE;
    const visiblePhotos = filtered.slice(start, start + PAGE_SIZE);
    const fragment = document.createDocumentFragment();
    visiblePhotos.forEach((photo) => fragment.append(createCard(photo)));
    // Only these 24 thumbnail elements exist: other pages are not hidden/preloaded.
    grid.replaceChildren(fragment);
    grid.setAttribute('aria-busy', 'false');
    const matchingCount = numberFormat.format(filtered.length);
    const totalCount = numberFormat.format(photos.length);
    results.textContent = filtered.length
      ? `Showing ${numberFormat.format(start + 1)}–${numberFormat.format(start + visiblePhotos.length)} of ${matchingCount} matching photos · ${totalCount} total`
      : `0 matching photos · ${totalCount} total`;
    byId('pl-empty').hidden = filtered.length !== 0;
    byId('pl-pagination').hidden = filtered.length <= PAGE_SIZE;
    byId('pl-page-label').textContent = `Page ${page} of ${pageCount}`;
    previous.disabled = page === 1;
    next.disabled = page === pageCount;
    if (moveFocus) {
      results.tabIndex = -1;
      results.focus({ preventScroll: true });
      results.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
  }

  function applyFilters() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    filtered = photos.filter((photo) => {
      const matchesOrientation = orientation.value === 'all' || photo.orientation === orientation.value;
      const searchable = [photo.id, photo.name, ...photo.sourceFiles].join(' ').toLocaleLowerCase();
      return matchesOrientation && terms.every((term) => searchable.includes(term));
    });
    page = 1;
    renderPage();
  }

  async function loadLibrary() {
    if (loading) return;
    loading = true;
    byId('pl-error').hidden = true;
    byId('pl-retry').disabled = true;
    grid.setAttribute('aria-busy', 'true');
    results.textContent = 'Loading photo inventory…';
    try {
      const response = await fetch('./assets/photos/library.json', { cache: 'no-cache' });
      if (!response.ok) throw new Error(`Inventory request returned HTTP ${response.status}.`);
      const data = validateLibrary(await response.json());
      photos = data.photos;
      renderSummary(data.summary);
      search.disabled = false;
      orientation.disabled = false;
      clear.disabled = false;
      applyFilters();
    } catch (error) {
      grid.setAttribute('aria-busy', 'false');
      results.textContent = 'Photo inventory unavailable.';
      byId('pl-error-message').textContent = 'Could not load assets/photos/library.json. Check that the inventory has been published alongside this page, and use an HTTP preview rather than opening the file directly. Please try again.';
      byId('pl-error').hidden = false;
      console.error('Photo library load failed:', error);
    } finally {
      loading = false;
      byId('pl-retry').disabled = false;
    }
  }

  function addMetadata(label, value) {
    byId('pl-photo-meta').append(makeElement('dt', '', label), makeElement('dd', '', value));
  }

  function openPhoto(photo, button) {
    if (typeof dialog.showModal !== 'function') {
      byId('pl-copy-status').textContent = 'Your browser does not support native photo dialogs. Please use a current browser or download the inventory CSV.';
      return;
    }
    selectedPhoto = photo;
    opener = button;
    const large = photo.variants.large;
    byId('pl-dialog-title').textContent = photo.sourceFiles[0];
    byId('pl-dialog-status').textContent = '';
    byId('pl-image-error').hidden = true;
    preview.alt = `Original file: ${photo.sourceFiles[0]}`;
    preview.width = large.width;
    preview.height = large.height;
    preview.src = localURL(large.path);
    byId('pl-photo-meta').replaceChildren();
    addMetadata('Photo ID', photo.id);
    addMetadata('Original size', `${photo.sourceWidth} × ${photo.sourceHeight} px`);
    addMetadata('Orientation', photo.orientation);
    addMetadata('Large preview', `${large.width} × ${large.height} px · ${formatBytes(large.bytes)}`);
    byId('pl-original-names').replaceChildren(...photo.sourceFiles.map((name) => makeElement('li', '', name)));
    const links = VARIANT_NAMES.map((name) => {
      const variant = photo.variants[name];
      const item = makeElement('li');
      const link = makeElement('a', 'pl-variant-link');
      link.href = canonicalURL(variant.path);
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.append(makeElement('strong', '', `${name[0].toUpperCase()}${name.slice(1)} ↗`));
      link.append(makeElement('span', '', `${variant.width} × ${variant.height} px · ${formatBytes(variant.bytes)}`));
      item.append(link);
      return item;
    });
    byId('pl-variant-links').replaceChildren(...links);
    dialog.showModal(); // Native focus containment, inert background, and Escape handling.
    document.body.classList.add('pl-dialog-open');
  }

  function escapeAttribute(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[character]);
  }

  function responsiveHTML(photo) {
    const variantsByWidth = new Map();
    // Later (higher-quality) variants replace duplicates at the same actual width.
    VARIANT_NAMES.forEach((name) => {
      const variant = photo.variants[name];
      variantsByWidth.set(variant.width, variant);
    });
    const srcset = [...variantsByWidth.values()]
      .sort((a, b) => a.width - b.width)
      .map((variant) => `${canonicalURL(variant.path)} ${variant.width}w`).join(',\n    ');
    const fallback = photo.variants.medium;
    const displayWidth = Math.min(960, photo.variants.large.width);
    // The example's CSS and sizes agree: viewport minus 16px per side, capped here.
    return [
      '<!-- Full-viewport example with 16px side gutters. Adjust both width and sizes if placed in a narrower container. -->',
      '<img',
      `  src="${escapeAttribute(canonicalURL(fallback.path))}"`,
      `  srcset="${escapeAttribute(srcset)}"`,
      `  sizes="(max-width: ${displayWidth + 32}px) calc(100vw - 32px), ${displayWidth}px"`,
      `  width="${fallback.width}" height="${fallback.height}"`,
      '  alt="Describe this photo before publishing"',
      '  loading="lazy" decoding="async"',
      `  style="display: block; width: min(${displayWidth}px, calc(100vw - 32px)); height: auto;"`,
      '/>'
    ].join('\n');
  }

  function fallbackCopy(text) {
    const activeElement = document.activeElement;
    const textarea = makeElement('textarea');
    textarea.value = text;
    textarea.readOnly = true;
    textarea.tabIndex = -1;
    textarea.setAttribute('aria-label', 'Clipboard copy buffer');
    textarea.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;padding:0;border:0;opacity:0;';
    // Appending inside an open dialog keeps the fallback within its native focus boundary.
    (dialog.open ? dialog : document.body).append(textarea);
    let copied = false;
    try {
      textarea.focus({ preventScroll: true });
      textarea.select();
      textarea.setSelectionRange(0, text.length);
      copied = typeof document.execCommand === 'function' && document.execCommand('copy');
    } catch (_) {
      copied = false;
    } finally {
      textarea.remove();
      if (activeElement && activeElement.isConnected) activeElement.focus({ preventScroll: true });
    }
    return copied;
  }

  async function copyText(text, label, button) {
    button.disabled = true;
    let copied = false;
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        try {
          await navigator.clipboard.writeText(text);
          copied = true;
        } catch (_) {
          // Permission-denied/insecure contexts can still support the legacy fallback.
        }
      }
      if (!copied) copied = fallbackCopy(text);
      const message = copied
        ? `${label} copied.${label === 'Responsive HTML' ? ' Replace the alt-text placeholder before publishing.' : ''}`
        : 'Could not copy automatically. Check browser clipboard permissions and try again; you can also open a variant link and copy its address.';
      const status = dialog.open ? byId('pl-dialog-status') : byId('pl-copy-status');
      status.textContent = '';
      const sequence = ++copySequence;
      // A separate update lets screen readers announce repeated copy actions too.
      window.setTimeout(() => {
        if (sequence === copySequence) {
          (dialog.open ? byId('pl-dialog-status') : byId('pl-copy-status')).textContent = message;
        }
      }, 40);
    } finally {
      button.disabled = false;
    }
  }

  byId('pl-filters').addEventListener('submit', (event) => event.preventDefault());
  search.addEventListener('input', applyFilters);
  orientation.addEventListener('change', applyFilters);
  clear.addEventListener('click', () => {
    search.value = '';
    orientation.value = 'all';
    applyFilters();
    search.focus();
  });
  previous.addEventListener('click', () => { page -= 1; renderPage(true); });
  next.addEventListener('click', () => { page += 1; renderPage(true); });
  byId('pl-retry').addEventListener('click', loadLibrary);
  byId('pl-dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('pl-dialog-open');
    preview.removeAttribute('src');
    selectedPhoto = null;
    if (opener && opener.isConnected) opener.focus({ preventScroll: true });
    opener = null;
  });
  preview.addEventListener('error', () => {
    if (dialog.open && preview.hasAttribute('src')) byId('pl-image-error').hidden = false;
  });
  byId('pl-copy-url').addEventListener('click', () => {
    if (selectedPhoto) void copyText(canonicalURL(selectedPhoto.variants.large.path), 'Large URL', byId('pl-copy-url'));
  });
  byId('pl-copy-html').addEventListener('click', () => {
    if (selectedPhoto) void copyText(responsiveHTML(selectedPhoto), 'Responsive HTML', byId('pl-copy-html'));
  });

  void loadLibrary();
})();
