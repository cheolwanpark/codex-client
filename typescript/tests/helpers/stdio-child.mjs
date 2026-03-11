const mode = process.argv[2];

if (mode === "echo") {
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => {
    process.stdout.write(chunk);
  });
  process.stdin.on("end", () => {
    process.exit(0);
  });
} else if (mode === "crash-after-first-line") {
  process.stdin.setEncoding("utf8");
  let buffer = "";
  process.stdin.on("data", (chunk) => {
    buffer += chunk;
    if (buffer.includes("\n")) {
      process.stderr.write("child saw line before crash\n");
      process.exit(7);
    }
  });
} else if (mode === "emit-path-and-exit") {
  process.stdout.write(`${process.cwd()}\n`);
  process.exit(0);
} else {
  throw new Error(`Unsupported mode: ${mode}`);
}
