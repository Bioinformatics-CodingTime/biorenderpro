const {chromium}=require('/Users/wa/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const root='/Users/wa/biorender-library',catalog=JSON.parse(fs.readFileSync(root+'/catalog.json'));
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1360,height:950},acceptDownloads:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+root+'/index.html');
  await page.locator('article').first().waitFor();
  assert.equal(await page.locator('article').count(),60);
  await page.locator('article img').evaluateAll(imgs=>imgs.forEach(i=>i.loading='eager'));
  await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete));
  assert.equal(await page.locator('article img').evaluateAll(imgs=>imgs.filter(i=>!i.naturalWidth).length),0);
  await page.screenshot({path:root+'/preview.png'});
  await page.locator('#next').click();assert.match(await page.locator('#status').innerText(),/第 2 /);
  await page.locator('#q').fill('monocyte');assert.ok(await page.locator('article').count()>0);
  const opened=page.context().waitForEvent('page');
  await page.locator('article a[download]').first().click();
  const svgPage=await opened;await svgPage.waitForLoadState();
  assert.ok(await svgPage.locator('svg').count()>0);await svgPage.close();
  await page.screenshot({path:root+'/diagnostics/monocyte-preview.png'});
  await page.locator('#q').fill('');
  await page.locator('#kind').selectOption('科研与技术');
  const scientific=catalog.filter(r=>r.kind==='科研与技术').length;
  assert.ok((await page.locator('#status').innerText()).startsWith(scientific.toLocaleString()));
  await page.locator('#kind').selectOption('');
  await page.locator('#collection').selectOption('SwissBioPics · original');
  assert.ok((await page.locator('#status').innerText()).startsWith(catalog.filter(r=>r.collection==='SwissBioPics · original').length.toLocaleString()+' '));
  await page.locator('#collection').selectOption('');
  await page.locator('#license').selectOption('CC-BY-4.0');
  await page.locator('#q').fill('zzzz-no-matching-icon');assert.match(await page.locator('#status').innerText(),/^0 /);
  await page.locator('#q').fill('');await page.locator('#license').selectOption('');
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:root+'/diagnostics/mobile-preview.png'});
  const samples=[...new Set(catalog.map(r=>r.collection))].flatMap(c=>catalog.filter(r=>r.collection===c).slice(0,3).map(r=>r.path));
  const failed=await page.evaluate(async paths=>{
   const out=[];
   for(let n=0;n<paths.length;n+=12){
    const results=await Promise.all(paths.slice(n,n+12).map(path=>new Promise(resolve=>{
     const img=new Image();img.onload=()=>resolve(img.naturalWidth?null:path);img.onerror=()=>resolve(path);
     img.src=path.split('/').map(encodeURIComponent).join('/');
    })));out.push(...results.filter(Boolean));
   }return out;
  },samples);
  const report={catalog_entries:catalog.length,first_page_images:60,sampled_images:samples.length,failed_sample_images:failed,page_errors:errors,checks:['paging','monocyte search','actual local SVG opened','type, source and license filtering','empty search','390px mobile layout']};
  fs.writeFileSync(root+'/diagnostics/browser-check.json',JSON.stringify(report,null,2));
  assert.deepEqual(failed,[]);assert.deepEqual(errors,[]);console.log(JSON.stringify(report,null,2));
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
