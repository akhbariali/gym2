const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const products = JSON.parse(fs.readFileSync(path.join(root, 'content/products.json')));
const source = fs.readFileSync(path.join(root, 'dist/app.js'), 'utf8');
function setup(initialType = '', catalog = true, saved = {}) {
 const elements = {};
 for (const key of ['#cartCount', '#cartItems', '#cartSummary', '#toast', ...(catalog ? ['#grid', '#products', '#search', '#price', '#sort', '#priceValue', '#resultCount', '#empty', '#reset', '#emptyReset'] : [])]) {
  elements[key] = { value: key === '#price' ? '4000000' : key === '#sort' ? 'featured' : '', dataset: key === '#products' ? { initialType } : {}, innerHTML: '', textContent: '', classList: { add() {}, remove() {}, toggle() {} }, addEventListener() {} };
 }
 const inputs = ['isolate', 'concentrate', 'blend'].map(value => ({value, checked: false, disabled: false, addEventListener() {}}));
 const storage = {value: saved};
 const document = {
  querySelector(selector) {
   const type = selector.match(/^input\[name=type\]\[value=(\w+)\]$/);
   return type ? inputs.find(x => x.value === type[1]) : elements[selector] || null;
  },
  querySelectorAll(selector) {
   if(selector === 'input[name=type]:checked') return inputs.filter(x=>x.checked);
   if(selector === 'input[name=type]' || selector === 'aside input' || selector === 'aside input[type=checkbox]') return inputs;
   return [];
  },
  addEventListener() {}
 };
 const context = vm.createContext({window:{WHEY_PRODUCTS:products},document,localStorage:{getItem:()=>JSON.stringify(storage.value),setItem:(key,value)=>{storage.value=JSON.parse(value)}},setTimeout:()=>1,clearTimeout(){}});
 vm.runInContext(source, context);
 return {elements,context,inputs,storage};
}
let env = setup('isolate');
assert.equal((env.elements['#grid'].innerHTML.match(/class="card"/g)||[]).length,3);
assert(env.elements['#grid'].innerHTML.includes('href="/products/whey-isolate-chocolate/"'));
assert(env.inputs.every(i=>i.disabled));
vm.runInContext('reset()', env.context);
assert.equal((env.elements['#grid'].innerHTML.match(/class="card"/g)||[]).length,3);
env = setup();
env.elements['#search'].value='توت';vm.runInContext('render()',env.context);
assert.equal((env.elements['#grid'].innerHTML.match(/class="card"/g)||[]).length,1);
env.elements['#search'].value='no result';vm.runInContext('render()',env.context);assert.equal(env.elements['#empty'].hidden,false);
vm.runInContext('reset();add(1);add(1);add(2)',env.context);
assert.equal(env.elements['#cartCount'].textContent,'۳');
assert(env.elements['#cartSummary'].innerHTML.includes((7570000).toLocaleString('fa-IR')));
assert.equal(env.storage.value[1],2);
env = setup('', false, {1:2});
assert.equal(env.elements['#cartCount'].textContent,'۲');
vm.runInContext('add(2);add(999)',env.context);
assert.equal(env.elements['#cartCount'].textContent,'۳');
console.log('Passed: category routing, reset, product links, search, empty state, cart totals, cross-page persistence, product-page initialization.');
