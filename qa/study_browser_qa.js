// Shared Controls browser contract. node qa/study_browser_qa.js courses/controls/<slug>
// No live tutor API: remove keys from the owned server's environment.
"use strict";
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert/strict');
const {spawn}=require('child_process');
const ROOT=path.resolve(__dirname,'..'),pkg=path.resolve(ROOT,process.argv[2]||'courses/controls/controllability');
assert.ok(pkg.startsWith(path.join(ROOT,'courses')+path.sep));
const slug=path.basename(pkg),dist=path.join(pkg,'dist');
const explorerOnly=process.argv.includes('--explorer-only');
const course=JSON.parse(fs.readFileSync(path.join(dist,'course.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(dist,'animations/manifest.json'),'utf8'));
const {chromium}=require('./tooling/node_modules/playwright-core');
const shots=path.join(__dirname,'screenshots',slug);fs.mkdirSync(shots,{recursive:true});
let checks=0;const results=[];
function check(name,ok){results.push({name,ok:!!ok});assert.ok(ok,name);checks++;console.log('PASS '+name);}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function stable(page,k){await page.waitForFunction(k=>{const w=document.querySelector('.stage-wrap'),im=document.querySelector('.stage-still'),stage=document.querySelector('.stage');return w&&w.dataset.step===String(k)&&w.dataset.playing==='false'&&im.complete&&im.naturalWidth>0&&!stage.classList.contains('video-on');},k);}
async function go(page,base,hash){await page.goto(base+'#'+hash);await page.waitForSelector('h1');await page.waitForTimeout(120);}
async function main(){
  const portFile=path.join(os.tmpdir(),`study-qa-${process.pid}.txt`),nonce='qa-'+process.pid;
  const env={...process.env};for(const k of Object.keys(env))if(k.startsWith('OPENAI_'))delete env[k];
  const py=path.join(ROOT,'.venv','Scripts','python.exe');
  const proc=spawn(py,['-I',path.join(pkg,'server.py'),'--port','8830','--port-file',portFile,'--nonce',nonce],{env,stdio:'ignore'});
  let browser;
  try{
    for(let i=0;!fs.existsSync(portFile)&&i<100;i++){if(proc.exitCode!==null)throw Error('Server exited');await pause(100);}
    const port=fs.readFileSync(portFile,'utf8').trim(),base=`http://127.0.0.1:${port}/`;
    let health;
    for(let i=0;i<100;i++){
      try{health=await(await fetch(base+'__control_health')).json();break;}catch(e){if(proc.exitCode!==null)throw Error('Server exited before readiness');await pause(100);}
    }
    check('owned server identity',health&&health.nonce===nonce&&health.app==='Study_'+slug.replaceAll('-','_'));
    browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true});
    const context=await browser.newContext({viewport:{width:1440,height:900}});
    await context.addInitScript(()=>{const play=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){this.playbackRate=8;return play.call(this);};});
    const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
    for(const sec of explorerOnly?[]:course.sections){
      await go(page,base,sec.id);
      for(const seq of manifest.sequences.filter(s=>s.section===sec.number)){
        const select=page.locator(`.seq-btn[data-seq="${seq.id}"]`);if(await select.count())await select.click();
        let restart=page.locator('[data-action="restart-complete"]');
        if(await restart.isVisible())await restart.click();else if(await page.locator('[data-action="restart"]').isEnabled())await page.locator('[data-action="restart"]').click();
        await stable(page,0);
        for(let i=1;i<=seq.steps.length;i++){
          await page.locator('[data-action="next"]').click();await stable(page,i);
          check(seq.id+' step '+i,await page.locator('.stage-still').getAttribute('src')===seq.steps[i-1].finalFrame);
        }
        await page.screenshot({path:path.join(shots,seq.id+'-desktop.png')});
        await page.locator('[data-action="back"]').click();await stable(page,seq.steps.length-1);
        if(seq.steps.length>1){await page.locator('[data-action="replay"]').click();await stable(page,seq.steps.length-1);}
        check(seq.id+' back/replay',true);
      }
      check(sec.id+' math and layout',await page.locator('.katex-error').count()===0&&await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    }
    if(!explorerOnly){
    await page.reload();await page.waitForSelector('.stage-wrap');check('saved animation step',Number(await page.locator('.stage-wrap').getAttribute('data-step'))>0);
    await go(page,base,'quiz');
    for(const q of course.quiz){
      await page.waitForSelector(`[data-qid="${q.id}"]`);
      if(q===course.quiz[0]){const wrong=q.choices.findIndex(c=>!c.correct);await page.locator(`[data-choice="${wrong}"]`).click();check('quiz explains wrong answer',await page.locator('.q-card').innerText().then(t=>t.includes(q.choices[wrong].why.replace(/\$/g,'')))||await page.locator('.q-card .feedback').count()>0);}
      await page.locator(`[data-choice="${q.choices.findIndex(c=>c.correct)}"]`).click();
      await page.locator('[data-action="next-question"]').click();
    }
    check('quiz completes',!(await page.locator('.q-card').count()));
    }
    await go(page,base,'explorer');check('explorer renders',await page.locator('svg').count()>0);
    const ranges=page.locator('main input[type="range"],#view input[type="range"]');
    if(await ranges.count()){
      const old=await page.locator('main').innerText();
      await ranges.first().evaluate(el=>{el.value=el.max;el.dispatchEvent(new Event('input',{bubbles:true}));});
      check('explorer updates',await page.locator('main').innerText()!==old);
    }
    check('explorer math',await page.locator('.katex-error').count()===0);
    const hook=path.join(__dirname,slug.replaceAll('-','_')+'_explorer_checks.js');
    if(fs.existsSync(hook))await require(hook)({page,context,course,check});
    await page.screenshot({path:path.join(shots,'explorer-desktop.png')});
    await page.setViewportSize({width:390,height:844});
    await go(page,base,'explorer');check('mobile explorer fits',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.screenshot({path:path.join(shots,'explorer-mobile.png')});
    for(const route of [course.sections[0].id,'quiz','sources']){
      await go(page,base,route);check('mobile '+route,await page.locator('.katex-error').count()===0&&await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    }
    await page.emulateMedia({reducedMotion:'reduce'});await go(page,base,course.sections[0].id);
    if(await page.locator('[data-action="restart"]').isEnabled())await page.locator('[data-action="restart"]').click();await stable(page,0);await page.locator('[data-action="next"]').click();await stable(page,1);check('reduced motion advances',true);
    const status=await(await fetch(base+'api/status')).json();check('tutor needs no key for guide',status.tutor.configured===false);
    check('no browser exceptions',errors.length===0);
    console.log(JSON.stringify({package:slug,checks,passed:true}));
  }finally{
    if(browser)await browser.close();proc.kill();if(fs.existsSync(portFile))fs.unlinkSync(portFile);
    fs.mkdirSync(path.join(__dirname,'results'),{recursive:true});fs.writeFileSync(path.join(__dirname,'results',slug+'-shared-browser.json'),JSON.stringify(results,null,2));
  }
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;});
