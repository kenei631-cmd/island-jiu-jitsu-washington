/* Run from the local preview console; not loaded by the website. */
(async () => {
  const curation = await fetch('/gallery-curation.json').then(response => response.json());
  const selected = Object.fromEntries(Object.values(curation).flat().map(photo => [photo.id, photo]));
  const failures = [], results = [];
  const check = (condition, detail) => { if (!condition) failures.push(detail); };
  const options = window.galleryCheckOptions || {};
  function cropCheck(win, image, page, width) {
    const style = win.getComputedStyle(image), box = image.getBoundingClientRect();
    const scale = Math.max(box.width / image.naturalWidth, box.height / image.naturalHeight);
    const position = style.objectPosition.split(' ').map(value => parseFloat(value) / 100);
    const lossX = image.naturalWidth - box.width / scale;
    const lossY = image.naturalHeight - box.height / scale;
    const crop = [lossX * position[0] / image.naturalWidth, lossY * position[1] / image.naturalHeight,
      (lossX * position[0] + box.width / scale) / image.naturalWidth,
      (lossY * position[1] + box.height / scale) / image.naturalHeight];
    const photo = selected[image.dataset.photoId];
    const roi = photo.roi;
    const safe = crop[0] <= roi[0] + .003 && crop[1] <= roi[1] + .003 && crop[2] >= roi[2] - .003 && crop[3] >= roi[3] - .003;
    check(style.objectFit === 'cover' && image.complete && image.naturalWidth > 0 && safe,
      {page,viewport:width,photo:photo.source_name,issue:'Image fill or important-subject crop',crop,roi,fit:style.objectFit});
    return box;
  }
  for (const width of [1280, 768, 390, 320]) {
    for (const page of options.pages || ['gallery.html', 'index.html']) {
      const frame = document.createElement('iframe');
      frame.style.cssText = `position:absolute;left:-10000px;top:0;width:${width}px;height:844px;border:0`;
      document.body.append(frame);
      await new Promise(resolve => { frame.onload = resolve; frame.src = page + '?verify-gallery=' + width; });
      const doc = frame.contentDocument, win = frame.contentWindow;
      let checkedPhotos = 0;
      if (page === 'gallery.html') {
        check(!doc.querySelector('[data-gallery-section="gym"]').hidden && doc.querySelector('[data-gallery-section="competition"]').hidden,
          {page,viewport:width,issue:'Default category must be gym'});
        check(win.getComputedStyle(doc.querySelector('.gallery-filter.selected')).backgroundColor !== 'rgba(0, 0, 0, 0)',
          {page,viewport:width,issue:'Selected filter needs a visible dark background'});
        for (const category of options.categories || ['gym', 'competition']) {
          doc.querySelector(`[data-gallery-filter="${category}"]`).click();
          const section = doc.querySelector(`[data-gallery-section="${category}"]`);
          check(!section.hidden && doc.querySelector(`[data-gallery-filter="${category}"]`).getAttribute('aria-pressed') === 'true',
            {page,viewport:width,issue:'Category switching',category});
          const images = [...section.querySelectorAll('.gallery-photo img')];
          images.forEach(image => { image.loading = 'eager'; });
          await Promise.all(images.map(image => image.decode()));
          const boxes = images.map(image => cropCheck(win,image,page,width));
          check(Math.max(...boxes.map(box=>box.width))-Math.min(...boxes.map(box=>box.width)) < .5 &&
            Math.max(...boxes.map(box=>box.height))-Math.min(...boxes.map(box=>box.height)) < .5,
            {page,viewport:width,issue:'Gallery thumbnail frames differ'});
          checkedPhotos += images.length;
        }
        const viewerCategory = options.viewerCategory || 'competition';
        doc.querySelector(`[data-gallery-filter="${viewerCategory}"]`).click();
        const viewerLinks = [...doc.querySelectorAll(`[data-gallery-section="${viewerCategory}"] .gallery-open`)];
        const first = viewerLinks[0];
        const dialog = doc.getElementById('gallery-viewer');
        first.click();
        const image = doc.getElementById('gallery-viewer-image');
        await image.decode();
        check(dialog.open && image.src === first.href && doc.documentElement.classList.contains('gallery-viewer-open'),
          {page,viewport:width,issue:'Full photo did not open correctly'});
        const firstCaption = doc.getElementById('gallery-viewer-title').textContent;
        const imageBox = image.getBoundingClientRect();
        check(Math.abs(imageBox.width/imageBox.height-image.naturalWidth/image.naturalHeight) < .015,
          {page,viewport:width,issue:'Full photo aspect ratio distorted'});
        doc.querySelector('[data-gallery-next]').click(); await image.decode();
        check(doc.getElementById('gallery-viewer-title').textContent !== firstCaption,
          {page,viewport:width,issue:'Next photo did not change'});
        dialog.dispatchEvent(new win.KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true})); await image.decode();
        check(doc.getElementById('gallery-viewer-title').textContent === firstCaption,
          {page,viewport:width,issue:'Keyboard previous did not return'});
        doc.querySelector('[data-gallery-previous]').click(); await image.decode();
        check(doc.getElementById('gallery-viewer-counter').textContent.startsWith(`${viewerLinks.length} of ${viewerLinks.length}`),
          {page,viewport:width,issue:'Previous wrap-around failed'});
        const closed = new Promise(resolve => dialog.addEventListener('close', resolve, {once:true}));
        doc.querySelector('[data-gallery-close]').click();
        await closed;
        check(!dialog.open && !doc.documentElement.classList.contains('gallery-viewer-open') && doc.activeElement === first,
          {page,viewport:width,issue:'Close/focus restoration failed'});
      } else {
        const images = [...doc.querySelectorAll('.gallery-preview-card img')];
        images.forEach(image => { image.loading = 'eager'; });
        await Promise.all(images.map(image => image.decode()));
        images.forEach(image => cropCheck(win,image,page,width));
        checkedPhotos = images.length;
        check(checkedPhotos === 4 && !!doc.querySelector('.gallery-preview-actions a[href="gallery.html"]'),
          {page,viewport:width,issue:'Homepage gallery preview/link'});
      }
      if (width <= 390) {
        const toggle = doc.querySelector('.menu-toggle');
        toggle.click();
        check(toggle.getAttribute('aria-expanded') === 'true' && !!doc.querySelector('.nav.open a[href="gallery.html"]'),
          {page,viewport:width,issue:'Mobile navigation gallery link'});
        toggle.click();
      }
      check(doc.documentElement.scrollWidth <= width,{page,viewport:width,issue:'Horizontal overflow',actual:doc.documentElement.scrollWidth});
      results.push({page,viewport:width,checkedPhotos});
      frame.remove();
    }
  }
  return {pass:failures.length===0,results,failures};
})()
