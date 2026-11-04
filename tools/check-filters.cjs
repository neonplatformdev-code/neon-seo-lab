const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const path = require("node:path");
const filters = ["all", "control", "finding", "refusal"].map(value => ({dataset: {filter: value}, attrs: {}, setAttribute(k,v) {this.attrs[k]=v;}, addEventListener(k,v) {this.click=v;}}));
const cards = ["control", "finding", "finding", "finding", "refusal"].map(kind => ({dataset: {kind}, hidden: false}));
const count = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../public/assets/site.js"),"utf8"), {document: {querySelectorAll(s) {return s === "[data-filter]" ? filters : cards;}, querySelector() {return count;}}});
for (const [index, total] of [[1,1],[2,3],[3,1],[0,5]]) {
 filters[index].click();
 assert.equal(cards.filter(x => !x.hidden).length,total);
 assert.equal(filters.filter(x => x.attrs["aria-pressed"] === "true").length,1);
 assert.ok(count.textContent.includes(String(total)));
}
console.log("PASS: all four filter states and accessible status updates");
