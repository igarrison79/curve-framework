// Drafts Action Script: Render HTML blocks
// 1. If draft contains no ```html``` code blocks, the script exits silently.
// 2. If a single block exists, it's displayed in a web view.
// 3. If multiple blocks exist, the user is prompted to choose one.
// Place this JavaScript in a Drafts action step.

// Collect all fenced ```html``` code blocks in the draft
let regex = /```html\s*\n([\s\S]*?)```/gi;
let blocks = [];
let match;
while ((match = regex.exec(draft.content)) !== null) {
  blocks.push(match[1]);
}

// No HTML blocks found — exit quietly
if (blocks.length === 0) {
  return;
}

let index = 0;
// If more than one block, prompt user for selection
if (blocks.length > 1) {
  let p = Prompt.create();
  p.title = "Select HTML Block";
  p.message = "Which HTML block would you like to preview?";
  for (let i = 0; i < blocks.length; i++) {
    p.addButton((i + 1).toString());
  }
  // If prompt dismissed, exit quietly
  if (!p.show()) {
    return;
  }
  index = parseInt(p.buttonPressed, 10) - 1;
}

// Load the chosen HTML block into a web view
let wv = WebView.create();
wv.loadHTML(blocks[index]);
wv.present();
