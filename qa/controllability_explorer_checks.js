// Lesson-specific assertions plugged into the shared browser runner; no second server/harness.
const SM=require('../courses/controls/controllability/dist/study_math.js');
module.exports=async function({page,course,check}){
  const set=async(k,v)=>page.locator('#ex-'+k).evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));},v);
  for(const p of course.explorer.presets){
    await page.getByRole('button',{name:p.label,exact:true}).click();
    const values=await page.evaluate(()=>Object.fromEntries(['c','b1','b2','alpha','beta'].map(k=>[k,+document.getElementById('ex-'+k).value])));
    const dual=await page.locator('#ex-dual').isChecked();
    check('preset '+p.id+' controls',Object.entries(values).every(([k,v])=>v===p[k])&&dual===p.dual);
    const expected=SM.explorerModel(p);
    check('preset '+p.id+' rank',await page.locator('.verdict').innerText().then(t=>t.startsWith('rank '+expected.rank)));
    check('preset '+p.id+' formulas',await page.locator('.katex-error').count()===0);
  }
  await page.getByRole('button',{name:'Uncoupled',exact:true}).click();await set('b2',0);
  check('zero actuator is rank zero',await page.locator('.verdict').innerText().then(t=>t.startsWith('rank 0')));
  await page.locator('#ex-dual').check();
  check('adding only e1 reaches one direction',await page.locator('.verdict').innerText().then(t=>t.startsWith('rank 1')));
  await set('b2',1);
  check('independent second actuator restores rank two',await page.locator('.verdict').innerText().then(t=>t.startsWith('rank 2')));
  await set('c',2);await set('b1',2);await set('b2',2);await set('alpha',2);await set('beta',2);
  check('off-scale coefficient point is reported',await page.locator('main').innerText().then(t=>t.includes('outside the plotted square')));
  await page.reload();await page.waitForSelector('#ex-c');
  check('explorer settings persist',await page.locator('#ex-c').inputValue()==='2'&&await page.locator('#ex-dual').isChecked());
  await page.evaluate(key=>{const saved=JSON.parse(localStorage.getItem(key));saved.explorer.b1='invalid';localStorage.setItem(key,JSON.stringify(saved));},'controllability-v1');
  await page.reload();await page.waitForSelector('#ex-c');
  check('invalid saved settings fall back safely',+(await page.locator('#ex-c').inputValue())===course.explorer.c.default&&+(await page.locator('#ex-b1').inputValue())===course.explorer.b1.default);
  check('restored explorer has no invalid formulas',await page.locator('.katex-error').count()===0);
};
