# Workspace implementation

Choose the canonical artifact first:

- Documents and block content: Tiptap, ProseMirror, Lexical, or the existing editor.
- Node graphs and simple boards: React Flow or DOM cards with stable IDs.
- Freeform drawing: tldraw, Excalidraw, Konva, or Fabric when true spatial editing is required.
- Mixed products: keep one canonical artifact model and project it into multiple views.

Define typed business tools around real actions such as reading, creating, validating, inserting, and reviewing domain entities. Wrap each tool so it emits start, completion, and failure events. Validate output before applying an artifact patch.

A common UI uses navigation or an artifact index, a central editor, and a task/progress panel. Keep assistant messages separate from tool statuses and artifact mutations. Each displayed item should link to the underlying job, call, or artifact record when practical.

Build the static artifact surface, then event handling, then real tools. Mock events are useful during UI construction but must be replaced or clearly separated before claiming the product shows real work.
