// Minimal DOM harness: verifies the offline gallery's filtering and navigation.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Element {
  constructor(){this.children=[];this.value='';this.events={};this.textContent=''}
  append(...nodes){this.children.push(...nodes)}
  replaceChildren(...nodes){this.children=nodes}
  addEventListener(name,fn){this.events[name]=fn}
}
const elements=Object.fromEntries(['q','collection','category','kind','license','grid','status','prev','next'].map(k=>['#'+k,new Element()]));
const context=vm.createContext({document:{querySelector:s=>elements[s],createElement:()=>new Element()},console});
const root=__dirname;
vm.runInContext(fs.readFileSync(root+'/catalog.js','utf8'),context);
const html=fs.readFileSync(root+'/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.runInContext(script,context);
assert.equal(elements['#grid'].children.length,60);
assert.equal(elements['#prev'].disabled,true);
elements['#next'].onclick();assert.equal(elements['#prev'].disabled,false);
elements['#q'].value='monocyte';elements['#q'].events.input();
assert.ok(elements['#grid'].children.some(c=>c.children.length>0));
const catalog=JSON.parse(fs.readFileSync(root+'/catalog.json','utf8'));
const expected=catalog.filter(r=>[r.name,r.tags,r.category,r.author,r.collection,...(r.also_available_from||[]).map(o=>o.name)].join(' ').toLowerCase().includes('monocyte')).slice(0,60).map(r=>r.name);
assert.deepEqual(elements['#grid'].children.map(c=>c.children[1].textContent),expected);
elements['#q'].value='';elements['#collection'].value='NIH BioArt Source';elements['#collection'].events.change();
const origins=r=>[r,...(r.also_available_from||[])];
const nihCount=catalog.filter(r=>origins(r).some(o=>o.collection==='NIH BioArt Source')).length;
assert.ok(elements['#status'].textContent.startsWith(nihCount.toLocaleString()+' '));
assert.ok(elements['#grid'].children.every(c=>c.children[4].href.endsWith('.svg')));
elements['#q'].value='no-such-icon-zzzz';elements['#q'].events.input();
assert.equal(elements['#grid'].children.length,1);assert.equal(elements['#next'].disabled,true);
assert.ok(elements['#status'].textContent.startsWith('0 '));
elements['#q'].value='';elements['#collection'].value='';elements['#kind'].value='AI生成（来源标记）';elements['#kind'].events.change();
const aiCount=catalog.filter(r=>r.kind==='AI生成（来源标记）').length;
assert.ok(elements['#status'].textContent.startsWith(aiCount.toLocaleString()+' '));
elements['#kind'].value='';elements['#license'].value='CC-BY-4.0';elements['#license'].events.change();
const licenseCount=catalog.filter(r=>origins(r).some(o=>o.license==='CC-BY-4.0')).length;
assert.ok(elements['#status'].textContent.startsWith(licenseCount.toLocaleString()+' '));
console.log('PASS: pagination, keyword search, source/license/AI filters, downloads, empty results');
