const {chromium}=require('C:/Users/lamon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const base='http://127.0.0.1:9142';
 const session=await(await fetch(base+'/qa-session')).json();
 await fetch(base+'/qa-reset',{method:'POST'});await fetch(base+'/qa-learning',{method:'POST'});
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 try{
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,extraHTTPHeaders:{'Cf-Access-Jwt-Assertion':session.token}});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/image-review/');await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 await page.locator('.learning-panel summary').click();assert.equal(await page.locator('#learn').isDisabled(),false);
 await page.locator('#learn').click();await page.waitForFunction(()=>document.getElementById('status').textContent==='Improved cutoff activated.');
 assert.match(await page.locator('#learning-status').innerText(),/Learned cutoff active/);assert.match(await page.locator('#learning-result').innerText(),/candidate/);
 await page.reload();await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
 await page.locator('.learning-panel summary').click();assert.match(await page.locator('#learning-status').innerText(),/Learned cutoff active/);
 await page.locator('#learn').click();await page.waitForFunction(()=>document.getElementById('status').textContent==='No verified improvement. Current cutoff retained.');
 assert.match(await page.locator('#learning-status').innerText(),/Learned cutoff active/);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);
 console.log('Learning browser checks passed: activation, persistence, rejected repeat retains active cutoff, mobile layout, no script errors.');
 }finally{await browser.close();await fetch(base+'/qa-reset',{method:'POST'});}
})().catch(e=>{console.error(e);process.exit(1);});
