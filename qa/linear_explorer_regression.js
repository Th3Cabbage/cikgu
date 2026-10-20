// Review regressions: zero eigenvalues and playback at 240 Hz. No external API calls.
const assert = require('assert/strict');
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const M = require('../courses/controls/linear-systems/dist/study_math.js');
for (const [a,b,expected] of [[0,1,'unstable'],[1,0,'unstable'],[-1,0,'marginal'],[0,0,'marginal'],[1,-1,'saddle'],[-1,-2,'stable']]) {
  assert.equal(M.classify(a,b),expected);
}

// Run the real explorer with a tiny DOM adapter and a manually driven RAF clock.
const course = JSON.parse(fs.readFileSync(path.join(__dirname,'../courses/controls/linear-systems/dist/course.json'),'utf8'));
const nodes = new Map();
function element(tag, attrs={}, children=[]) {
  attrs=attrs||{};
  const n={tag, children:[], attrs:{}, value:attrs.value, textContent:attrs.text||'',
    appendChild(c){this.children.push(c);return c},
    removeChild(c){this.children.splice(this.children.indexOf(c),1)},
    get firstChild(){return this.children[0]},
    setAttribute(k,v){this.attrs[k]=String(v)},getAttribute(k){return this.attrs[k]},
    addEventListener(k,fn){this[k]=fn}};
  if(attrs.id)nodes.set(attrs.id,n);
  if(attrs.onclick)n.click=attrs.onclick;
  children.forEach(c=>n.appendChild(c));return n;
}
let pending=null;
const win={StudyMath:M};
const sandbox={window:win,requestAnimationFrame(fn){pending=fn;return 1},cancelAnimationFrame(){pending=null},console};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../courses/controls/linear-systems/dist/explorer.js'),'utf8'),sandbox);
const state={explorer:null};
const math=(n,text)=>{n.textContent=text;return n};
win.StudyExplorer.render({root:element('root'),course,state,save(){},html:element,svg:element,mathText:math,flowMath:math,displayMath:math,announce(){}});
const initial=state.explorer.t;
nodes.get('ex-play').click();
for(let i=0;i<=240;i++) {const fn=pending;pending=null;assert.ok(fn);fn(i*1000/240)}
assert.ok(Math.abs(state.explorer.t-initial-course.explorer.playRate)<1e-9,'time must advance by elapsed seconds, independent of frame rate');
nodes.get('ex-play').click();
assert.equal(pending,null,'pause cancels playback');
nodes.get('ex-play').click();win.StudyExplorer.stop();assert.equal(pending,null,'navigation stop cancels playback');
const restored=win.StudyExplorer.restore(state.explorer,course.explorer);
assert.ok(restored && Math.abs(restored.t-state.explorer.t)<=course.explorer.t.step/2+1e-9);
console.log('PASS 6 eigenvalue cases; 240 Hz elapsed-time playback; pause; stop; persisted time validation');
