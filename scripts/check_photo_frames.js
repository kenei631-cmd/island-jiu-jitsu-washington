/* Run in the local preview browser console. Read-only apart from temporary
 * test iframes; images are checked against conservatively identified source
 * subject regions, not automatic face-detection claims. Not imported by the site.
 */
(async () => {
  const regions = [
    ['img-4823', [0, .28, 1, 1]],
    ['img-5777', [.14, .515, .87, 1]],
    ['img-5407', [.13, .11, .87, .71]],
    ['img-5701', [.11, .29, .93, .70]],
    ['img-4902', [.025, .36, .93, .75]],
    ['instagram-back-on-the-mats', [.15, .57, .91, 1]],
  ];
  const pages = ['index.html', 'contact.html', 'smokey-point.html', 'lakewood-north-marysville.html'];
  const results = [], failures = [];
  for (const page of pages) {
    for (const width of [1280, 768, 390, 320]) {
      const frame = document.createElement('iframe');
      frame.style.cssText = `position:absolute;left:-10000px;top:0;width:${width}px;height:844px;border:0`;
      document.body.append(frame);
      await new Promise(resolve => { frame.onload = resolve; frame.src = page + '?check-full-bleed=' + width; });
      const doc = frame.contentDocument, win = frame.contentWindow;
      const images = [...doc.querySelectorAll('.cards .card>img,.instagram-card-image img,.page-grid .content-card img')];
      images.forEach(image => { image.loading = 'eager'; });
      await Promise.all(images.map(image => image.decode()));
      const checked = [];
      for (const image of images) {
        const rect = image.getBoundingClientRect(), style = win.getComputedStyle(image);
        const scale = Math.max(rect.width / image.naturalWidth, rect.height / image.naturalHeight);
        const positions = style.objectPosition.split(' ').map(value => parseFloat(value) / 100);
        const horizontalLoss = image.naturalWidth - rect.width / scale;
        const verticalLoss = image.naturalHeight - rect.height / scale;
        const crop = [horizontalLoss * positions[0] / image.naturalWidth,
          verticalLoss * positions[1] / image.naturalHeight,
          (horizontalLoss * positions[0] + rect.width / scale) / image.naturalWidth,
          (verticalLoss * positions[1] + rect.height / scale) / image.naturalHeight];
        const region = regions.find(([key]) => image.src.includes(key));
        const safe = !region || (crop[0] <= region[1][0] + .002 && crop[1] <= region[1][1] + .002 && crop[2] >= region[1][2] - .002 && crop[3] >= region[1][3] - .002);
        const loaded = image.complete && image.naturalWidth > 0;
        const filled = style.objectFit === 'cover' && image.naturalWidth * scale >= rect.width - .5 && image.naturalHeight * scale >= rect.height - .5;
        const item = {photo:image.src.split('/').pop(),width:rect.width,height:rect.height,filled,loaded,subjectSafe:safe,crop};
        checked.push(item);
        if (!filled || !safe || !loaded) failures.push({page,viewport:width,...item});
      }
      for (const selector of ['.cards .card>img', '.instagram-card-image img', '.page-grid .content-card img']) {
        const boxes = [...doc.querySelectorAll(selector)].map(image => image.getBoundingClientRect());
        if (boxes.length > 1 && (Math.max(...boxes.map(box=>box.width))-Math.min(...boxes.map(box=>box.width)) > .5 || Math.max(...boxes.map(box=>box.height))-Math.min(...boxes.map(box=>box.height)) > .5)) {
          failures.push({page,viewport:width,issue:'Image frames in this group do not match',selector,boxes:boxes.map(box=>[box.width,box.height])});
        }
      }
      if (doc.documentElement.scrollWidth > width) failures.push({page,viewport:width,issue:'Horizontal overflow'});
      results.push({page,viewport:width,images:checked.length,allFilled:checked.every(item=>item.filled),subjectsSafe:checked.every(item=>item.subjectSafe)});
      frame.remove();
    }
  }
  return {results,failures,pass:failures.length===0};
})()
