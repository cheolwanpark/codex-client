# Repo Agent Notes

- Read [DESIGN.md](/Users/cheolwanpark/Documents/Projects/codex-client/DESIGN.md) before changing protocol-facing code.
- `schema/` is the source of truth for wire shapes. `DESIGN.md` is the source of truth for shared layering and lifecycle rules.
- Keep bindings parallel where practical. Treat `python/` as the behavioral reference when building out `typescript/`.
- Build the TypeScript binding bottom-up: messages/errors -> codec -> transport -> connection -> typed client -> runtime.
- The TypeScript package now includes all 3 layers. Preserve the separation between generated protocol surface and handwritten client/runtime logic.
- If protocol-facing TypeScript types or wrapper methods change, update the codegen source and regenerate the checked-in files in `typescript/src/generated*.ts`.
- Keep new TypeScript helpers limited to parity-oriented payload builders and documented runtime ergonomics. Do not add higher-level workflow helpers unless the task explicitly asks for them.
- Prefer parity tests against the Python low-level behavior before introducing TypeScript-only abstractions.
- Keep the TypeScript package Node-focused until a task explicitly asks for additional runtimes or transports.
- When repo docs mention available bindings or TypeScript support level, keep them accurate now that the runtime layer exists.
- Run TypeScript examples through the checked-in `pnpm example:*` scripts. `pnpm examples:build` compiles `src/` and `examples/` into `typescript/.examples-dist/` for local example execution.
- If a commit is requested, follow the existing Conventional Commit pattern from `git log` such as `feat: ...`, `fix: ...`, `docs: ...`, or `refactor: ...`.
