const {chromium}=require('C:/Users/lamon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const base='http://127.0.0.1:9142',session=await(await fetch(base+'/qa-session')).json(),headers={'Cf-Access-Jwt-Assertion':session.token};
 await fetch(base+'/qa-reset',{method:'POST'});await fetch(base+'/qa-adult-ml',{method:'POST'});
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,extraHTTPHeaders:headers});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const settled=async()=>page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 const ready=async()=>page.waitForFunction(()=>!document.getElementById('no-people').disabled);
 const queue=async()=>await(await fetch(base+'/image-review/api/queue?band=all&mode=people', {headers})).json();
 await page.goto(base+'/image-review/');await ready();assert.equal(await page.locator('#mode').inputValue(),'people');
 const first=(await queue()).items[0].sha256;
 await page.locator('#person-name').fill('Alex');await page.locator('#add-person').click();await page.waitForFunction(()=>document.getElementById('people-choices').querySelector('input:checked'));
 await page.locator('#other-people').check();await page.locator('#save-people').click();await settled();await ready();
 let q=await queue();let person=q.people[0].id;assert.equal(q.overall.reviewed,0);assert.equal(q.items.find(i=>i.sha256===first)?.people_review.state,'tagged');
 await page.reload();await ready();await page.locator('#undo').click();await settled();await ready();assert.equal((await queue()).items.find(i=>i.sha256===first)?.people_review.state,null);
 await page.locator('#people-choices input').check();await page.locator('#save-people').click();await settled();await ready();
 await page.locator('#filter-toggle').click();await page.locator('#refine').click();await settled();await page.waitForFunction(()=>!document.getElementById('meme').disabled);
 assert.equal(await page.locator('#band').inputValue(),'priority');assert.equal(await page.locator('#people-state').inputValue(),'tagged');
 await page.locator('#person-filter').selectOption([person]);await settled();assert.match(await page.locator('#position').innerText(),/1 \/ 1/);
 await page.locator('#meme').click();await settled();assert.equal((await queue()).overall.reviewed,1);
 // Adult-content review is independent and can be filtered by those same tags.
 await page.locator('#mode').selectOption('adult');await settled();await page.waitForFunction(()=>!document.getElementById('meme').disabled);
 assert.match(await page.locator('#meme').innerText(),/Adult content/);await page.locator('#meme').click();await settled();
 assert.equal((await queue()).overall.reviewed,1);await page.locator('#adult-state').selectOption('adult');await settled();await page.waitForFunction(()=>!document.getElementById('meme').disabled);
 assert.match(await page.locator('#previous-label').innerText(),/Adult content/);assert.match(await page.locator('#previous-label').innerText(),/Saved: Meme/);
 await page.locator('#undo').click();await settled();assert.equal((await queue()).overall.reviewed,1);
 // Confirm lost responses retain the same people operation after reload.
 await page.locator('#clear-people').click();await settled();await page.locator('#mode').selectOption('people');await settled();await ready();
 let fail=true;await page.route('**/api/people/decision',async route=>{if(fail){fail=false;await route.fetch();await route.abort('failed');}else await route.continue();});
 await page.locator('#no-people').click();await page.waitForFunction(()=>!document.getElementById('retry').hidden);await page.reload();await settled();assert.equal(await page.locator('#retry').isVisible(),true);
 await page.locator('#retry').click();await settled();assert.equal(await page.locator('#retry').isVisible(),false);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.screenshot({path:path.join(__dirname,'../qa-people-mobile.png'),fullPage:true});
 await page.setViewportSize({width:1440,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);
 const exp=await(await fetch(base+'/image-review/api/export?format=json',{headers})).json();assert.ok(exp.annotation_events.some(e=>e.kind==='undo'));assert.equal(exp.events.length,1);
 const result={passed:true,checks:['People-first mode','Name creation and multi-person tags','Independent meme counts','People undo persists across reload','Named-person + likely-meme/borderline filters','Separate adult-content review and filter','Adult undo leaves meme labels intact','Lost people-save response retries idempotently','Mobile and desktop fit','Annotation history exported','No script errors']};
 fs.writeFileSync(path.join(__dirname,'../annotation-browser-results.json'),JSON.stringify(result,null,2));console.log(result);
 }finally{await browser.close();await fetch(base+'/qa-reset',{method:'POST'});}
})().catch(e=>{console.error(e);process.exit(1);});
