const {chromium}=require('C:/Users/lamon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const base='http://127.0.0.1:9142',session=await(await fetch(base+'/qa-session')).json(),headers={'Cf-Access-Jwt-Assertion':session.token};
 await fetch(base+'/qa-reset',{method:'POST'});await fetch(base+'/qa-adult-ml',{method:'POST'});
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,extraHTTPHeaders:headers});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const settled=()=>page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 const ready=()=>page.waitForFunction(()=>!document.getElementById('meme').disabled);
 await page.goto(base+'/image-review/');await settled();await page.locator('#mode').selectOption('adult');await ready();
 assert.equal(await page.locator('#adult-ml').inputValue(),'flagged');assert.equal(await page.locator('#sort').inputValue(),'adult');assert.match(await page.locator('#position').innerText(),/1 \/ 3/);
 assert.match(await page.locator('#adult-suggestion').innerText(),/Likely adult content/);
 await page.locator('#filter-toggle').click();assert.match(await page.locator('#adult-ml-status').innerText(),/6 \/ 6 scanned/);
 await page.locator('#adult-ml').selectOption('uncertain');await ready();await settled();assert.match(await page.locator('#position').innerText(),/1 \/ 1/);assert.match(await page.locator('#adult-suggestion').innerText(),/Uncertain/);
 await page.locator('#adult-ml').selectOption('likely_safe');await settled();await ready();assert.match(await page.locator('#position').innerText(),/1 \/ 3/);
 // A manual adult label must remain visible even when the classifier suggested safe.
 await page.locator('#meme').click();await settled();await page.locator('#adult-state').selectOption('adult');await settled();await ready();
 assert.equal(await page.locator('#adult-ml').inputValue(),'all');assert.match(await page.locator('#adult-suggestion').innerText(),/Likely not adult/);assert.match(await page.locator('#previous-label').innerText(),/Adult content/);
 await page.reload();await settled();await ready();assert.match(await page.locator('#previous-label').innerText(),/Adult content/);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.screenshot({path:path.join(__dirname,'../qa-adult-ml-mobile.png'),fullPage:true});
 await page.setViewportSize({width:1440,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);
 const result={passed:true,checks:['Adult mode defaults to machine-flagged subset','Highest scores first','Likely-adult, uncertain and likely-safe filters','Machine suggestion shown separately','Manual correction overrides review selection','Saved correction survives reload','Mobile and desktop fit','No script errors']};
 fs.writeFileSync(path.join(__dirname,'../adult-ml-browser-results.json'),JSON.stringify(result,null,2));console.log(result);
 }finally{await browser.close();await fetch(base+'/qa-reset',{method:'POST'});}
})().catch(e=>{console.error(e);process.exit(1);});
